import json
import os
import shlex

import lldb


def probe(debugger, command, result, internal_dict):
    case = os.path.abspath(shlex.split(command)[0])
    source = os.path.join(case, 'main.c')
    target = debugger.CreateTarget(os.path.join(case, 'trace-main'))
    debugger.SetAsync(False)
    for line in range(1, len(open(source, encoding='utf-8').readlines()) + 1):
        target.BreakpointCreateByLocation(source, line)
    info = target.GetLaunchInfo()
    info.SetWorkingDirectory(case)
    info.SetLaunchFlags(info.GetLaunchFlags() & ~lldb.eLaunchFlagDisableASLR)
    info.AddOpenFileAction(0, os.path.join(case, 'stdin.txt'), True, False)
    info.AddOpenFileAction(1, os.path.join(case, 'trace-stdout.txt'), False, True)
    info.AddOpenFileAction(2, os.path.join(case, 'trace-stderr.txt'), False, True)
    error = lldb.SBError()
    process = target.Launch(info, error)
    if not error.Success():
        result.SetError(str(error))
        return
    stops = []
    try:
        while process.GetState() == lldb.eStateStopped and len(stops) < 100:
            thread = process.GetSelectedThread()
            frames = []
            for frame in thread:
                entry = frame.GetLineEntry()
                if not entry.IsValid() or entry.GetFileSpec().GetFilename() != 'main.c':
                    continue
                values = []
                for value in frame.GetVariables(True, True, True, True):
                    values.append({
                        'name': value.GetName(), 'type': value.GetTypeName(),
                        'size': value.GetByteSize(), 'value': value.GetValue(),
                        'address': value.GetLoadAddress(),
                        'children': [{'name': child.GetName(), 'value': child.GetValue()}
                                     for child in value],
                    })
                frames.append({'function': frame.GetFunctionName(), 'line': entry.GetLine(), 'values': values})
            if frames:
                stops.append(frames)
            process.Continue()
        doc = {'target': target.GetTriple(), 'stops': stops,
               'state': process.GetState(), 'exit': process.GetExitStatus()}
        with open(os.path.join(case, 'probe.json'), 'w', encoding='utf-8') as out:
            json.dump(doc, out, ensure_ascii=False, indent=2)
    finally:
        if process.GetState() != lldb.eStateExited:
            process.Kill()


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f probe.probe mq-probe')
