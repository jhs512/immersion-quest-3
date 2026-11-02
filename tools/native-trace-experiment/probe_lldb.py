"""Raw LLDB dump: every line stop of an unmodified debug binary, every in-scope variable as LLDB sees it."""
import json
import os
import shlex

import lldb


def dump(value, depth=0):
    out = {'name': value.GetName(), 'type': value.GetTypeName(), 'value': value.GetValue(),
           'summary': value.GetSummary(), 'address': value.GetLoadAddress(),
           'synthetic': value.IsSynthetic(), 'in_scope': value.IsInScope()}
    declaration = value.GetDeclaration()
    if declaration.IsValid():
        out['declared'] = declaration.GetLine()
    if depth < 3:
        out['children'] = [dump(value.GetChildAtIndex(i), depth + 1) for i in range(min(value.GetNumChildren(), 12))]
    return out


def probe(debugger, command, result, internal_dict):
    case, binary, source = shlex.split(command)
    target = debugger.CreateTarget(os.path.join(case, binary))
    debugger.SetAsync(False)
    path = os.path.join(case, source)
    for line in range(1, len(open(path, encoding='utf-8').readlines()) + 1):
        target.BreakpointCreateByLocation(path, line)
    info = target.GetLaunchInfo()
    info.SetWorkingDirectory(case)
    info.SetLaunchFlags(info.GetLaunchFlags() & ~lldb.eLaunchFlagDisableASLR)
    info.AddOpenFileAction(0, '/dev/null', True, False)
    info.AddOpenFileAction(1, os.path.join(case, 'probe-stdout.txt'), False, True)
    error = lldb.SBError()
    process = target.Launch(info, error)
    doc = {'target': target.GetTriple(), 'launch_error': None if error.Success() else str(error), 'stops': []}
    try:
        while error.Success() and process.GetState() == lldb.eStateStopped and len(doc['stops']) < 200:
            thread = process.GetSelectedThread()
            frames = []
            for frame in thread:
                entry = frame.GetLineEntry()
                if not entry.IsValid() or entry.GetFileSpec().GetFilename() != source:
                    continue
                frames.append({'function': frame.GetFunctionName(), 'display': frame.GetDisplayFunctionName(),
                               'line': entry.GetLine(), 'cfa': frame.GetCFA(),
                               'values': [dump(v) for v in frame.GetVariables(True, True, True, True)]})
            doc['stops'].append({'reason': thread.GetStopReason(), 'frames': frames})
            process.Continue()
        doc['state'] = process.GetState()
        doc['exit'] = process.GetExitStatus()
    finally:
        if process.IsValid() and process.GetState() != lldb.eStateExited:
            process.Kill()
        with open(os.path.join(case, 'probe-' + source + '.json'), 'w', encoding='utf-8') as out:
            json.dump(doc, out, ensure_ascii=False, indent=1)


def __lldb_init_module(debugger, internal_dict):
    debugger.HandleCommand('command script add -f probe_lldb.probe mq-probe')
