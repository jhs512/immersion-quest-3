//! Creator-authored changes. Applying an update never adds a history entry.
use serde::{Deserialize, Serialize};
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq)]
pub struct ChangeEntry {
    pub at: String,
    pub summary: String,
    pub reason: String,
    #[serde(default)]
    pub details: Vec<String>,
}
#[derive(Clone, Debug, PartialEq)]
pub struct HistoryRow {
    pub origin: String,
    pub entry: ChangeEntry,
}
impl ChangeEntry {
    pub fn validate(&self) -> Result<(), String> {
        if !utc_timestamp(&self.at)
            || !short_line(&self.summary, 240)
            || !short_line(&self.reason, 400)
            || self.details.len() > 50
            || self
                .details
                .iter()
                .any(|detail| detail.trim().is_empty() || detail.len() > 8000)
        {
            return Err("변경 시간·요약·이유·세부 내용을 확인하세요.".into());
        }
        Ok(())
    }
}
fn short_line(value: &str, maximum: usize) -> bool {
    !value.trim().is_empty() && value.len() <= maximum && !value.contains(['\n', '\r'])
}
fn utc_timestamp(value: &str) -> bool {
    let b = value.as_bytes();
    if b.len() != 20
        || b[4] != b'-'
        || b[7] != b'-'
        || b[10] != b'T'
        || b[13] != b':'
        || b[16] != b':'
        || b[19] != b'Z'
        || b.iter()
            .enumerate()
            .any(|(i, c)| ![4, 7, 10, 13, 16, 19].contains(&i) && !c.is_ascii_digit())
    {
        return false;
    }
    let number = |start, end| value[start..end].parse::<u32>().unwrap_or(u32::MAX);
    let year = number(0, 4);
    let month = number(5, 7);
    let day = number(8, 10);
    let days = match month {
        1 | 3 | 5 | 7 | 8 | 10 | 12 => 31,
        4 | 6 | 9 | 11 => 30,
        2 => {
            if year % 4 == 0 && (year % 100 != 0 || year % 400 == 0) {
                29
            } else {
                28
            }
        }
        _ => 0,
    };
    year >= 1
        && day >= 1
        && day <= days
        && number(11, 13) < 24
        && number(14, 16) < 60
        && number(17, 19) < 60
}
pub fn validate(entries: &[ChangeEntry]) -> Result<(), String> {
    if entries.len() > 1000 {
        return Err("변경 이력의 개수를 확인하세요.".into());
    }
    entries.iter().try_for_each(ChangeEntry::validate)
}
