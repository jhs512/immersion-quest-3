use molip_quest::runner::{run_python, Artifact};

#[tokio::test]
async fn plain_python_stdout_is_unchanged() {
    let result = run_python("print('통과')", "").await.unwrap();
    assert!(result.success, "{}", result.stderr);
    assert_eq!(result.stdout, "통과\n");
    assert!(result.artifacts.is_empty());
}

#[tokio::test]
async fn dataframe_and_seaborn_chart_are_returned_as_separate_outputs() {
    let result = run_python("import pandas as pd\nimport seaborn as sns\nimport matplotlib.pyplot as plt\ndf=pd.DataFrame({'상품':['빵','커피'],'수량':[3,5]})\nsns.barplot(data=df,x='상품',y='수량')\nplt.show()\ndf\n", "").await.unwrap();
    assert!(result.success, "{}", result.stderr);
    assert!(result.stdout.is_empty());
    let table = result
        .artifacts
        .iter()
        .find_map(|a| match a {
            Artifact::Table {
                columns,
                rows,
                total_rows,
                ..
            } => Some((columns, rows, *total_rows)),
            _ => None,
        })
        .expect("DataFrame preview");
    assert_eq!(table.0, &["인덱스", "상품", "수량"]);
    assert_eq!(table.1[0], ["0", "빵", "3"]);
    assert_eq!(table.2, 2);
    assert_eq!(
        result
            .artifacts
            .iter()
            .filter(|a| matches!(a, Artifact::Image { .. }))
            .count(),
        1
    );
    assert!(result.artifacts.iter().any(|a| matches!(a, Artifact::Image { data_url, .. } if data_url.starts_with("data:image/png;base64,iVBOR"))));
}

#[tokio::test]
async fn large_tables_are_limited_and_report_original_size() {
    let result = run_python(
        "import pandas as pd\ndf=pd.DataFrame({'value':range(150)})\ndf",
        "",
    )
    .await
    .unwrap();
    assert!(result.success, "{}", result.stderr);
    assert!(
        matches!(&result.artifacts[0], Artifact::Table { rows, total_rows:150, .. } if rows.len()==100)
    );
}

#[tokio::test]
async fn runtime_errors_are_not_reported_as_success() {
    let result = run_python("print('before')\nraise ValueError('broken')", "")
        .await
        .unwrap();
    assert!(!result.success);
    assert_eq!(result.state, "runtime_error");
    assert!(result.stderr.contains("ValueError: broken"));
}
