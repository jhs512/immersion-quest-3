//! App-owned, pinned Java library sets for lessons (`java_libraries`, `docker`).
//! A lesson can only name a set. It can never supply a URL, a version or a hash, so a
//! published lesson cannot make the player download anything this table does not pin.
use std::path::PathBuf;

pub struct Jar { pub file:&'static str, pub url:&'static str, pub sha256:&'static str }

const H2:&[Jar]=&[Jar{file:"h2-2.4.240.jar",
    url:"https://repo.maven.apache.org/maven2/com/h2database/h2/2.4.240/h2-2.4.240.jar",
    sha256:"29b70e427cc1c40cdc376283adbb0cc62853073797bb5fe5761f81fe73d57ce0"}];
const POSTGRESQL_JDBC:&[Jar]=&[Jar{file:"postgresql-42.7.13.jar",
    url:"https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.13/postgresql-42.7.13.jar",
    sha256:"6e0e4cc2d8cae902084f8a2b18728b073a6fd9d1f87c9d8bff8f298c18185b93"}];

pub fn set(name:&str)->Option<&'static [Jar]> {
    match name {"h2"=>Some(H2),"postgresql-jdbc"=>Some(POSTGRESQL_JDBC),_=>None}
}

pub fn validate(names:&[String])->Result<(),String> {
    if names.len()>4 {return Err("라이브러리 묶음 수를 확인하세요.".into())}
    let mut seen=std::collections::HashSet::new();
    for name in names {
        if set(name).is_none()||!seen.insert(name) {return Err(format!("앱이 제공하지 않는 라이브러리 묶음이에요: {name}"))}
    }
    Ok(())
}

/// Download (once, hash-checked) and return the jar paths in a stable order.
pub async fn classpath(names:&[String])->Result<Vec<PathBuf>,String> {
    validate(names)?;
    let mut paths=Vec::new();
    for name in names {
        for jar in set(name).unwrap() {
            paths.push(crate::lesson_runner::dependency(jar.file,jar.url,jar.sha256).await
                .map_err(|e|format!("라이브러리 {}를 준비하지 못했어요. 인터넷 연결을 확인하세요: {e}",jar.file))?);
        }
    }
    Ok(paths)
}

pub fn joined(paths:&[PathBuf])->String {
    let separator=if cfg!(windows){";"}else{":"};
    paths.iter().map(|p|p.to_string_lossy().replace('\\',"/")).collect::<Vec<_>>().join(separator)
}

#[cfg(test)]
mod tests {
    #[test]
    fn only_pinned_sets_are_accepted() {
        assert!(super::validate(&["h2".into(),"postgresql-jdbc".into()]).is_ok());
        assert!(super::validate(&["h2".into(),"h2".into()]).is_err());
        assert!(super::validate(&["https://example.invalid/x.jar".into()]).is_err());
        for name in ["h2","postgresql-jdbc"] {
            for jar in super::set(name).unwrap() {
                assert!(jar.url.starts_with("https://repo.maven.apache.org/maven2/")&&jar.url.ends_with(jar.file));
                assert_eq!(jar.sha256.len(),64);
            }
        }
    }
}

#[cfg(test)]
mod runtime_tests {
    /// Downloads the pinned H2 jar once (hash-checked) and grades a real JDBC program.
    #[tokio::test]
    #[ignore="Needs network for the first download and JDK 25"]
    async fn h2_lesson_runs_on_the_pinned_jar_and_rejects_a_wrong_answer() {
        let task:crate::repository_course::Task=serde_json::from_value(serde_json::json!({
            "id":"stp_h2_probe","title":"H2","goal":"x","language":"java_libraries","libraries":["h2"],
            "starter_code":"","solution":"","tests":[{"input":"우유","expected":"우유"}]})).unwrap();
        let source=r#"import java.sql.*;
class Main { public static void main(String[] args) throws Exception {
    String title=new java.util.Scanner(System.in).nextLine();
    try (Connection c=DriverManager.getConnection("jdbc:h2:mem:t","sa","")) {
        c.createStatement().execute("CREATE TABLE memo(title VARCHAR(20))");
        PreparedStatement insert=c.prepareStatement("INSERT INTO memo VALUES (?)");insert.setString(1,title);insert.executeUpdate();
        ResultSet rows=c.createStatement().executeQuery("SELECT title FROM memo");rows.next();System.out.println(rows.getString(1));
    }
} }"#;
        let report=crate::lesson_runner::check(&task,source).await.unwrap();
        assert!(report.passed,"{}",serde_json::to_string(&report).unwrap());
        assert!(!crate::lesson_runner::check(&task,&source.replace("rows.getString(1)","\"빵\"")).await.unwrap().passed);
        let mut plain=task.clone();plain.language=crate::repository_course::TaskLanguage::Java;plain.libraries.clear();
        let without=crate::lesson_runner::run(&plain,source,"우유").await.unwrap();
        assert!(!without.success,"H2 must come only from the pinned set");
    }
}
