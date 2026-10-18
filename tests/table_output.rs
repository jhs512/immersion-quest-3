use molip_quest::runner::{run_python,Artifact};

#[tokio::test]
async fn previews_follow_printed_selections_instead_of_unprinted_whole_table() {
    let result=run_python("import pandas as pd\ndf=pd.DataFrame({'id':[101,102,103,104],'minutes':[12,18,30,42]})\nprint(df.head(2))\nprint(df[['minutes']])\nwith open('private.txt','w',encoding='utf-8') as output:\n    print(df,file=output)\nprint(df.shape)\n","").await.unwrap();
    assert!(result.success,"{}",result.stderr);
    assert!(result.stdout.ends_with("(4, 2)\n"),"Printing keeps ordinary stdout");
    let tables:Vec<_>=result.artifacts.iter().filter_map(|artifact|match artifact {
        Artifact::Table{columns,total_rows,..}=>Some((columns.clone(),*total_rows)),_=>None
    }).collect();
    assert_eq!(tables,vec![(vec!["인덱스".to_owned(),"id".into(),"minutes".into()],2),(vec!["인덱스".to_owned(),"minutes".into()],4)]);
}

#[tokio::test]
async fn redirected_stdout_does_not_publish_a_hidden_table_as_a_visible_result() {
    let result=run_python("import pandas as pd\nfrom contextlib import redirect_stdout\ndf=pd.DataFrame({'value':[1,2]})\nwith open('hidden.txt','w') as output, redirect_stdout(output):\n    print(df.head(1))\n","").await.unwrap();
    assert!(result.success,"{}",result.stderr);
    assert!(result.stdout.is_empty());
    assert!(result.artifacts.is_empty(),"A redirected print is not visible table output");
}
