from _python_final import make

START = '''import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LinearRegression
# 제공된 두 파일을 읽어요. 주문번호는 예측 뒤 원래 배송과 연결할 때 써요.
train_rows = pd.read_csv("delivery.csv").to_dict(orient="list")
new_rows = pd.read_csv("new.csv").to_dict(orient="list")
train = pd.DataFrame(train_rows)
new = pd.DataFrame(new_rows)
preprocess = ColumnTransformer([
    ("num",Pipeline([("fill",SimpleImputer()),("scale",StandardScaler())]),["distance"]),
    ("cat",OneHotEncoder(handle_unknown="error",sparse_output=False),["zone"])])
pipeline = Pipeline([("prep",preprocess),("model",LinearRegression())])
pipeline.fit(train[["distance","zone"]],train["minutes"])
predictions = pipeline.predict(new[["distance","zone"]])
result = pd.DataFrame({"id":range(len(new)),"minutes":predictions.round(6)})
print(result.to_csv(index=False,lineterminator="\\n").strip())
'''
SPEC = make('aice-integration', '처음 보는 지역도 예측하고 주문번호와 함께 내보내세요',
    'delivery.csv로 전처리와 회귀를 함께 학습해요. new.csv에는 처음 보는 지역도 있어요. '
    '그 지역의 표시 열은 0으로 두고 실행을 이어가요. 결과 CSV의 id는 새 배송의 원래 id를 보존해야 해요. '
    '번호를 새로 0부터 만들지 마세요. 다른 배송 파일로도 검사해요.',
    '훈련 기준의 전처리·추론과 원래 주문번호를 지킨 결과 CSV를 연결해요.', START,
    [('handle_unknown="error"','handle_unknown="ignore"','처음 보는 지역도 변환을 이어가도록 범주 처리 정책을 고치세요.'),
     ('"id":range(len(new))','"id":new["id"]','예측 결과를 새 배송의 원래 주문번호와 연결하세요.')],
    'id,minutes\n501,30.0\n502,35.0',
    [dict(values=dict(new_rows={'id':[10,11],'distance':[4,5],'zone':['b','a']}),expected='id,minutes\n10,50.0\n11,50.0'),
     dict(values=dict(new_rows={'id':[900],'distance':[None],'zone':['a']}),expected='id,minutes\n900,15.0')],
    [([['"id":new["id"]','"id":range(len(new))']], 'Predictions retain original order identifiers'),
     ([['handle_unknown="ignore"','handle_unknown="error"']], 'A new category must not abort inference')],
    [([['"id":new["id"]','"id":new["id"].to_numpy()']], 'An equivalent ordered identifier array')],
    '새 지역 c가 훈련에 없어 변환을 중단했어요.',
    '새 지역도 예측했지만 결과의 주문번호가 0, 1로 바뀌었어요.',
    '예측을 원래 주문 501, 502와 연결한 CSV가 나왔어요.',
    '조심하세요. 결과에 새 번호를 붙이면 어느 주문의 예측인지 원래 파일과 연결하기 어려워요.',
    probe='assert result["id"].tolist() == new["id"].tolist()\nassert pipeline.named_steps["prep"].named_transformers_["cat"].categories_[0].tolist() == sorted(train["zone"].unique())',
    first_error='ValueError', baseline_values={'new_rows': {'id': [501, 502], 'distance': [3, 3], 'zone': ['a', 'c']}})
SPEC['task']['files'] = {
    'delivery.csv':'id,distance,zone,minutes\n1,1,a,10\n2,2,a,20\n3,1,b,20\n4,2,b,30\n',
    'new.csv':'id,distance,zone\n501,3,a\n502,3,c\n'}
