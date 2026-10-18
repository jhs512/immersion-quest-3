//! Optional published aids. They do not own answers, completion, or authoring prompts.
use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, HashSet};

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct SupportingMaterial {
    pub id: String,
    pub title: String,
    #[serde(flatten)]
    pub content: MaterialContent,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(tag = "kind", rename_all = "snake_case", deny_unknown_fields)]
pub enum MaterialContent {
    Mermaid { source: String },
    Interactive { variants: Vec<VisualVariant> },
    Image { image: RasterImage },
    Comic { image: RasterImage },
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct RasterImage {
    pub alt: String,
    pub png_base64: String,
    pub sha256: String,
}

impl RasterImage {
    fn validate(&self) -> Result<(), String> {
        use base64::Engine;
        use sha2::{Digest, Sha256};
        if self.alt.trim().is_empty() || self.alt.len() > 4000 || self.png_base64.len() > 2_800_000
        {
            return Err("그림의 설명과 크기를 확인하세요.".into());
        }
        let bytes = base64::engine::general_purpose::STANDARD
            .decode(&self.png_base64)
            .map_err(|_| "PNG 그림 데이터를 확인하세요.")?;
        if bytes.len() < 33
            || &bytes[..8] != b"\x89PNG\r\n\x1a\n"
            || &bytes[12..16] != b"IHDR"
            || format!("{:x}", Sha256::digest(&bytes)) != self.sha256
        {
            return Err("PNG 그림과 고정한 해시가 맞지 않아요.".into());
        }
        let width = u32::from_be_bytes(bytes[16..20].try_into().unwrap());
        let height = u32::from_be_bytes(bytes[20..24].try_into().unwrap());
        if width == 0
            || height == 0
            || width > 4096
            || height > 4096
            || u64::from(width) * u64::from(height) > 8_000_000
        {
            return Err("그림의 가로·세로 크기를 확인하세요.".into());
        }
        let decoder = png::Decoder::new_with_limits(
            std::io::Cursor::new(&bytes),
            png::Limits {
                bytes: 64 * 1024 * 1024,
            },
        );
        let mut reader = decoder
            .read_info()
            .map_err(|_| "PNG 그림을 읽지 못했어요.")?;
        if reader.info().animation_control.is_some() {
            return Err("움직이는 PNG 대신 정지 그림을 넣어 주세요.".into());
        }
        let size = reader
            .output_buffer_size()
            .filter(|size| *size <= 64 * 1024 * 1024)
            .ok_or("PNG 그림이 너무 커요.")?;
        reader
            .next_frame(&mut vec![0; size])
            .map_err(|_| "PNG 그림 내용이 손상됐어요.")?;
        reader
            .finish()
            .map_err(|_| "PNG 그림이 끝까지 저장되지 않았어요.")?;
        Ok(())
    }
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct VisualVariant {
    pub label: String,
    pub frames: Vec<VisualFrame>,
}

#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
#[serde(deny_unknown_fields)]
pub struct VisualFrame {
    pub caption: String,
    pub facts: BTreeMap<String, String>,
}

/// Use only inside an iframe with `sandbox="allow-scripts"` (no same-origin).
pub fn diagram_document(source: &str) -> String {
    let source = script_value(source);
    let vendor = include_str!("../assets/comics/mermaid.min.js").replace("</script", "<\\/script");
    format!(
        r#"<!doctype html><html lang="ko"><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; connect-src 'none'; form-action 'none'; base-uri 'none'">
<style>body{{margin:12px;background:#fff;color:#182838;font:16px sans-serif}}svg{{max-width:100%;height:auto}}pre{{white-space:pre-wrap;overflow-wrap:anywhere}}</style>
<div id="diagram" role="img" aria-label="다이어그램"></div><pre id="fallback"></pre>
<script>{vendor}</script><script>
(async()=>{{const source={source};const fallback=document.getElementById('fallback');
try{{mermaid.initialize({{startOnLoad:false,securityLevel:'strict',maxTextSize:32768}});
const result=await mermaid.render('support-diagram',source);
document.getElementById('diagram').innerHTML=result.svg;
parent.postMessage({{type:'molip-support-render',status:'ready'}},'*');
}}catch(_){{document.getElementById('diagram').textContent='다이어그램을 그리지 못했어요.';fallback.textContent=source;parent.postMessage({{type:'molip-support-render',status:'error'}},'*');}}}})();
</script></html>"#
    )
}

fn script_value(text: &str) -> String {
    serde_json::to_string(text)
        .expect("string JSON")
        .replace('<', "\\u003c")
        .replace('>', "\\u003e")
        .replace('&', "\\u0026")
        .replace('\u{2028}', "\\u2028")
        .replace('\u{2029}', "\\u2029")
}

pub fn validate(materials: &[SupportingMaterial]) -> Result<(), String> {
    let mut ids = HashSet::new();
    if materials.len() > 8 {
        return Err("부가 설명 자료는 8개까지 넣을 수 있어요.".into());
    }
    for material in materials {
        if material.id.is_empty()
            || material.id.len() > 80
            || !material
                .id
                .bytes()
                .all(|c| c.is_ascii_alphanumeric() || b"-_".contains(&c))
            || !ids.insert(&material.id)
            || material.title.trim().is_empty()
            || material.title.len() > 240
        {
            return Err("부가 설명 자료의 이름과 고유 키를 확인하세요.".into());
        }
        match &material.content {
            MaterialContent::Image { image } | MaterialContent::Comic { image } => {
                image.validate()?
            }
            MaterialContent::Mermaid { source }
                if source.trim().is_empty() || source.len() > 32_768 =>
            {
                return Err("다이어그램 원문은 1~32768바이트로 넣어 주세요.".into());
            }
            MaterialContent::Interactive { variants } => {
                if variants.is_empty()
                    || variants.len() > 8
                    || variants.iter().any(|variant| {
                        variant.label.trim().is_empty()
                            || variant.label.len() > 240
                            || variant.frames.is_empty()
                            || variant.frames.len() > 80
                            || variant.frames.iter().any(|frame| {
                                frame.caption.trim().is_empty()
                                    || frame.caption.len() > 2000
                                    || frame.facts.len() > 20
                                    || frame.facts.iter().any(|(key, value)| {
                                        key.trim().is_empty()
                                            || key.len() > 160
                                            || value.len() > 2000
                                    })
                            })
                    })
                {
                    return Err("시각화의 조건과 단계별 상태를 확인하세요.".into());
                }
            }
            _ => {}
        }
    }
    Ok(())
}
