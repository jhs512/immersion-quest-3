//! Each SQL execution owns one bounded in-memory database; no database files are opened.
use crate::runner::Execution;
use rusqlite::{Connection, hooks::{AuthAction,AuthContext,Authorization}, limits::Limit};
use std::{collections::BTreeMap,time::{Duration,Instant}};

const OUTPUT_BYTES:usize=65_536;
const RESULT_ROWS:usize=2_000;

pub async fn execute(files:&BTreeMap<String,String>,source:&str)->Result<Execution,String> {
    let files=files.clone();let source=source.to_owned();
    tokio::task::spawn_blocking(move||session(&files,&source)).await.map_err(|e|e.to_string())
}

fn session(files:&BTreeMap<String,String>,source:&str)->Execution {
    let mut output=String::new();
    let result=(||{
        let conn=Connection::open_in_memory().map_err(|e|e.to_string())?;
        // Set resource and integrity policy before learner statements are authorized.
        conn.execute_batch("PRAGMA foreign_keys=ON; PRAGMA temp_store=MEMORY; PRAGMA main.max_page_count=4096; PRAGMA temp.max_page_count=4096;").map_err(|e|e.to_string())?;
        for (limit,value) in [(Limit::SQLITE_LIMIT_LENGTH,1_000_000),(Limit::SQLITE_LIMIT_SQL_LENGTH,200_000),(Limit::SQLITE_LIMIT_COLUMN,100),(Limit::SQLITE_LIMIT_ATTACHED,0),(Limit::SQLITE_LIMIT_EXPR_DEPTH,100)] {conn.set_limit(limit,value);}
        conn.authorizer(Some(|context:AuthContext<'_>|match context.action {
            AuthAction::Attach{..}|AuthAction::Detach{..}|AuthAction::Pragma{..}|AuthAction::Unknown{..}|AuthAction::CreateVtable{..}|AuthAction::DropVtable{..}=>Authorization::Deny,
            AuthAction::Function{function_name} if matches!(function_name.to_ascii_lowercase().as_str(),"load_extension"|"readfile"|"writefile")=>Authorization::Deny,
            _=>Authorization::Allow,
        }));
        let started=Instant::now();let mut ticks=0;
        conn.progress_handler(1000,Some(move||{ticks+=1;ticks>10_000||started.elapsed()>Duration::from_secs(10)}));
        let mut row_count=0;
        if let Some(setup)=files.get("setup.sql"){statements(&conn,setup,"준비 SQL",false,&mut output,&mut row_count)?;}
        statements(&conn,source,"SQL 오류",true,&mut output,&mut row_count)?;
        if let Some(after)=files.get("after.sql"){statements(&conn,after,"확인 SQL",true,&mut output,&mut row_count)?;}
        Ok::<(),String>(())
    })();
    match result {
        Ok(())=>Execution{stdout:output,stderr:String::new(),success:true,state:"finished".into(),artifacts:vec![]},
        Err(error)=>{let interrupted=error.contains("interrupt");Execution{stdout:output,stderr:if interrupted{"실행 한도를 넘었어요. 반복·결합 조건을 확인하세요.".into()}else{error},success:false,state:if interrupted{"timeout"}else{"runtime_error"}.into(),artifacts:vec![]}},
    }
}

fn append(output:&mut String,text:&str)->Result<(),String> {
    if output.len()+text.len()>OUTPUT_BYTES {return Err("결과가 너무 길어요. 조회할 행·열을 줄여 보세요.".into());}
    output.push_str(text);Ok(())
}

fn statements(conn:&Connection,sql:&str,label:&str,show:bool,output:&mut String,row_count:&mut usize)->Result<(),String> {
    let mut batch=rusqlite::Batch::new(conn,sql);
    while let Some(mut statement)=batch.next().map_err(|e|format!("{label}: {e}"))? {
        let columns:Vec<_>=statement.column_names().iter().map(|name|name.to_string()).collect();
        if show&&!columns.is_empty(){if !output.is_empty(){append(output,"\n")?;}append(output,&columns.join(" | "))?;append(output,"\n")?;}
        let mut rows=statement.raw_query();let mut any=false;
        while let Some(row)=rows.next().map_err(|e|format!("{label}: {e}"))? {
            *row_count+=1;if *row_count>RESULT_ROWS {return Err("조회 결과가 너무 많아요. 조건으로 행을 줄여 보세요.".into());}
            any=true;
            if show {
                let mut values=Vec::with_capacity(columns.len());
                for i in 0..columns.len(){values.push(value(row.get_ref(i).map_err(|e|e.to_string())?));}
                append(output,&values.join(" | "))?;append(output,"\n")?;
            }
        }
        if show&&!columns.is_empty()&&!any {append(output,"(행 없음)\n")?;}
    }
    Ok(())
}

fn value(value:rusqlite::types::ValueRef<'_>)->String {
    use rusqlite::types::ValueRef;
    match value {
        ValueRef::Null=>"NULL".into(),ValueRef::Integer(i)=>i.to_string(),
        ValueRef::Real(f)=>if f.fract()==0.0&&f.abs()<1e15 {format!("{f:.1}")}else{f.to_string()},
        ValueRef::Text(text)=>String::from_utf8_lossy(text).into_owned(),ValueRef::Blob(_)=>"<blob>".into(),
    }
}
