//! Small on-this-computer preferences: whether reward effects animate and make sound, and the
//! screen theme. Saved as JSON next to the progress database; the page scripts
//! (assets/layout/victory.js, assets/layout/theme.js) are told the values at start and on change.
//!
//! The theme has one authority: the stored choice here (시스템 / 밝게 / 어둡게). The effective
//! light or dark look is derived from it in the page, where 시스템 follows the OS setting live.

use serde::{Deserialize, Serialize};

fn default_true() -> bool {
    true
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq)]
pub struct Prefs {
    /// Fireworks, avatar swaps, floating XP: the motion parts of a reward.
    #[serde(default = "default_true")]
    pub animations: bool,
    /// The XP chime and the level-up fanfare.
    #[serde(default = "default_true")]
    pub sounds: bool,
    /// The screen theme the learner chose. Missing (files written before themes existed) or
    /// unreadable values mean 시스템, so nobody is moved off their OS setting by surprise.
    #[serde(default, deserialize_with = "ThemeChoice::tolerant")]
    pub theme: ThemeChoice,
}

#[derive(Clone, Copy, Debug, Default, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum ThemeChoice {
    #[default]
    System,
    Light,
    Dark,
}

impl ThemeChoice {
    pub const ALL: [ThemeChoice; 3] = [ThemeChoice::System, ThemeChoice::Light, ThemeChoice::Dark];
    pub fn parse(value: &str) -> Self {
        match value {
            "light" => Self::Light,
            "dark" => Self::Dark,
            _ => Self::System,
        }
    }
    pub fn key(self) -> &'static str {
        match self {
            Self::System => "system",
            Self::Light => "light",
            Self::Dark => "dark",
        }
    }
    pub fn label(self) -> &'static str {
        match self {
            Self::System => "시스템",
            Self::Light => "밝게",
            Self::Dark => "어둡게",
        }
    }
    fn tolerant<'de, D: serde::Deserializer<'de>>(deserializer: D) -> Result<Self, D::Error> {
        let value = serde_json::Value::deserialize(deserializer)?;
        Ok(value.as_str().map(Self::parse).unwrap_or_default())
    }
    /// Markup for the page head, applied before the first paint: the choice on `<html>` and the
    /// ground colour, so the window does not flash the other theme while the app mounts.
    pub fn boot_head(self) -> String {
        format!(
            "<script>document.documentElement.dataset.themeChoice={:?};</script><style>html{{background:#eef1f5;color-scheme:light}}html[data-theme-choice=dark]{{background:#161f2e;color-scheme:dark}}@media (prefers-color-scheme:dark){{html[data-theme-choice=system]{{background:#161f2e;color-scheme:dark}}}}</style>",
            self.key()
        )
    }
    /// The WebView's own background before any page exists. Only an explicit choice is known
    /// here; 시스템 is resolved by the page head a moment later.
    pub fn window_background(self) -> Option<(u8, u8, u8, u8)> {
        match self {
            Self::Light => Some((0xee, 0xf1, 0xf5, 0xff)),
            Self::Dark => Some((0x16, 0x1f, 0x2e, 0xff)),
            Self::System => None,
        }
    }
    /// The JavaScript that applies a choice in the running page.
    pub fn script(self) -> String {
        format!("window.mqTheme&&mqTheme.set({:?});", self.key())
    }
}

impl Default for Prefs {
    fn default() -> Self {
        Prefs {
            animations: true,
            sounds: true,
            theme: ThemeChoice::System,
        }
    }
}

impl Prefs {
    fn path() -> Result<std::path::PathBuf, String> {
        Ok(crate::data_dir()?.join("prefs.json"))
    }

    pub fn load() -> Prefs {
        Self::path()
            .ok()
            .and_then(|path| std::fs::read_to_string(path).ok())
            .and_then(|text| serde_json::from_str(&text).ok())
            .unwrap_or_default()
    }

    pub fn save(&self) -> Result<(), String> {
        let text = serde_json::to_string_pretty(self).map_err(|e| e.to_string())?;
        std::fs::write(Self::path()?, text).map_err(|e| e.to_string())
    }

    /// Change one value and keep the rest of the file as it is on disk.
    pub fn update(change: impl FnOnce(&mut Prefs)) -> Result<Prefs, String> {
        let mut prefs = Self::load();
        change(&mut prefs);
        prefs.save()?;
        Ok(prefs)
    }

    /// The JavaScript that hands these values to the page (`molipFx` in victory.js).
    pub fn script(&self) -> String {
        format!(
            "window.molipFx && molipFx.set({{animations:{},sounds:{}}});",
            self.animations, self.sounds
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn theme_defaults_to_system_and_bad_values_fall_back_to_system() {
        let old: Prefs = serde_json::from_str(r#"{"animations": false, "sounds": true}"#).unwrap();
        assert_eq!(old.theme, ThemeChoice::System, "files from before themes keep the OS look");
        assert!(!old.animations, "other settings survive");
        for (raw, expected) in [(r#""dark""#, ThemeChoice::Dark), (r#""light""#, ThemeChoice::Light), (r#""system""#, ThemeChoice::System),
            (r#""Dark""#, ThemeChoice::System), (r#""sepia""#, ThemeChoice::System), ("3", ThemeChoice::System), ("null", ThemeChoice::System), ("{}", ThemeChoice::System)] {
            let prefs: Prefs = serde_json::from_str(&format!(r#"{{"theme": {raw}}}"#)).unwrap();
            assert_eq!(prefs.theme, expected, "{raw}");
        }
        let saved = serde_json::to_string(&Prefs { theme: ThemeChoice::Dark, ..Prefs::default() }).unwrap();
        assert!(saved.contains(r#""theme":"dark""#));
        assert_eq!(serde_json::from_str::<Prefs>(&saved).unwrap().theme, ThemeChoice::Dark);
    }

    #[test]
    fn boot_head_marks_the_choice_before_paint_and_explicit_choices_set_the_window() {
        assert!(ThemeChoice::Dark.boot_head().contains(r#"themeChoice="dark""#));
        assert!(ThemeChoice::System.boot_head().contains("prefers-color-scheme:dark"));
        assert_eq!(ThemeChoice::System.window_background(), None);
        assert!(ThemeChoice::Dark.window_background().is_some());
        assert_eq!(ThemeChoice::Light.script(), r#"window.mqTheme&&mqTheme.set("light");"#);
    }

    #[test]
    fn missing_fields_default_to_on_and_the_script_carries_both() {
        let prefs: Prefs = serde_json::from_str("{}").unwrap();
        assert!(prefs.animations && prefs.sounds);
        let prefs: Prefs = serde_json::from_str(r#"{"sounds": false}"#).unwrap();
        assert!(prefs.animations && !prefs.sounds);
        assert_eq!(
            prefs.script(),
            "window.molipFx && molipFx.set({animations:true,sounds:false});"
        );
    }
}
