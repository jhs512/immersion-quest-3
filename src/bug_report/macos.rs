use objc2_core_foundation::{CFDictionary, CFNumber, CFString, CFType, CGRect};
use objc2_core_graphics::{
    CGDataProvider, CGImage, CGRectMakeWithDictionaryRepresentation, CGWindowImageOption,
    CGWindowListCopyWindowInfo, CGWindowListCreateImage, CGWindowListOption,
};
use xcap::image::RgbaImage;

type WindowInfo = CFDictionary<CFString, CFType>;

fn number(info: &WindowInfo, key: &str) -> Option<i32> {
    info.get(&CFString::from_str(key))?.downcast::<CFNumber>().ok()?.as_i32()
}

fn window(info: &WindowInfo, parent: u32) -> Option<(u32, CGRect)> {
    if number(info, "kCGWindowOwnerPID")? as u32 != parent { return None; }
    let title = info.get(&CFString::from_str("kCGWindowName"))?.downcast::<CFString>().ok()?;
    if title.to_string() != "MQ" { return None; }
    let id = number(info, "kCGWindowNumber")? as u32;
    let bounds = info.get(&CFString::from_str("kCGWindowBounds"))?.downcast::<CFDictionary>().ok()?;
    let mut rect = CGRect::default();
    if !unsafe { CGRectMakeWithDictionaryRepresentation(Some(&bounds), &mut rect) } { return None; }
    Some((id, rect))
}

pub(super) fn capture(parent: u32) -> Result<RgbaImage, String> {
    if parent != std::process::id() { return Err("MQ can only capture its own window".into()); }
    let windows = CGWindowListCopyWindowInfo(CGWindowListOption::ExcludeDesktopElements, 0)
        .ok_or("MQ window list unavailable")?;
    let mut best: Option<(u32, CGRect)> = None;
    for index in 0..windows.count() {
        // CoreGraphics defines this array as window dictionaries with CFString keys and CFType values.
        let info = unsafe { &*windows.value_at_index(index).cast::<WindowInfo>() };
        if let Some((id, rect)) = window(info, parent) {
            let area = rect.size.width * rect.size.height;
            if area > 0.0 && best.as_ref().is_none_or(|(_, previous)| area > previous.size.width * previous.size.height) {
                best = Some((id, rect));
            }
        }
    }
    let (id, rect) = best.ok_or("MQ window unavailable")?;
    let image = CGWindowListCreateImage(rect, CGWindowListOption::OptionIncludingWindow, id, CGWindowImageOption::Default)
        .ok_or("MQ window image unavailable")?;
    let width = CGImage::width(Some(&image));
    let height = CGImage::height(Some(&image));
    if width == 0 || height == 0 || width.checked_mul(height).is_none_or(|pixels| pixels > 32_000_000) {
        return Err("capture too large or empty".into());
    }
    let provider = CGImage::data_provider(Some(&image)).ok_or("MQ image data unavailable")?;
    let data = CGDataProvider::data(Some(&provider)).ok_or("MQ image bytes unavailable")?;
    let stride = CGImage::bytes_per_row(Some(&image));
    let required = stride.checked_mul(height).ok_or("MQ image layout too large")?;
    if stride < width * 4 || data.len() < required { return Err("MQ image layout unavailable".into()); }
    let mut pixels = Vec::with_capacity(width * height * 4);
    for row in data.to_vec().chunks_exact(stride).take(height) {
        pixels.extend_from_slice(&row[..width * 4]);
    }
    for bgra in pixels.chunks_exact_mut(4) { bgra.swap(0, 2); }
    RgbaImage::from_raw(width as u32, height as u32, pixels).ok_or_else(|| "MQ image decoding failed".into())
}
