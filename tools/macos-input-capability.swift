import Foundation
import ApplicationServices
import CoreGraphics
// Read-only checks: no permission requests and no input events are posted.
let ax = AXIsProcessTrusted()
let post = CGPreflightPostEventAccess()
let result: [String: Any] = [
    "accessibilityTrusted": ax,
    "postEventsAllowed": post,
    "capabilityAvailable": ax && post,
    "actualOsInputVerified": false,
    "permissionsRequested": false,
    "status": ax && post ? "capability_available_not_yet_tested" : "blocked_by_os_input_permission",
    "system": ProcessInfo.processInfo.operatingSystemVersionString
]
let data = try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys])
print(String(decoding: data, as: UTF8.self))
