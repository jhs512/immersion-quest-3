param([string]$Binary)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class DiagnosticNative {
 public delegate bool EnumWindowsProc(IntPtr window, IntPtr data);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr data);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr window,System.Text.StringBuilder text,int count);
 public struct Rect {public int Left,Top,Right,Bottom;}
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr window,out Rect rect);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr window,IntPtr dc,uint flags);
 [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr window,uint message,IntPtr w,IntPtr l);
 public static IntPtr Find(string title) {
   IntPtr found=IntPtr.Zero;
   EnumWindows((window,data)=>{var text=new System.Text.StringBuilder(256);GetWindowText(window,text,256);if(text.ToString()==title){found=window;return false;}return true;},IntPtr.Zero);
   return found;
 }
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr window,System.Text.StringBuilder text,int count);
 [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr parent,EnumWindowsProc callback,IntPtr data);
 [DllImport("user32.dll",EntryPoint="SendMessageTimeoutW",CharSet=CharSet.Unicode)] private static extern IntPtr SendText(IntPtr window,uint msg,UIntPtr w,string text,uint flags,uint timeout,out UIntPtr result);
 [DllImport("user32.dll",EntryPoint="SendMessageTimeoutW",CharSet=CharSet.Unicode)] private static extern IntPtr ReadText(IntPtr window,uint msg,UIntPtr w,System.Text.StringBuilder text,uint flags,uint timeout,out UIntPtr result);
 public static IntPtr Edit(IntPtr parent) {
   IntPtr found=IntPtr.Zero;
   EnumChildWindows(parent,(window,data)=>{var name=new System.Text.StringBuilder(256);GetClassName(window,name,256);if(name.ToString().StartsWith("WindowsForms10.EDIT")||name.ToString()=="EDIT"){found=window;return false;}return true;},IntPtr.Zero);
   return found;
 }
 public static bool SetAndCheck(IntPtr edit,string value) {
   UIntPtr result; if(SendText(edit,12,UIntPtr.Zero,value,2,1000,out result)==IntPtr.Zero)return false;
   var text=new System.Text.StringBuilder(256);ReadText(edit,13,(UIntPtr)256,text,2,1000,out result);return text.ToString()==value;
 }
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr window);
 [DllImport("user32.dll")] public static extern void keybd_event(byte key, byte scan, uint flags, UIntPtr extra);
 [DllImport("ntdll.dll")] public static extern int NtSuspendProcess(IntPtr process);
 [DllImport("ntdll.dll")] public static extern int NtResumeProcess(IntPtr process);
}
'@
$root=Join-Path ([System.IO.Path]::GetTempPath()) ('mq-native-report-test-'+[Guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $root | Out-Null
$hostScript=Join-Path $root 'host.ps1'
$hostSource=@'
param([string]$Ready)
Add-Type -AssemblyName System.Windows.Forms
$form=New-Object System.Windows.Forms.Form
$form.Text='MQ';$form.Width=700;$form.Height=500;$form.StartPosition='CenterScreen'
$form.Add_Shown({[System.IO.File]::WriteAllText($Ready,'ready');$form.Activate()})
$form.ShowDialog() | Out-Null
'@
[System.IO.File]::WriteAllText($hostScript,$hostSource,(New-Object System.Text.UTF8Encoding($true)))
$ready=Join-Path $root 'host.ready'
$hostInfo=New-Object System.Diagnostics.ProcessStartInfo
$hostInfo.FileName='powershell.exe';$hostInfo.Arguments='-NoProfile -ExecutionPolicy Bypass -File "'+$hostScript+'" "'+$ready+'"'
$hostInfo.UseShellExecute=$false;$hostInfo.CreateNoWindow=$true
$testHost=[System.Diagnostics.Process]::Start($hostInfo)
$agent=$null;$suspended=$false
$previous=$env:MOLIP_DATA_DIR;$previousPilot=$env:MOLIP_PILOT
function Wait-Until([scriptblock]$Action,[int]$Seconds=8) {
 $end=[DateTime]::UtcNow.AddSeconds($Seconds)
 do { $value=& $Action; if ($value) {return $value};Start-Sleep -Milliseconds 100 } while ([DateTime]::UtcNow -lt $end)
 throw 'Native dialog test timed out'
}
function Find-Dialog([string]$Title) {
 $handle=[DiagnosticNative]::Find($Title)
 if ($handle.ToInt64() -ne 0) {return $handle}
 return $null
}
function Cancel-Dialog($Dialog) {
 [DiagnosticNative]::PostMessage($Dialog,0x10,[IntPtr]::Zero,[IntPtr]::Zero) | Out-Null
}
try {
 Wait-Until {Test-Path -LiteralPath $ready} | Out-Null
 $testHost.Refresh()
 $location=@{course_id='course_fixture';course_title='Fixture';lesson_id='lesson_fixture';lesson_title='Fixture lesson';lesson_repository='fixture/lesson';revision='fixture-1';task_id='task_fixture';task_title='Fixture step'}
 $location | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $root ('report-location-'+$testHost.Id+'.json')) -Encoding UTF8
 # Rust reads UTF-8 JSON without a BOM.
 $locationPath=Join-Path $root ('report-location-'+$testHost.Id+'.json')
 [System.IO.File]::WriteAllText($locationPath,($location | ConvertTo-Json),(New-Object System.Text.UTF8Encoding($false)))
 $env:MOLIP_DATA_DIR=$root;$env:MOLIP_PILOT=$null
 $agentInfo=New-Object System.Diagnostics.ProcessStartInfo
 $agentInfo.FileName=$Binary;$agentInfo.Arguments='--diagnostics-agent '+$testHost.Id
 $agentInfo.UseShellExecute=$false;$agentInfo.CreateNoWindow=$true;$agentInfo.RedirectStandardInput=$true
 $agent=[System.Diagnostics.Process]::Start($agentInfo)
 $agentReady=Join-Path $root ('report-agent-'+$testHost.Id+'.json')
 Wait-Until {Test-Path -LiteralPath $agentReady} | Out-Null
 $configuration=Get-Content -LiteralPath $agentReady -Raw | ConvertFrom-Json
 if (!$configuration.bug_hotkey) {throw 'Emergency hotkey could not be registered'}
 [DiagnosticNative]::SetForegroundWindow($testHost.MainWindowHandle) | Out-Null
 Start-Sleep -Milliseconds 250
 if ([DiagnosticNative]::NtSuspendProcess($testHost.Handle) -ne 0) {throw 'Could not suspend owned fixture process'}
 $suspended=$true
 $clock=[System.Diagnostics.Stopwatch]::StartNew()
 foreach ($key in @(0x11,0x12,0x10,0x42)) {[DiagnosticNative]::keybd_event($key,0,0,[UIntPtr]::Zero)}
 foreach ($key in @(0x42,0x10,0x12,0x11)) {[DiagnosticNative]::keybd_event($key,0,2,[UIntPtr]::Zero)}
 $dialog=Wait-Until {Find-Dialog 'MQ · 앱 오류 신고'}
 $clock.Stop()
 $edit=Wait-Until { $handle=[DiagnosticNative]::Edit($dialog); if($handle.ToInt64() -ne 0){return $handle} }
 if (![DiagnosticNative]::SetAndCheck($edit,'추가 설명 입력 검증')) {throw 'Native text input failed'}
 Start-Sleep -Milliseconds 200
 Add-Type -AssemblyName System.Drawing
 $rect=New-Object DiagnosticNative+Rect
 [DiagnosticNative]::GetWindowRect($dialog,[ref]$rect) | Out-Null
 $bitmap=New-Object System.Drawing.Bitmap(($rect.Right-$rect.Left),($rect.Bottom-$rect.Top))
 $graphics=[System.Drawing.Graphics]::FromImage($bitmap)
 $dc=$graphics.GetHdc()
 try {[DiagnosticNative]::PrintWindow($dialog,$dc,2) | Out-Null} finally {$graphics.ReleaseHdc($dc)}
 $bitmap.Save((Join-Path $PWD 'target/native-report-dialog.png'),[System.Drawing.Imaging.ImageFormat]::Png)
 $graphics.Dispose();$bitmap.Dispose()
 Cancel-Dialog $dialog
 [DiagnosticNative]::NtResumeProcess($testHost.Handle) | Out-Null;$suspended=$false
 Wait-Until {!(Find-Dialog 'MQ · 앱 오류 신고')} | Out-Null
 Start-Sleep -Milliseconds 700
 $agent.StandardInput.WriteLine('content');$agent.StandardInput.Flush()
 $content=Wait-Until {Find-Dialog 'MQ · 문제 신고'}
 Cancel-Dialog $content
 $drafts=@(Get-ChildItem -LiteralPath (Join-Path $root 'bug-reports') -Filter draft.json -Recurse | ForEach-Object {Get-Content -LiteralPath $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json})
 if (!($drafts | Where-Object {$_.kind -eq 'bug' -and $_.repository -eq 'jhs512/immersion-quest-3'})) {throw 'App report routed incorrectly'}
 if (!($drafts | Where-Object {$_.kind -eq 'content' -and $_.repository -eq 'fixture/lesson'})) {throw 'Content report routed incorrectly'}
 @{passed=$true;emergency_dialog_seconds=[Math]::Round($clock.Elapsed.TotalSeconds,2);main_process_suspended=$true;content_repository_correct=$true;sent_to_github=$false} | ConvertTo-Json
} finally {
 if ($dialog) {Cancel-Dialog $dialog}
 if ($content) {Cancel-Dialog $content}
 if ($suspended) {[DiagnosticNative]::NtResumeProcess($testHost.Handle) | Out-Null}
 if ($agent -and !$agent.HasExited) {$agent.Kill();$agent.WaitForExit()}
 if (!$testHost.HasExited) {$testHost.Kill();$testHost.WaitForExit()}
 $env:MOLIP_DATA_DIR=$previous;$env:MOLIP_PILOT=$previousPilot
}
