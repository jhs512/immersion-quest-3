// Reads and clicks the native report dialog on a CI Mac: System Events does not list its window.
// read <png>: finds the dialog through CGWindowList (a modal panel, layer 8), captures it with screencapture, OCRs it.
// click <x> <y>: posts a left click at screen points.
// activate <pid>...: brings apps forward; the dialog panel hides while its app is in the background.
import Cocoa
import Vision

let args = CommandLine.arguments
func mouse(_ type: CGEventType, _ point: CGPoint) {
    CGEvent(mouseEventSource: nil, mouseType: type, mouseCursorPosition: point, mouseButton: .left)!.post(tap: .cghidEventTap)
}
if args[1] == "activate" {
    for pid in args.dropFirst(2) {
        print(pid, NSRunningApplication(processIdentifier: pid_t(pid)!)?.activate(options: [.activateIgnoringOtherApps]) ?? false)
    }
    exit(0)
}
if args[1] == "click" {
    let point = CGPoint(x: Double(args[2])!, y: Double(args[3])!)
    mouse(.mouseMoved, point)
    usleep(150_000)
    mouse(.leftMouseDown, point)
    usleep(80_000)
    mouse(.leftMouseUp, point)
    exit(0)
}
let list = CGWindowListCopyWindowInfo([.optionAll, .excludeDesktopElements], kCGNullWindowID) as! [[String: Any]]
var windows: [[String: Any]] = []
var best: (CGWindowID, CGRect)? = nil
for window in list {
    let owner = window[kCGWindowOwnerName as String] as? String ?? ""
    let layer = window[kCGWindowLayer as String] as? Int ?? -1
    let onscreen = window[kCGWindowIsOnscreen as String] as? Bool ?? false
    let pid = window[kCGWindowOwnerPID as String] as? Int ?? 0
    let application = NSRunningApplication(processIdentifier: pid_t(pid))
    var rect = CGRect.zero
    if let bounds = window[kCGWindowBounds as String] { CGRectMakeWithDictionaryRepresentation(bounds as! CFDictionary, &rect) }
    windows.append(["owner": owner, "pid": pid, "layer": layer, "onscreen": onscreen, "app_hidden": application?.isHidden ?? false, "app_active": application?.isActive ?? false, "bounds": [rect.minX, rect.minY, rect.width, rect.height]])
    if onscreen && [0, 8].contains(layer) && ["osascript", "MQ", "molip-quest"].contains(owner)
        && (300...900).contains(rect.width) && (150...600).contains(rect.height)
        && (best == nil || rect.width * rect.height < best!.1.width * best!.1.height) {
        best = (window[kCGWindowNumber as String] as! CGWindowID, rect)
    }
}
var lines: [[String: Any]] = []
if let (id, rect) = best {
    let capture = Process()
    capture.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
    capture.arguments = ["-x", "-o", "-l", String(id), args[2]]
    try capture.run()
    capture.waitUntilExit()
    if let image = NSImage(contentsOfFile: args[2])?.cgImage(forProposedRect: nil, context: nil, hints: nil) {
        let request = VNRecognizeTextRequest()
        request.recognitionLanguages = ["ko-KR", "en-US"]
        request.recognitionLevel = .accurate
        try? VNImageRequestHandler(cgImage: image).perform([request])
        for observation in request.results ?? [] {
            guard let text = observation.topCandidates(1).first?.string else { continue }
            let box = observation.boundingBox
            lines.append(["text": text, "x": rect.minX + box.midX * rect.width, "y": rect.minY + (1 - box.midY) * rect.height])
        }
    }
}
let dialog: Any = best.map { [$0.1.minX, $0.1.minY, $0.1.width, $0.1.height] } ?? NSNull()
print(String(data: try JSONSerialization.data(withJSONObject: ["dialog": dialog, "lines": lines, "windows": windows]), encoding: .utf8)!)
