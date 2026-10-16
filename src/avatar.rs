//! Level avatars: 큐, the course mascot, drawn as inline SVG and growing with the student.
//!
//! A level is 5 cleared missions (500 XP). Levels group into eight tiers of four, and each tier
//! is a new form of 큐: an egg, a hatchling, a sprout, an explorer with glasses, a painter, a
//! model trainer, a caped champion, and finally a sage with a crown. Inside a tier the level
//! adds one star under the figure, so every level looks different. Everything is geometric
//! and self-contained: no fonts, no images, no network.

/// Missions per level; the header, the victory card and the galleries all share it.
pub const MISSIONS_PER_LEVEL: usize = 5;
pub const XP_PER_MISSION: usize = 100;
pub const LEVELS_PER_TIER: usize = 4;

pub fn level_for(completed_missions: usize) -> usize {
    completed_missions / MISSIONS_PER_LEVEL + 1
}

/// The highest level a course can reach, so the gallery knows how many figures to show.
pub fn max_level(total_missions: usize) -> usize {
    level_for(total_missions)
}

pub fn tier(level: usize) -> usize {
    ((level.max(1) - 1) / LEVELS_PER_TIER).min(TITLES.len() - 1)
}

const TITLES: [&str; 8] = [
    "데이터 알",
    "갓 깬 분석가",
    "새싹 분석가",
    "표 읽는 탐험가",
    "그래프 화가",
    "모델 조련사",
    "기준을 이기는 자",
    "데이터 현자",
];

pub fn title(level: usize) -> &'static str {
    TITLES[tier(level)]
}

/// Body, outline, highlight, and backdrop colours per tier.
fn palette(tier: usize) -> (&'static str, &'static str, &'static str, &'static str) {
    match tier {
        0 => ("#f6e7c6", "#a88a55", "#fff8ea", "#eef3ee"),
        1 => ("#f8d75c", "#b8901a", "#fff2b8", "#eef3ee"),
        2 => ("#86d49a", "#2f8a4c", "#c9f2d3", "#e8f5ea"),
        3 => ("#62cbc8", "#1f7f80", "#c6f1ef", "#e4f4f3"),
        4 => ("#5fa3ee", "#245f9d", "#c8def7", "#e3eef9"),
        5 => ("#8a86ea", "#4a45a8", "#d6d4f7", "#ebeaf9"),
        6 => ("#bf84ea", "#7a3fb0", "#e8d4f8", "#f1e8f9"),
        _ => ("#f3c94e", "#a67a10", "#fff0b8", "#fbf3dc"),
    }
}

/// The SVG for one level, 120 × 120 units, scalable to any size.
pub fn svg(level: usize) -> String {
    let level = level.max(1);
    let tier = tier(level);
    let stars = (level - 1) % LEVELS_PER_TIER + 1;
    let (body, dark, light, bg) = palette(tier);
    let mut parts = vec![format!(
        r##"<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120" role="img" aria-label="Lv. {level} {title}"><circle cx="60" cy="60" r="57" fill="{bg}"/><circle cx="60" cy="60" r="57" fill="none" stroke="{dark}" stroke-opacity=".25" stroke-width="2"/>"##,
        title = title(level)
    )];
    if tier == 7 {
        // Aura rays behind the sage.
        for i in 0..12 {
            let angle = i as f64 * 30.0;
            parts.push(format!(
                r##"<rect x="58" y="6" width="4" height="16" rx="2" fill="{body}" opacity=".55" transform="rotate({angle} 60 60)"/>"##
            ));
        }
    }
    if tier == 6 {
        // Cape behind the body.
        parts.push(format!(
            r##"<path d="M34 58 L22 104 L60 94 L98 104 L86 58 Z" fill="#d94b5a" stroke="#8e2a36" stroke-width="2" stroke-linejoin="round"/>"##
        ));
    }
    match tier {
        0 => {
            parts.push(format!(
                r##"<path d="M60 26 C44 26 32 46 32 66 C32 86 44 100 60 100 C76 100 88 86 88 66 C88 46 76 26 60 26 Z" fill="{body}" stroke="{dark}" stroke-width="2.5"/><circle cx="48" cy="52" r="4" fill="{dark}" opacity=".18"/><circle cx="72" cy="78" r="5" fill="{dark}" opacity=".18"/><circle cx="68" cy="46" r="3" fill="{dark}" opacity=".18"/><path d="M50 70 q4 4 8 0" fill="none" stroke="{dark}" stroke-width="2.5" stroke-linecap="round"/><path d="M62 70 q4 4 8 0" fill="none" stroke="{dark}" stroke-width="2.5" stroke-linecap="round"/><path d="M56 82 q4 3 8 0" fill="none" stroke="{dark}" stroke-width="2" stroke-linecap="round"/>"##
            ));
            // The egg cracks a little more at every level of the tier.
            let cracks = [
                "M60 30 l4 6 -5 5",
                "M60 30 l4 6 -5 5 6 6",
                "M60 30 l4 6 -5 5 6 6 -4 7",
                "M60 30 l4 6 -5 5 6 6 -4 7 M44 40 l5 4 -3 5",
            ];
            parts.push(format!(
                r##"<path d="{}" fill="none" stroke="{dark}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>"##,
                cracks[stars - 1]
            ));
        }
        1 => {
            parts.push(format!(
                r##"<ellipse cx="60" cy="72" rx="30" ry="27" fill="{body}" stroke="{dark}" stroke-width="2.5"/><path d="M38 60 l6 -10 6 10 6 -10 6 10 6 -10 6 10 6 -10 6 10" fill="{light}" stroke="{dark}" stroke-width="2" stroke-linejoin="round"/><path d="M38 60 C38 44 48 34 60 34 C72 34 82 44 82 60 Z" fill="#f6e7c6" stroke="{dark}" stroke-width="2.5"/><circle cx="50" cy="70" r="3.4" fill="#2b2b2b"/><circle cx="70" cy="70" r="3.4" fill="#2b2b2b"/><path d="M55 78 l5 5 5 -5 Z" fill="#f08a2e" stroke="#b25f12" stroke-width="1.5" stroke-linejoin="round"/><path d="M50 99 l-4 7 M50 99 l4 7 M70 99 l-4 7 M70 99 l4 7" stroke="#e0862a" stroke-width="2.5" stroke-linecap="round"/>"##
            ));
        }
        _ => {
            // 큐: a round body with the Q tail, eyes, cheeks and a smile.
            parts.push(format!(
                r##"<circle cx="60" cy="66" r="31" fill="{body}" stroke="{dark}" stroke-width="2.5"/><path d="M80 86 l12 12" stroke="{dark}" stroke-width="9" stroke-linecap="round"/><path d="M80 86 l12 12" stroke="#f2c94c" stroke-width="5" stroke-linecap="round"/><circle cx="49" cy="62" r="6" fill="#fff"/><circle cx="71" cy="62" r="6" fill="#fff"/><circle cx="50" cy="63" r="3.2" fill="#2b2b2b"/><circle cx="72" cy="63" r="3.2" fill="#2b2b2b"/><circle cx="43" cy="73" r="3.5" fill="#f28c8c" opacity=".7"/><circle cx="77" cy="73" r="3.5" fill="#f28c8c" opacity=".7"/><path d="M52 77 q8 7 16 0" fill="none" stroke="{dark}" stroke-width="2.5" stroke-linecap="round"/>"##
            ));
        }
    }
    match tier {
        2 => parts.push(format!(
            r##"<path d="M60 36 v-12" stroke="#2f8a4c" stroke-width="3" stroke-linecap="round"/><path d="M60 28 C52 28 48 22 47 16 C54 16 60 20 60 28 Z" fill="#5fc46f" stroke="#2f8a4c" stroke-width="2"/><path d="M60 24 C68 24 72 18 73 12 C66 12 60 16 60 24 Z" fill="#7bd98a" stroke="#2f8a4c" stroke-width="2"/>"##
        )),
        3 => parts.push(format!(
            r##"<circle cx="49" cy="62" r="9.5" fill="none" stroke="{dark}" stroke-width="2.5"/><circle cx="71" cy="62" r="9.5" fill="none" stroke="{dark}" stroke-width="2.5"/><path d="M58.5 62 h3" stroke="{dark}" stroke-width="2.5"/><path d="M30 46 h60 l-6 -14 h-48 Z" fill="#c8a062" stroke="#7a5a24" stroke-width="2" stroke-linejoin="round"/><rect x="36" y="32" width="48" height="4" fill="#7a5a24" opacity=".35"/>"##
        )),
        4 => parts.push(format!(
            r##"<ellipse cx="56" cy="34" rx="24" ry="9" fill="#d94b5a" stroke="#8e2a36" stroke-width="2"/><ellipse cx="60" cy="30" rx="16" ry="7" fill="#e85d6c"/><circle cx="60" cy="24" r="3" fill="#8e2a36"/><path d="M90 40 l8 -18" stroke="#8c6b3f" stroke-width="3" stroke-linecap="round"/><path d="M98 22 l4 -7 3 8 Z" fill="#5fa3ee" stroke="#245f9d" stroke-width="1.5"/><ellipse cx="30" cy="86" rx="11" ry="8" fill="#fff6e0" stroke="#8c6b3f" stroke-width="2"/><circle cx="25" cy="84" r="2.2" fill="#d94b5a"/><circle cx="31" cy="81" r="2.2" fill="#2f8a4c"/><circle cx="36" cy="85" r="2.2" fill="#f2c94c"/>"##
        )),
        5 => parts.push(format!(
            r##"<path d="M30 42 C34 24 86 24 90 42 Z" fill="#2f5fa5" stroke="#1d3f70" stroke-width="2"/><path d="M28 42 h64 v6 h-64 Z" fill="#1d3f70"/><path d="M60 28 l2.5 5.5 6 .5 -4.5 4 1.5 6 -5.5 -3.2 -5.5 3.2 1.5 -6 -4.5 -4 6 -.5 Z" fill="#f2c94c"/><path d="M44 84 C50 94 70 94 76 84" fill="none" stroke="#1d3f70" stroke-width="2"/><rect x="55" y="88" width="12" height="7" rx="3" fill="#f2c94c" stroke="#a67a10" stroke-width="1.5"/><circle cx="66" cy="91.5" r="2.5" fill="#f2c94c" stroke="#a67a10" stroke-width="1.5"/>"##
        )),
        6 => parts.push(format!(
            r##"<path d="M31 50 C38 38 82 38 89 50" fill="none" stroke="#f2c94c" stroke-width="6" stroke-linecap="round"/><path d="M31 50 C38 38 82 38 89 50" fill="none" stroke="#a67a10" stroke-width="1.5" stroke-linecap="round" opacity=".5"/><path d="M60 36 l2.5 5.5 6 .5 -4.5 4 1.5 6 -5.5 -3.2 -5.5 3.2 1.5 -6 -4.5 -4 6 -.5 Z" fill="#fff" stroke="#a67a10" stroke-width="1"/><circle cx="60" cy="90" r="6.5" fill="#f2c94c" stroke="#a67a10" stroke-width="2"/><path d="M58 80 h4 v5 h-4 Z" fill="#d94b5a"/>"##
        )),
        7 => parts.push(format!(
            r##"<path d="M40 38 l6 -14 8 10 6 -16 6 16 8 -10 6 14 Z" fill="#f2c94c" stroke="#a67a10" stroke-width="2" stroke-linejoin="round"/><circle cx="46" cy="24" r="2.4" fill="#d94b5a"/><circle cx="60" cy="18" r="2.4" fill="#5fa3ee"/><circle cx="74" cy="24" r="2.4" fill="#2f8a4c"/><path d="M22 70 l2 -5 2 5 5 2 -5 2 -2 5 -2 -5 -5 -2 Z" fill="#fff"/><path d="M98 54 l1.5 -4 1.5 4 4 1.5 -4 1.5 -1.5 4 -1.5 -4 -4 -1.5 Z" fill="#fff"/>"##
        )),
        _ => {}
    }
    // Stars under the figure: one more for every level inside the tier.
    let width = stars as f64 * 12.0;
    for i in 0..stars {
        let cx = 60.0 - width / 2.0 + 6.0 + i as f64 * 12.0;
        parts.push(format!(
            r##"<path transform="translate({cx} 108)" d="M0 -5 l1.5 3.3 3.6 .4 -2.7 2.4 .8 3.5 -3.2 -1.9 -3.2 1.9 .8 -3.5 -2.7 -2.4 3.6 -.4 Z" fill="#f2c94c" stroke="#a67a10" stroke-width="1"/>"##
        ));
    }
    parts.push("</svg>".into());
    parts.concat()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn levels_follow_five_missions_each() {
        assert_eq!(level_for(0), 1);
        assert_eq!(level_for(4), 1);
        assert_eq!(level_for(5), 2);
        assert_eq!(max_level(159), 32);
        assert_eq!(tier(1), 0);
        assert_eq!(tier(4), 0);
        assert_eq!(tier(5), 1);
        assert_eq!(tier(32), 7);
        assert_eq!(tier(99), 7);
        assert_eq!(title(1), "데이터 알");
        assert_eq!(title(29), "데이터 현자");
    }

    /// `MOLIP_AVATAR_SHEET=<file.html> cargo test avatar` writes a contact sheet to look at.
    #[test]
    fn contact_sheet_on_request() {
        let Ok(path) = std::env::var("MOLIP_AVATAR_SHEET") else { return };
        let cells: String = (1..=32)
            .map(|level| format!("<figure><div>{}</div><figcaption>Lv. {level} · {}</figcaption></figure>", svg(level), title(level)))
            .collect();
        std::fs::write(path, format!("<!doctype html><meta charset=utf-8><style>body{{background:#17303a;color:#eee;font-family:sans-serif}}main{{display:grid;grid-template-columns:repeat(8,1fr);gap:14px;padding:16px}}figure{{margin:0;text-align:center}}figure div{{width:120px;height:120px;margin:0 auto}}svg{{width:100%;height:100%}}figcaption{{font-size:12px;margin-top:4px}}</style><main>{cells}</main>")).unwrap();
    }

    #[test]
    fn every_level_draws_a_distinct_figure() {
        let drawings: Vec<String> = (1..=32).map(svg).collect();
        for (i, drawing) in drawings.iter().enumerate() {
            assert!(drawing.starts_with("<svg") && drawing.ends_with("</svg>"), "level {}", i + 1);
            assert!(!drawing.contains("{"), "unfilled placeholder at level {}", i + 1);
            let stars = drawing.matches("translate(").count();
            assert_eq!(stars, i % LEVELS_PER_TIER + 1, "stars at level {}", i + 1);
        }
        let unique: std::collections::HashSet<&String> = drawings.iter().collect();
        assert_eq!(unique.len(), 32);
    }
}
