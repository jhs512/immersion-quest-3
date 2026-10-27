use dioxus::prelude::*;
use molip_quest::{
    docker_lab::{LessonSession, SqlTables},
    repository_course::Task,
};

#[component]
pub fn SqlBrowser(task: Task, revision: u64, paused: bool, explaining: bool) -> Element {
    let session = use_context::<LessonSession>();
    let mut tables = use_signal(SqlTables::default);
    let mut selected = use_signal(String::new);
    let mut loading = use_signal(|| true);
    let mut error = use_signal(String::new);
    let mut refresh = use_signal(|| 0u64);
    let mut generation = use_signal(|| 0u64);
    use_effect(use_reactive(
        (&task, &revision, &paused),
        move |(task, _, paused)| {
            let _ = refresh();
            generation.with_mut(|v| *v += 1);
            if paused {
                return;
            }
            let current = *generation.peek();
            let session = session.clone();
            loading.set(true);
            error.set(String::new());
            spawn(async move {
                let result = session.sql_tables(&task).await;
                if *generation.peek() != current {
                    return;
                }
                match result {
                    Ok(value) => {
                        if !value.tables.iter().any(|t| t.name == *selected.peek()) {
                            selected.set(
                                value
                                    .tables
                                    .first()
                                    .map(|t| t.name.clone())
                                    .unwrap_or_default(),
                            );
                        }
                        tables.set(value);
                    }
                    Err(reason) => error.set(reason),
                }
                loading.set(false);
            });
        },
    ));
    let snapshot = tables();
    let active = snapshot.tables.iter().find(|t| t.name == selected());
    rsx! {
        aside {class:"sql-browser",aria_label:"실습 데이터베이스",aria_busy:loading(),
            header {strong {"실습 DB"} button {r#type:"button",disabled:loading()||paused,onclick:move |_|refresh+=1,"새로고침"}}
            if explaining {p {class:"sql-browser-note","내 실습 DB예요. 해설은 별도 DB에서 실행해요."}}
            if loading() {p {role:"status","테이블을 읽고 있어요."}}
            if !error().is_empty() {p {class:"sql-browser-error",role:"alert","{error}"}}
            if !loading()&&error().is_empty()&&snapshot.tables.is_empty() {p {"아직 테이블이 없어요. 테이블을 만들면 여기에 보여요."}}
            nav {class:"sql-table-list",aria_label:"테이블 목록",
                for table in &snapshot.tables {
                    button {key:"{table.name}",r#type:"button","data-table":table.name.clone(),aria_pressed:table.name==selected(),onclick:{let name=table.name.clone();move |_|selected.set(name.clone())},"{table.name}"}
                }
            }
            if snapshot.limited {p {class:"sql-browser-note","테이블은 20개까지 보여요."}}
            if let Some(table)=active {
                section {class:"sql-schema",aria_label:"테이블 구조",
                    h3 {"{table.name} · 구조"}
                    div {class:"sql-grid-scroll",table {
                        thead {tr {th {scope:"col","컬럼"}th {scope:"col","자료형"}th {scope:"col","조건"}}}
                        tbody {for column in &table.columns {tr {key:"{column.name}",
                            th {scope:"row",code {"{column.name}"}}
                            td {code {"{column.data_type}"}}
                            td {span {if column.nullable{"NULL 허용"}else{"NOT NULL"}}if !column.rules.is_empty(){small {"{column.rules}"}}}
                        }}}
                    }}
                }
                section {class:"sql-table-data",aria_label:"테이블 데이터",
                    h3 {"현재 데이터"}
                    div {class:"sql-grid-scroll",table {
                        thead {tr {for column in &table.columns {th {scope:"col","{column.name}"}}}}
                        tbody {for (index,row) in table.rows.iter().enumerate(){tr {key:"{index}",for cell in row {td {
                            if let Some(value)=cell {if value.is_empty(){span {class:"sql-empty",title:"빈 문자열","\"\""}}else{"{value}"}}
                            else {span {class:"sql-null","NULL"}}
                        }}}}}
                    }}
                    if table.rows.is_empty(){p {"저장된 행이 없어요."}}
                    if table.limited{p {class:"sql-browser-note","일부 열·행만 보여요. 긴 값은 128자까지예요."}}
                }
            }
        }
    }
}
