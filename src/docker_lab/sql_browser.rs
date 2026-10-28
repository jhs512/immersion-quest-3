//! Inspect the learner's real database without executing their answer or observer SQL.
use super::*;
use serde_json::Value;

#[derive(Clone, Debug, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct SqlColumn {
    pub name: String,
    pub data_type: String,
    pub nullable: bool,
    pub rules: String,
}
#[derive(Clone, Debug, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct SqlTable {
    pub name: String,
    pub columns: Vec<SqlColumn>,
    pub rows: Vec<Vec<Option<String>>>,
    pub limited: bool,
}
#[derive(Clone, Debug, Default, PartialEq, serde::Serialize, serde::Deserialize)]
pub struct SqlTables {
    pub tables: Vec<SqlTable>,
    pub limited: bool,
}

fn literal(value: &str, mysql: bool) -> String {
    let value = if mysql {
        value.replace('\\', "\\\\")
    } else {
        value.to_owned()
    };
    format!("'{}'", value.replace('\'', "''"))
}
fn identifier(value: &str, mysql: bool) -> String {
    let quote = if mysql { '`' } else { '"' };
    format!(
        "{quote}{}{quote}",
        value.replace(quote, &format!("{quote}{quote}"))
    )
}
fn text(value: &Value, key: &str) -> String {
    value[key].as_str().unwrap_or_default().to_owned()
}

fn query(
    environment: &Environment,
    mysql: bool,
    sql: &str,
    cancel: &std::sync::atomic::AtomicBool,
    read_only: bool,
) -> Result<Vec<Value>, String> {
    let mut command = Command::new(&environment.lab.cli);
    prepare(&mut command, &environment.lab.cli);
    command
        .current_dir(environment.directory.path())
        .env("COMPOSE_PROJECT_NAME", &environment.lab.project)
        .env("PGCLIENTENCODING", "UTF8")
        .args(["compose", "exec", "-T"]);
    if mysql {
        command.args([
            "-e",
            "MYSQL_PWD=lab",
            "db",
            "mysql",
            "-uroot",
            "--default-character-set=utf8mb4",
            "--batch",
            "--raw",
            "--skip-column-names",
            "lab",
        ]);
    } else {
        command.args([
            "db",
            "psql",
            "-U",
            "postgres",
            "-d",
            "lab",
            "-X",
            "-q",
            "-A",
            "-t",
            "-v",
            "ON_ERROR_STOP=1",
        ]);
    }
    let sql = if read_only {
        if mysql {
            format!(
                "SET SESSION MAX_EXECUTION_TIME=3000; START TRANSACTION READ ONLY;\n{sql}\nCOMMIT;"
            )
        } else {
            format!("BEGIN READ ONLY; SET LOCAL statement_timeout='3s';\n{sql}\nCOMMIT;")
        }
    } else {
        sql.to_owned()
    };
    let output = execute_cancellable(command, &sql, 30, Some(cancel))?;
    if !output.success {
        return Err(format!("테이블을 읽지 못했어요. {}", output.stderr.trim()));
    }
    // Setup SQL is trusted lesson content, not JSON output. Never run it on refresh.
    if !read_only {
        return Ok(vec![]);
    }
    output
        .stdout
        .lines()
        .filter(|line| !line.trim().is_empty())
        .map(|line| {
            serde_json::from_str(line).map_err(|_| "테이블 응답을 읽지 못했어요.".to_owned())
        })
        .collect()
}

fn snapshot(
    environment: &Environment,
    mysql: bool,
    cancel: &std::sync::atomic::AtomicBool,
) -> Result<SqlTables, String> {
    let list = if mysql {
        "SELECT JSON_OBJECT('name',TABLE_NAME) FROM information_schema.tables WHERE TABLE_SCHEMA='lab' AND TABLE_TYPE='BASE TABLE' ORDER BY TABLE_NAME LIMIT 21;"
    } else {
        "SELECT json_build_object('name',tablename) FROM pg_catalog.pg_tables WHERE schemaname='public' ORDER BY tablename LIMIT 21;"
    };
    let tables = query(environment, mysql, list, cancel, true)?;
    let mut result = SqlTables {
        limited: tables.len() > 20,
        tables: vec![],
    };
    for item in tables.iter().take(20) {
        let name = text(item, "name");
        let name_literal = literal(&name, mysql);
        let columns = if mysql {
            format!(
                r#"SELECT JSON_OBJECT('name',c.COLUMN_NAME,'data_type',c.COLUMN_TYPE,'nullable',c.IS_NULLABLE,'rules',CONCAT_WS(' ',CASE c.COLUMN_KEY WHEN 'PRI' THEN 'PRIMARY KEY' WHEN 'UNI' THEN 'UNIQUE' ELSE NULL END,(SELECT GROUP_CONCAT(CONCAT('REFERENCES ',k.REFERENCED_TABLE_NAME,'(',k.REFERENCED_COLUMN_NAME,')') SEPARATOR ', ') FROM information_schema.KEY_COLUMN_USAGE k WHERE k.TABLE_SCHEMA='lab' AND k.TABLE_NAME=c.TABLE_NAME AND k.COLUMN_NAME=c.COLUMN_NAME AND k.REFERENCED_TABLE_NAME IS NOT NULL))) FROM information_schema.COLUMNS c WHERE c.TABLE_SCHEMA='lab' AND c.TABLE_NAME={name_literal} ORDER BY c.ORDINAL_POSITION LIMIT 33;"#
            )
        } else {
            format!(
                r#"SELECT json_build_object('name',a.attname,'data_type',format_type(a.atttypid,a.atttypmod),'nullable',CASE WHEN a.attnotnull THEN 'NO' ELSE 'YES' END,'rules',COALESCE((SELECT string_agg(pg_get_constraintdef(k.oid),'; ' ORDER BY k.oid) FROM pg_constraint k WHERE k.conrelid=c.oid AND a.attnum=ANY(k.conkey)),'')) FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='public' AND c.relname={name_literal} AND a.attnum>0 AND NOT a.attisdropped ORDER BY a.attnum LIMIT 33;"#
            )
        };
        let meta = query(environment, mysql, &columns, cancel, true)?;
        let columns: Vec<_> = meta
            .iter()
            .take(32)
            .map(|c| SqlColumn {
                name: text(c, "name"),
                data_type: text(c, "data_type"),
                nullable: text(c, "nullable") == "YES",
                rules: text(c, "rules"),
            })
            .collect();
        let values = columns
            .iter()
            .map(|c| {
                let id = identifier(&c.name, mysql);
                if mysql {
                    format!("LEFT(CAST({id} AS CHAR),128)")
                } else {
                    format!("left({id}::text,128)")
                }
            })
            .collect::<Vec<_>>()
            .join(",");
        let qualified = if mysql {
            format!("lab.{}", identifier(&name, true))
        } else {
            format!("public.{}", identifier(&name, false))
        };
        let row_limit = (40000 / (columns.len().max(1) * 768)).clamp(1, 20);
        let sql = format!(
            "SELECT {}({values}) FROM {qualified} LIMIT {};",
            if mysql {
                "JSON_ARRAY"
            } else {
                "json_build_array"
            },
            row_limit + 1
        );
        let rows = if columns.is_empty() {
            vec![]
        } else {
            query(environment, mysql, &sql, cancel, true)?
        };
        let limited = rows.len() > row_limit
            || meta.len() > 32
            || rows.iter().any(|row| {
                row.as_array().is_some_and(|cells| {
                    cells
                        .iter()
                        .any(|v| v.as_str().is_some_and(|s| s.chars().count() >= 128))
                })
            });
        let rows = rows
            .into_iter()
            .take(row_limit)
            .map(|row| {
                row.as_array()
                    .ok_or_else(|| "테이블의 행 형식을 확인하세요.".to_owned())
                    .map(|cells| {
                        cells
                            .iter()
                            .map(|v| v.as_str().map(str::to_owned))
                            .collect()
                    })
            })
            .collect::<Result<Vec<_>, _>>()?;
        result.tables.push(SqlTable {
            name,
            columns,
            rows,
            limited,
        });
    }
    Ok(result)
}

impl LessonSession {
    pub async fn sql_tables(&self, task: &Task) -> Result<SqlTables, String> {
        let database = sql_fixture(task).ok_or("이 문제에는 SQL 테이블 보기가 없어요.")?;
        self.ensure_open()?;
        let (session, task) = (self.clone(), task.clone());
        tokio::task::spawn_blocking(move || {
            let mut environments = session
                .0
                .environments
                .lock()
                .unwrap_or_else(|e| e.into_inner());
            session.ensure_open()?;
            let key = environment_key(&task, false);
            if !environments.contains_key(&key) {
                let cli = cli().ok_or("Docker를 찾지 못했어요.")?;
                ensure_engine(&cli)?;
                ensure_images(&cli, &task.docker_images)?;
                session.ensure_open()?;
                let directory = tempfile::Builder::new()
                    .prefix("mq3-docker-lesson-")
                    .tempdir()
                    .map_err(|e| e.to_string())?;
                let lab = Lab::open(&cli, &task)?;
                environments.insert(
                    key.clone(),
                    Environment {
                        lab,
                        directory,
                        fixture: None,
                    },
                );
            }
            let environment = environments.get_mut(&key).unwrap();
            let fixture =
                serde_json::to_string(&(&task.id, &task.files)).map_err(|e| e.to_string())?;
            if environment.fixture.as_ref() != Some(&fixture) {
                for (name, content) in &task.files {
                    write(environment.directory.path(), name, content)?;
                }
                if let Some(problem) = compose_problem(
                    &environment.lab.cli,
                    environment.directory.path(),
                    &environment.lab.project,
                    &task.docker_images,
                )? {
                    return Err(problem);
                }
                if let Some(problem) = dockerfile_problem(environment.directory.path(), &task.docker_images) {
                    return Err(problem);
                }
                reset_sql_fixture(environment, database, &session.0.closed)?;
                query(
                    environment,
                    database == "mysql",
                    &task.files["before.sql"],
                    &session.0.closed,
                    false,
                )?;
                environment.fixture = Some(fixture);
            }
            let result = snapshot(environment, database == "mysql", &session.0.closed)?;
            session.ensure_open()?;
            Ok(result)
        })
        .await
        .map_err(|e| e.to_string())?
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn identifiers_and_values_are_quoted_separately() {
        assert_eq!(identifier("odd`table", true), "`odd``table`");
        assert_eq!(identifier("odd\"table", false), "\"odd\"\"table\"");
        assert_eq!(literal("O'Brien", true), "'O''Brien'");
        assert_eq!(literal("a\\b", false), "'a\\b'");
    }

    #[tokio::test]
    #[ignore = "Needs Docker and the course MySQL/PostgreSQL images"]
    async fn real_metadata_refresh_is_read_only_and_keeps_learner_state() {
        for source in [
            include_str!("../../courses/redesigned/sql-first.json"),
            include_str!("../../courses/redesigned/sql-index-plan.json"),
        ] {
            let lesson: Value = serde_json::from_str(source).unwrap();
            let mut task: Task = serde_json::from_value(lesson["tasks"][0].clone()).unwrap();
            task.files.insert("before.sql".into(),"CREATE TABLE parent(id INT PRIMARY KEY); INSERT INTO parent VALUES(1); CREATE TABLE child(id INT PRIMARY KEY, parent_id INT REFERENCES parent(id), name VARCHAR(100), price INT NOT NULL); INSERT INTO child VALUES(1,1,NULL,100),(2,1,'',200),(3,1,'한글',300); CREATE TABLE empty_table(id INT);".into());
            // Both are destructive if accidentally executed while opening the browser.
            task.starter_code = "DROP TABLE child;".into();
            task.files
                .insert("after.sql".into(), "DELETE FROM child WHERE id=3;".into());
            let session = LessonSession::new();
            let first = session.sql_tables(&task).await.unwrap();
            assert_eq!(
                first
                    .tables
                    .iter()
                    .map(|t| t.name.as_str())
                    .collect::<Vec<_>>(),
                ["child", "empty_table", "parent"]
            );
            let child = &first.tables[0];
            assert_eq!(
                child.rows.len(),
                3,
                "the browser must not execute starter or observer SQL"
            );
            assert!(child.columns[0].rules.contains("PRIMARY KEY"));
            assert!(!child.columns[3].nullable);
            assert_eq!(child.rows[0][2], None);
            assert_eq!(child.rows[1][2], Some(String::new()));
            assert_eq!(child.rows[2][2].as_deref(), Some("한글"));
            assert!(first.tables[1].rows.is_empty());
            let result=session.run(&task,"UPDATE child SET price=777 WHERE id=1; CREATE TABLE created_by_learner(id INT);","").await.unwrap();
            assert!(result.success, "{}", result.stderr);
            let changed = session.sql_tables(&task).await.unwrap();
            assert!(changed
                .tables
                .iter()
                .any(|t| t.name == "created_by_learner"));
            assert_eq!(changed.tables[0].rows.len(), 2);
            assert!(changed.tables[0]
                .rows
                .iter()
                .any(|r| r[3].as_deref() == Some("777")));
            assert_eq!(
                changed,
                session.sql_tables(&task).await.unwrap(),
                "refresh must preserve the current DB"
            );
            // A different problem seeds its own prepared tables instead of showing stale rows.
            task.id.push_str("-next");
            assert_eq!(first, session.sql_tables(&task).await.unwrap());
            session.close();
            session.wait_closed().await;
            assert!(session.sql_tables(&task).await.is_err());
        }
    }
}
