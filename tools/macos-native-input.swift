import AppKit
import ApplicationServices
import CoreGraphics
import Carbon

var report:[String:Any] = ["actualOsInputVerified":false,"permissionsRequested":false,"source":ProcessInfo.processInfo.environment["AUDIT_SOURCE"] ?? "unknown"]
func attr(_ el:AXUIElement,_ name:String)->CFTypeRef? {var value:CFTypeRef?;return AXUIElementCopyAttributeValue(el,name as CFString,&value) == .success ? value:nil}
func nodes(_ root:AXUIElement)->[AXUIElement] {
 var found=[AXUIElement]();var pending=[(root,0)]
 while let (el,depth)=pending.popLast(){found.append(el);if depth<32,let children=attr(el,kAXChildrenAttribute) as? [AXUIElement]{pending += children.map{($0,depth+1)}};if found.count>8000{break}}
 return found
}
func text(_ el:AXUIElement)->String { [kAXTitleAttribute,kAXDescriptionAttribute,kAXValueAttribute].compactMap{attr(el,$0) as? String}.joined(separator:" ") }
func wait(_ label:String,_ body:()->Bool)throws {let until=Date().addingTimeInterval(60);while Date()<until {if body(){return};RunLoop.current.run(until:Date().addingTimeInterval(0.2))};throw NSError(domain:label,code:1)}
let task=Process()
let directory=FileManager.default.temporaryDirectory.appendingPathComponent("mq3-os-input-"+UUID().uuidString)
try FileManager.default.createDirectory(at:directory,withIntermediateDirectories:true)
let trusted=AXIsProcessTrusted(),post=CGPreflightPostEventAccess()
report["accessibilityTrusted"]=trusted;report["postEventsAllowed"]=post
let original=TISCopyCurrentKeyboardInputSource().takeRetainedValue()
defer {TISSelectInputSource(original);if task.isRunning{task.terminate()}}
do {
 guard trusted && post else {throw NSError(domain:"Existing OS automation permissions unavailable; no permission requested",code:2)}
 task.executableURL=URL(fileURLWithPath:CommandLine.arguments[1]);task.currentDirectoryURL=directory
 var env=ProcessInfo.processInfo.environment;env["MOLIP_PILOT"]="1";env.removeValue(forKey:"MOLIP_PILOT_SELF_TEST");env.removeValue(forKey:"MOLIP_PILOT_DIRECTORY");env.removeValue(forKey:"MOLIP_PILOT_OWNER");task.environment=env
 let log=directory.appendingPathComponent("app.log");FileManager.default.createFile(atPath:log.path,contents:nil);task.standardOutput=try FileHandle(forWritingTo:log);task.standardError=task.standardOutput
 try task.run();let pid=task.processIdentifier;report["pid"]=pid
 let app=AXUIElementCreateApplication(pid)
 func owned()throws {guard NSWorkspace.shared.frontmostApplication?.processIdentifier==pid else{throw NSError(domain:"Owned test app lost foreground; event cancelled",code:3)}}
 func key(_ code:CGKeyCode,_ command:Bool=false,_ control:Bool=false)throws {try owned();for down in [true,false] {guard let event=CGEvent(keyboardEventSource:nil,virtualKey:code,keyDown:down) else{throw NSError(domain:"CGEvent creation",code:4)};event.flags=command ? .maskCommand:[];if control {event.flags.insert(.maskControl)};event.post(tap:.cghidEventTap)};Thread.sleep(forTimeInterval:0.2)}
 try wait("catalog"){NSRunningApplication(processIdentifier:pid)?.activate(options:[.activateIgnoringOtherApps]);return nodes(app).contains{text($0).contains("학습 시작")}}
 guard let start=nodes(app).first(where:{text($0).contains("학습 시작") && (attr($0,kAXRoleAttribute) as? String)==kAXButtonRole}) else{throw NSError(domain:"Catalog button unavailable",code:5)}
 guard AXUIElementPerformAction(start,kAXPressAction as CFString) == .success else{throw NSError(domain:"Catalog press failed",code:6)}
 var editor:AXUIElement?
 try wait("editor"){editor=nodes(app).first{(attr($0,kAXRoleAttribute) as? String)==kAXTextAreaRole && text($0).contains("코드 편집기")};return editor != nil}
 guard let editor=editor else{throw NSError(domain:"Editor unavailable",code:7)}
 report["editorLabel"]=text(editor)
 AXUIElementSetAttributeValue(editor,kAXFocusedAttribute as CFString,kCFBooleanTrue)
 Thread.sleep(forTimeInterval:0.5)
 func fullscreenLabel()->String {nodes(app).filter{(attr($0,kAXRoleAttribute) as? String)==kAXButtonRole}.map{text($0)}.first{$0.contains("F11")} ?? ""}
 let beforeFullscreen=fullscreenLabel();report["fullscreenLabelBefore"]=beforeFullscreen
 guard !beforeFullscreen.isEmpty else{throw NSError(domain:"Fullscreen button unavailable",code:11)}
 try key(CGKeyCode(kVK_ANSI_F),true,true)
 try wait("Native control-command-F toggle"){let label=fullscreenLabel();return !label.isEmpty && label != beforeFullscreen}
 Thread.sleep(forTimeInterval:2)
 report["fullscreenLabelAfter"]=fullscreenLabel()
 try key(CGKeyCode(kVK_ANSI_F),true,true)
 try wait("Native control-command-F restore"){fullscreenLabel()==beforeFullscreen}
 report["nativeFullscreenShortcutVerified"]=true
 AXUIElementSetAttributeValue(editor,kAXFocusedAttribute as CFString,kCFBooleanTrue)
 Thread.sleep(forTimeInterval:0.5)
 let pasteboard=NSPasteboard.general
 func copied()throws->String {try key(CGKeyCode(kVK_ANSI_A),true);try key(CGKeyCode(kVK_ANSI_C),true);return pasteboard.string(forType:.string) ?? ""}
 let expected="한글 입력 검증 123"
 pasteboard.clearContents();pasteboard.setString(expected,forType:.string)
 try key(CGKeyCode(kVK_ANSI_A),true);try key(CGKeyCode(kVK_ANSI_V),true)
 let actual=try copied();report["clipboardExpected"]=expected;report["clipboardActual"]=actual
 guard actual==expected else{throw NSError(domain:"Native Cmd+V/C clipboard mismatch",code:8)}
 report["keyboardClipboardVerified"]=true
 let sources=TISCreateInputSourceList(nil,false).takeRetainedValue() as! [TISInputSource]
 func property(_ source:TISInputSource,_ key:CFString)->String {guard let ptr=TISGetInputSourceProperty(source,key) else{return ""};return Unmanaged<CFString>.fromOpaque(ptr).takeUnretainedValue() as String}
 let sourceIds=sources.map{property($0,kTISPropertyInputSourceID)};report["enabledInputSources"]=sourceIds
 if let korean=sources.first(where:{property($0,kTISPropertyInputSourceID).contains("Korean.2SetKorean")}) {
  guard TISSelectInputSource(korean)==noErr else{throw NSError(domain:"Selecting already enabled Korean source failed",code:9)}
  Thread.sleep(forTimeInterval:0.4);try key(CGKeyCode(kVK_ANSI_A),true);try key(CGKeyCode(kVK_Delete))
  for code in [kVK_ANSI_G,kVK_ANSI_K,kVK_ANSI_S,kVK_ANSI_R,kVK_ANSI_M,kVK_ANSI_F,kVK_RightArrow]{try key(CGKeyCode(code))}
  let composed=try copied();report["imeActual"]=composed;report["imeVerified"]=composed=="한글"
  guard composed=="한글" else{throw NSError(domain:"Native Korean IME mismatch",code:10)}
 }else{report["imeVerified"]=false;report["imeLimitation"]="Korean input source not enabled; no system settings changed"}
 report["actualOsInputVerified"]=true;report["status"]="passed"
}catch{report["status"]="failed_or_blocked";report["error"]=String(describing:error)}
if let data=try? JSONSerialization.data(withJSONObject:report,options:[.prettyPrinted,.sortedKeys]),let value=String(data:data,encoding:.utf8){print(value)}
exit(report["actualOsInputVerified"] as? Bool == true ? 0:1)
