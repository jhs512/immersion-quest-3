"""Read the unmodified native C program through LLDB's typed debug values."""
import json
import math
import os
import shlex

import lldb


LIMIT = 1000
MAX_CHILDREN = 64


def _read(path):
    try:
        with open(path, 'rb') as stream:
            return stream.read().decode('utf-8', 'replace').replace('\r\n', '\n')
    except FileNotFoundError:
        return ''


class Recorder:
    def __init__(self, target, case, source):
        self.target = target
        self.case = case
        self.blocks = {}
        self.freed = {}
        self.serial = 0
        self.pending = {}
        self.returning = {}
        self.return_addresses = set()
        self.allocator_ids = {}
        self.frame_ids = {}
        self.next_frame = 1
        self.live_frames = set()
        self.truncated = False
        self.view_ids = {}
        self.next_view = 1
        declarations = os.path.join(case, 'declarations.json')
        self.declarations = json.loads(_read(declarations)) if os.path.isfile(declarations) else {}
        self.arm = target.GetTriple().startswith(('arm64', 'aarch64'))
        for name in ('malloc', 'calloc', 'realloc', 'free'):
            breakpoint = target.BreakpointCreateByName(name)
            self.allocator_ids[breakpoint.GetID()] = name

    def register(self, frame, index, returning=False):
        if self.arm:
            name = 'x0' if returning else 'x' + str(index)
        else:
            name = 'rax' if returning else ('rdi', 'rsi')[index]
        return frame.FindRegister(name).GetValueAsUnsigned()

    def user_frame(self, frame):
        entry = frame.GetLineEntry()
        return entry.IsValid() and entry.GetFileSpec().GetFilename() == 'main.c'

    def type_key(self, typ):
        return typ.GetCanonicalType().GetUnqualifiedType().GetName()

    def object_id(self, key):
        if key not in self.view_ids:
            self.view_ids[key] = self.next_view
            self.next_view += 1
        return str(self.view_ids[key])

    def allocator_stop(self, process, thread):
        frame = thread.GetFrameAtIndex(0)
        key = (thread.GetThreadID(), frame.GetPC())
        if key in self.pending:
            kind, size, old = self.pending.pop(key)
            address = self.register(frame, 0, True)
            if kind == 'realloc' and old in self.blocks and (address or size == 0):
                self.freed[old] = self.blocks.pop(old)
            if address:
                self.serial += 1
                self.freed.pop(address, None)
                self.blocks[address] = (size, self.serial)
            return True
        for index in range(thread.GetStopReasonDataCount() // 2):
            kind = self.allocator_ids.get(thread.GetStopReasonDataAtIndex(index * 2))
            if not kind:
                continue
            caller = thread.GetFrameAtIndex(1)
            if not self.user_frame(caller):
                return True
            first = self.register(frame, 0)
            if kind == 'free':
                if first in self.blocks:
                    self.freed[first] = self.blocks.pop(first)
                return True
            second = self.register(frame, 1) if kind in ('calloc', 'realloc') else 0
            size = first * second if kind == 'calloc' else second if kind == 'realloc' else first
            at = caller.GetPC()
            self.target.BreakpointCreateByAddress(at).SetOneShot(True)
            self.pending[(thread.GetThreadID(), at)] = (kind, size, first if kind == 'realloc' else None)
            return True
        return False

    def return_stop(self, thread):
        frame = thread.GetFrameAtIndex(0)
        key = (thread.GetThreadID(), frame.GetPC(), frame.GetCFA())
        returned = self.returning.pop(key, None)
        if returned:
            self.live_frames.difference_update(returned)
            return True
        return False

    def values(self, frame):
        line = frame.GetLineEntry().GetLine()
        out = []
        for value in frame.GetVariables(True, True, True, True):
            declaration = value.GetDeclaration()
            if declaration.IsValid() and declaration.GetFileSpec().GetFilename() not in (None, '', 'main.c'):
                continue
            argument = value.GetValueType() == lldb.eValueTypeVariableArgument
            global_ = value.GetValueType() == lldb.eValueTypeVariableGlobal
            if not argument and not global_ and declaration.IsValid() and declaration.GetLine() >= line:
                continue
            out.append(value)
        return out

    def encode(self, value, heap, names, depth=0):
        if depth > 5 or not value.IsValid() or value.GetError().Fail():
            return ['C_NOTE', '값을 읽을 수 없어요']
        typ = value.GetType().GetCanonicalType()
        type_class = typ.GetTypeClass()
        if type_class & lldb.eTypeClassPointer:
            address = value.GetValueAsUnsigned()
            if not address:
                return None
            named = names.get((address, self.type_key(typ.GetPointeeType())))
            if named:
                return ['C_PTR', named]
            for start, (size, serial) in self.blocks.items():
                if start <= address < start + size:
                    pointee = typ.GetPointeeType()
                    width = pointee.GetByteSize()
                    if not width or pointee.GetTypeClass() & lldb.eTypeClassFunction:
                        return ['C_NOTE', '주소만 확인할 수 있는 포인터예요']
                    offset = address - start
                    hid = self.object_id(('allocation', serial, offset, self.type_key(pointee)))
                    if hid not in heap:
                        heap[hid] = ['ARRAY', pointee.GetName()]
                        available = (size - offset) // width
                        count = min(available, MAX_CHILDREN)
                        self.truncated |= available > MAX_CHILDREN
                        values = []
                        for index in range(count):
                            child = self.target.CreateValueFromAddress(
                                'item', lldb.SBAddress(address + index * width, self.target), pointee)
                            values.append(self.encode(child, heap, names, depth + 1))
                        heap[hid] = ['INSTANCE', f'동적 할당 · {pointee.GetName()} · +{offset}바이트',
                                     *[[f'[{index}]', child] for index, child in enumerate(values)]]
                    return ['REF', int(hid)]
            if any(start <= address < start + size for start, (size, _) in self.freed.items()):
                return ['C_NOTE', f'0x{address:x} · 해제된 동적 메모리']
            return ['C_NOTE', f'0x{address:x} · 대상 범위를 몰라 따라가지 않아요']
        if type_class & (lldb.eTypeClassArray | lldb.eTypeClassStruct | lldb.eTypeClassUnion):
            if type_class & lldb.eTypeClassUnion:
                return ['C_NOTE', 'union은 어느 필드가 활성인지 알 수 없어요']
            hid = self.object_id(('object', value.GetLoadAddress(), self.type_key(typ)))
            if hid not in heap:
                heap[hid] = ['ARRAY', value.GetTypeName()]
                children = [value.GetChildAtIndex(i) for i in range(min(value.GetNumChildren(), MAX_CHILDREN))]
                self.truncated |= value.GetNumChildren() > MAX_CHILDREN
                if type_class & lldb.eTypeClassArray:
                    heap[hid] = ['ARRAY', value.GetTypeName(), *[self.encode(child, heap, names, depth + 1) for child in children]]
                else:
                    heap[hid] = ['INSTANCE', value.GetTypeName(),
                                 *[[child.GetName(), self.encode(child, heap, names, depth + 1)] for child in children]]
            return ['REF', int(hid)]
        basic = typ.GetBasicType()
        if basic == lldb.eBasicTypeBool:
            return bool(value.GetValueAsUnsigned())
        if basic == lldb.eBasicTypeLongDouble:
            raw = value.GetValue()
            return ['SPECIAL_FLOAT', raw] if raw is not None else ['C_NOTE', 'long double 값을 읽을 수 없어요']
        if basic in (lldb.eBasicTypeFloat, lldb.eBasicTypeDouble):
            try:
                number = float(value.GetValue())
                return number if math.isfinite(number) else ['SPECIAL_FLOAT', str(number)]
            except (TypeError, ValueError):
                return ['C_NOTE', value.GetValue() or '값을 읽을 수 없어요']
        if basic in (lldb.eBasicTypeChar, lldb.eBasicTypeSignedChar, lldb.eBasicTypeUnsignedChar):
            number = value.GetValueAsUnsigned() & 255
            return ['CHAR', chr(number)]
        if type_class & (lldb.eTypeClassBuiltin | lldb.eTypeClassEnumeration):
            if value.GetByteSize() > 8:
                raw = value.GetValue()
                return ['LONG', raw] if raw is not None else ['C_NOTE', f'{value.GetTypeName()} 값을 읽을 수 없어요']
            signed = bool(typ.GetTypeFlags() & lldb.eTypeIsSigned)
            number = value.GetValueAsSigned() if signed else value.GetValueAsUnsigned()
            return ['LONG', str(number)] if abs(number) > (1 << 53) - 1 else number
        return ['C_NOTE', f'{value.GetTypeName()} 형식은 아직 그리지 않아요']

    def snapshot(self, thread):
        frames = [frame for frame in thread if self.user_frame(frame)]
        if not frames:
            return None
        frames.reverse()
        collected = [(frame, self.values(frame)) for frame in frames]
        names = {}
        def named_cells(value, name, depth=0):
            address = value.GetLoadAddress()
            if address != lldb.LLDB_INVALID_ADDRESS:
                names[(address, self.type_key(value.GetType()))] = name
            typ = value.GetType().GetCanonicalType()
            if depth >= 5 or not typ.GetTypeClass() & (lldb.eTypeClassArray | lldb.eTypeClassStruct):
                return
            for index in range(min(value.GetNumChildren(), MAX_CHILDREN)):
                child = value.GetChildAtIndex(index)
                suffix = f'[{index}]' if typ.GetTypeClass() & lldb.eTypeClassArray else '.' + child.GetName()
                named_cells(child, name + suffix, depth + 1)
        for frame, values in collected:
            for value in values:
                named_cells(value, value.GetName())
        heap, stack, live, globals_ = {}, [], set(), {}
        for frame, values in collected:
            key = (frame.GetFunctionName(), frame.GetCFA())
            live.add(key)
            if key not in self.live_frames:
                self.frame_ids[key] = self.next_frame
                self.next_frame += 1
            locals_ = []
            for value in values:
                if value.GetValueType() == lldb.eValueTypeVariableGlobal:
                    globals_[value.GetName()] = self.encode(value, heap, names)
                else:
                    locals_.append(value)
            encoded = {value.GetName(): self.encode(value, heap, names) for value in locals_}
            uninitialized = []
            for value in locals_:
                declaration = value.GetDeclaration()
                if declaration.IsValid() and value.GetValueType() != lldb.eValueTypeVariableArgument:
                    line = declaration.GetLine()
                    if self.declarations.get(f'{line}:{value.GetName()}') is False:
                        uninitialized.append(value.GetName())
            stack.append({'func_name': frame.GetFunctionName(), 'frame_id': self.frame_ids[key],
                          'line': frame.GetLineEntry().GetLine(), 'is_highlighted': False,
                          'encoded_locals': encoded, 'ordered_varnames': list(encoded),
                          'declared_without_initializer': uninitialized,
                          'static_names': [value.GetName() for value in locals_ if value.GetValueType() == lldb.eValueTypeVariableStatic]})
        stack[-1]['is_highlighted'] = True
        represented = {key[1] for key, hid in self.view_ids.items()
                       if key[0] == 'allocation' and str(hid) in heap}
        for index, (address, (size, serial)) in enumerate(self.blocks.items()):
            if index >= MAX_CHILDREN:
                self.truncated = True
                break
            if serial not in represented:
                hid = self.object_id(('allocation-metadata', serial))
                heap[hid] = ['INSTANCE', '동적 할당 · 자료형 미확인',
                             ['주소', f'0x{address:x}'], ['바이트 수', size],
                             ['상태', ['C_NOTE', '현재 포인터에서 자료형을 확인하지 못했어요']]]
        top = frames[-1]
        event = 'call' if (top.GetFunctionName(), top.GetCFA()) not in self.live_frames else 'step_line'
        caller = thread.GetFrameAtIndex(1)
        if event == 'call' and self.user_frame(caller):
            at = caller.GetPC()
            key = (thread.GetThreadID(), at, caller.GetCFA())
            self.returning.setdefault(key, set()).add((top.GetFunctionName(), top.GetCFA()))
            if at not in self.return_addresses:
                self.target.BreakpointCreateByAddress(at)
                self.return_addresses.add(at)
        self.live_frames = live
        return {'event': event, 'line': top.GetLineEntry().GetLine(), 'func_name': top.GetFunctionName(),
                'stdout': _read(os.path.join(self.case, 'trace-stdout.txt')), 'globals': globals_,
                'ordered_globals': list(globals_), 'stack_to_render': stack, 'heap': heap}


def trace(debugger, command, result, internal_dict):
    case = os.path.abspath(shlex.split(command)[0])
    source = _read(os.path.join(case, 'main.c'))
    target = debugger.CreateTarget(os.path.join(case, 'main'))
    debugger.SetAsync(False)
    recorder = Recorder(target, case, source)
    for line in range(1, len(source.splitlines()) + 1):
        target.BreakpointCreateByLocation(os.path.join(case, 'main.c'), line)
    info = target.GetLaunchInfo()
    info.SetWorkingDirectory(case)
    info.SetLaunchFlags(info.GetLaunchFlags() & ~lldb.eLaunchFlagDisableASLR)
    for fd, filename, read in [(0, 'stdin.txt', True), (1, 'trace-stdout.txt', False), (2, 'trace-stderr.txt', False)]:
        info.AddOpenFileAction(fd, os.path.join(case, filename), read, not read)
    error = lldb.SBError()
    process = target.Launch(info, error)
    doc = {'code': source, 'stdin': _read(os.path.join(case, 'stdin.txt')), 'language': 'c',
           'compiler': target.GetTriple() + ' · 원본 C 프로그램 · LLDB', 'trace': [], 'problems': [],
           'stepBudget': LIMIT, 'options': {'objects': False}, 'heapTruncated': False,
           'stdout_per_step': False, 'program_runs': 0 if error.Fail() else 1}
    try:
        if error.Fail():
            doc.update(status='unsupported', message='C 디버거를 시작하지 못했어요. ' + str(error))
        else:
            hits = 0
            while process.GetState() == lldb.eStateStopped:
                hits += 1
                if process.GetNumThreads() > 1:
                    doc.update(status='unsupported', message='여러 스레드의 실행 흐름은 아직 그리지 않아요', trace=[])
                    break
                if sum(1 for frame in process.GetSelectedThread() if recorder.user_frame(frame)) > 64:
                    doc.update(status='step_limit', message='함수 호출이 64단계보다 깊어 기록을 멈췄어요')
                    break
                thread = process.GetSelectedThread()
                if thread.GetStopReason() in (lldb.eStopReasonException, lldb.eStopReasonSignal):
                    doc.update(status='uncaught_exception', message=thread.GetStopDescription(512))
                    break
                if hits > 20000 or len(doc['trace']) >= LIMIT:
                    doc.update(status='step_limit')
                    break
                if not recorder.allocator_stop(process, thread) and not recorder.return_stop(thread):
                    snapshot = recorder.snapshot(thread)
                    if snapshot:
                        doc['trace'].append(snapshot)
                process.Continue()
            if 'status' not in doc:
                doc['status'] = 'ok' if process.GetExitStatus() == 0 else 'uncaught_exception'
            doc['exit_code'] = process.GetExitStatus() if process.GetState() == lldb.eStateExited else None
        doc['stdout'] = _read(os.path.join(case, 'trace-stdout.txt'))
        doc['heapTruncated'] = recorder.truncated
        if doc['trace']:
            doc['trace'][-1]['stdout'] = doc['stdout']
        with open(os.path.join(case, 'c_flow.json'), 'w', encoding='utf-8') as out:
            json.dump(doc, out, ensure_ascii=False, allow_nan=False)
    finally:
        if process.IsValid() and process.GetState() != lldb.eStateExited:
            process.Kill()


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f mac_lldb.trace mq-c-trace')
