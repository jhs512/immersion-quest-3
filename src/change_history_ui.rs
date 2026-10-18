use dioxus::prelude::*;
#[component]
pub fn ChangeHistory(repository: String) -> Element {
    let mut open = use_signal(|| false);
    let mut rows = use_signal(Vec::<molip_quest::change_history::HistoryRow>::new);
    let mut error = use_signal(String::new);
    let mut count = use_signal(|| 50usize);
    rsx! {
        button {onclick:move |_|{
            count.set(50);open.set(true);rows.set(vec![]);error.set("변경 이력을 불러오고 있어요.".into());
            let repository=repository.clone();
            spawn(async move {
                let result=molip_quest::github_player::background(move||molip_quest::content_updates::installed_store()?.active(&repository)?.map(|snapshot|snapshot.history()).ok_or_else(||"설치된 코스가 없어요.".into())).await;
                match result {Ok(history)=>{rows.set(history);error.set(String::new());},Err(message)=>error.set(message)}
            });
        },"변경 이력"}
        if open() {section {class:"change-history-panel",role:"region",aria_label:"변경 이력",
            header {h2 {"변경 이력"}button {aria_label:"변경 이력 닫기",onclick:move |_|open.set(false),"닫기"}}
            p {role:"status","{error}"}
            if rows().is_empty()&&error().is_empty() {p {"기록된 변경 이력이 없어요."}}
            ol {for row in rows().into_iter().take(count()) {li {class:"change-entry",
                time {datetime:row.entry.at.clone(),{format!("{} UTC",row.entry.at.trim_end_matches('Z').replace('T'," "))}}
                small {"{row.origin}"}strong {"{row.entry.summary}"}p {"{row.entry.reason}"}
                if !row.entry.details.is_empty(){details {summary {"세부 내용"}for detail in row.entry.details {p {"{detail}"}}}}
            }}}
            if count()<rows().len(){button {onclick:move |_|count+=50,"이전 내역 더 보기"}}
        }}
    }
}
