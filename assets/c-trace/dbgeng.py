"""Minimal ctypes driver for the Windows debugger engine (C:\\Windows\\System32\\dbgeng.dll, the
engine behind cdb/WinDbg). Nothing is installed: dbgeng ships with Windows. Vtable indices were
computed from Windows SDK 10.0.26100.0 um/DbgEng.h (see report.md).

Debugger(cmdline, stdin_path, stdout_path).run(cmd) -> text output of a debugger command.
"""
import ctypes
from ctypes import wintypes as W

HRESULT = ctypes.c_long


class GUID(ctypes.Structure):
    _fields_ = [('a', ctypes.c_uint32), ('b', ctypes.c_uint16), ('c', ctypes.c_uint16), ('d', ctypes.c_ubyte * 8)]

    def __init__(self, a, b, c, *d):
        super().__init__(a, b, c, (ctypes.c_ubyte * 8)(*d))


IID_IDebugClient = GUID(0x27fe5639, 0x8407, 0x4f47, 0x83, 0x64, 0xee, 0x11, 0x8f, 0xb0, 0x8a, 0xc8)
IID_IDebugControl = GUID(0x5182e668, 0x105e, 0x416e, 0xad, 0x92, 0x24, 0xef, 0x80, 0x04, 0x24, 0xba)
IID_IDebugOutputCallbacks = GUID(0x4bf58045, 0xd654, 0x4c40, 0xb0, 0xaf, 0x68, 0x30, 0x90, 0xf3, 0x56, 0xdc)

# IDebugClient / IDebugControl vtable slots (DbgEng.h order, IUnknown included)
CLIENT = {'QueryInterface': 0, 'Release': 2, 'CreateProcessAndAttach': 14, 'TerminateProcesses': 24,
          'EndSession': 26, 'GetExitCode': 27, 'SetOutputCallbacks': 34}
CONTROL = {'Release': 2, 'GetExecutionStatus': 49, 'SetExecutionStatus': 50, 'Execute': 66, 'WaitForEvent': 93, 'AddEngineOptions': 54}  # STDMETHODV slots counted
DEBUG_STATUS_GO, DEBUG_STATUS_BREAK, DEBUG_STATUS_NO_DEBUGGEE = 1, 6, 7
DEBUG_ONLY_THIS_PROCESS = 0x2
DEBUG_END_ACTIVE_TERMINATE = 1
STARTF_USESTDHANDLES = 0x100
INFINITE = 0xFFFFFFFF


def method(obj, index, *argtypes):
    vtbl = ctypes.cast(obj, ctypes.POINTER(ctypes.POINTER(ctypes.c_void_p))).contents
    return ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, *argtypes)(vtbl[index])


class Debugger:
    def __init__(self, cmdline, stdin_path, stdout_path):
        self.chunks = []
        self.dbgeng = ctypes.WinDLL(r'C:\Windows\System32\dbgeng.dll')
        self.client = ctypes.c_void_p()
        hr = self.dbgeng.DebugCreate(ctypes.byref(IID_IDebugClient), ctypes.byref(self.client))
        if hr: raise OSError(f'DebugCreate {hr:#x}')
        self.control = ctypes.c_void_p()
        hr = method(self.client, CLIENT['QueryInterface'], ctypes.c_void_p, ctypes.c_void_p)(
            self.client, ctypes.byref(IID_IDebugControl), ctypes.byref(self.control))
        if hr: raise OSError(f'QueryInterface IDebugControl {hr:#x}')
        self._install_output()
        # Stop at the loader's initial breakpoint so breakpoints can be set before main runs.
        method(self.control, CONTROL['AddEngineOptions'], ctypes.c_ulong)(self.control, 0x20)  # DEBUG_ENGOPT_INITIAL_BREAK
        # The debuggee inherits our standard handles; point them at files for its stdin/stdout.
        k32 = ctypes.WinDLL('kernel32', use_last_error=True)
        k32.CreateFileW.restype = W.HANDLE
        sa = (ctypes.c_byte * 24)(); ctypes.c_uint32.from_buffer(sa).value = 24; sa[16] = 1  # bInheritHandle
        h_in = k32.CreateFileW(stdin_path, 0x80000000, 1, ctypes.byref(sa), 3, 0, None)
        h_out = k32.CreateFileW(stdout_path, 0x40000000, 1, ctypes.byref(sa), 2, 0, None)
        self.saved = [k32.GetStdHandle(-10), k32.GetStdHandle(-11), k32.GetStdHandle(-12)]
        k32.SetStdHandle(-10, h_in); k32.SetStdHandle(-11, h_out); k32.SetStdHandle(-12, h_out)
        try:
            hr = method(self.client, CLIENT['CreateProcessAndAttach'], ctypes.c_uint64, ctypes.c_char_p, ctypes.c_ulong,
                        ctypes.c_ulong, ctypes.c_ulong)(self.client, 0, cmdline.encode('mbcs'), DEBUG_ONLY_THIS_PROCESS, 0, 0)
            if hr: raise OSError(f'CreateProcessAndAttach {hr:#x}')
        finally:
            for n, h in zip((-10, -11, -12), self.saved): k32.SetStdHandle(n, h)
        self.k32, self.handles = k32, (h_in, h_out)
        self.wait()   # initial break

    def _install_output(self):
        chunks = self.chunks
        QI = ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
        REF = ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p)
        OUT = ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, ctypes.c_ulong, ctypes.c_char_p)
        wanted = {bytes(IID_IDebugOutputCallbacks), bytes(GUID(0, 0, 0, 0xC0, 0, 0, 0, 0, 0, 0, 0x46))}  # + IUnknown

        def query(this, iid, out):
            # Only the plain IDebugOutputCallbacks is offered; saying yes to ...Wide/...2 would make the
            # engine call slots this object does not have.
            if ctypes.string_at(iid, 16) in wanted:
                out[0] = this
                return 0
            out[0] = None
            return ctypes.c_long(0x80004002).value  # E_NOINTERFACE
        self._fns = [QI(query), REF(lambda this: 1), REF(lambda this: 1),
                     OUT(lambda this, mask, text: (chunks.append(text.decode('mbcs', 'replace')), 0)[1])]
        self._vtbl = (ctypes.c_void_p * 4)(*[ctypes.cast(f, ctypes.c_void_p) for f in self._fns])
        self._obj = ctypes.pointer(ctypes.pointer(self._vtbl))
        hr = method(self.client, CLIENT['SetOutputCallbacks'], ctypes.c_void_p)(self.client, ctypes.cast(self._obj, ctypes.c_void_p))
        if hr: raise OSError(f'SetOutputCallbacks {hr:#x}')

    def run(self, command):
        self.chunks.clear()
        method(self.control, CONTROL['Execute'], ctypes.c_ulong, ctypes.c_char_p, ctypes.c_ulong)(
            self.control, 0, command.encode('mbcs'), 0)
        return ''.join(self.chunks)

    def wait(self, ms=INFINITE):
        self.chunks.clear()
        hr = method(self.control, CONTROL['WaitForEvent'], ctypes.c_ulong, ctypes.c_ulong)(self.control, 0, ms)
        return hr, ''.join(self.chunks)

    def status(self):
        s = ctypes.c_ulong()
        method(self.control, CONTROL['GetExecutionStatus'], ctypes.c_void_p)(self.control, ctypes.byref(s))
        return s.value

    def go(self):
        method(self.control, CONTROL['SetExecutionStatus'], ctypes.c_ulong)(self.control, DEBUG_STATUS_GO)
        return self.wait()

    def close(self):
        try:
            method(self.client, CLIENT['EndSession'], ctypes.c_ulong)(self.client, DEBUG_END_ACTIVE_TERMINATE)
        finally:
            for h in self.handles: self.k32.CloseHandle(h)
