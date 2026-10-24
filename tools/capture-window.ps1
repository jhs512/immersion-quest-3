# Capture a process's main window, including WebView2 content (PrintWindow, PW_RENDERFULLCONTENT).
# Used by debug self-tests to keep real native screenshots as evidence.
param([Parameter(Mandatory=$true)][int]$ProcessId,[Parameter(Mandatory=$true)][string]$Out)
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
Add-Type @'
using System;using System.Runtime.InteropServices;
public static class MqCapture {
 public struct Rect {public int Left,Top,Right,Bottom;}
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr window,out Rect rect);
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr window,IntPtr dc,uint flags);
 [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
}
'@
# Physical pixels: without this, a scaled display crops the capture to the logical size.
[MqCapture]::SetProcessDPIAware() | Out-Null
$window=(Get-Process -Id $ProcessId).MainWindowHandle
if ($window -eq [IntPtr]::Zero) {throw 'no main window'}
$rect=New-Object MqCapture+Rect
[MqCapture]::GetWindowRect($window,[ref]$rect) | Out-Null
$bitmap=New-Object System.Drawing.Bitmap(($rect.Right-$rect.Left),($rect.Bottom-$rect.Top))
$graphics=[System.Drawing.Graphics]::FromImage($bitmap)
$dc=$graphics.GetHdc()
try {[MqCapture]::PrintWindow($window,$dc,2) | Out-Null} finally {$graphics.ReleaseHdc($dc)}
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Out) | Out-Null
$bitmap.Save($Out,[System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose();$bitmap.Dispose()
