//! Small on-this-computer preferences: whether reward effects animate and make sound. Saved as
//! JSON next to the progress database; the page scripts (assets/layout/victory.js) are told the
//! values at start and whenever the home screen toggles them.

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
}

impl Default for Prefs {
    fn default() -> Self {
        Prefs {
            animations: true,
            sounds: true,
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
