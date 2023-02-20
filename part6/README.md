# 5주차_API Serving
<img width="721" alt="스크린샷 2023-02-20 오전 11 25 20" src="https://user-images.githubusercontent.com/92080209/219995408-f2da53ab-ca10-4fea-807b-9af4a246a175.png">


# 1. Model API

## 환경설정

- part2-model development, part3-mlflow server, part5-FastAPI의 docker compose를 열어두고 시작.
<img width="1301" alt="스크린샷 2023-02-17 오후 5 02 11" src="https://user-images.githubusercontent.com/92080209/219995435-780554c2-4b08-4ede-ae1e-f5ee4940ca1e.png">

- db확인
<img width="586" alt="스크린샷 2023-02-17 오후 5 49 21" src="https://user-images.githubusercontent.com/92080209/219996391-7d45f16d-433f-4c48-92bc-885075ee16aa.png">


- 패키지 설치

`$ pip install boto3==1.26.8 mlflow==1.30.0 "fastapi[all]" pandas scikit-learn`

## 모델 다운로드

```python
# download_model.py
import os
from argparse import ArgumentParser

import mlflow

# Set environments
# Model Registry 에 저장되어 있는 모델을 다운로드하기 위해 MLflow 서버와 MinIO 서버에 접속하기 위한 정보를 환경 변수로 설정
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5001"
os.environ["AWS_ACCESS_KEY_ID"] = "minio"
os.environ["AWS_SECRET_ACCESS_KEY"] = "miniostorage"

# mlflow 패키지를 사용하여 model artifact를 다운로드 함.
def download_model(args):
    # Download model artifacts
    mlflow.artifacts.download_artifacts(artifact_uri=f"runs:/{args.run_id}/{args.model_name}", dst_path=".")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--model-name", dest="model_name", type=str, default="sk_model")
    parser.add_argument("--run-id", dest="run_id", type=str)
    args = parser.parse_args()

    download_model(args)
```

- mlflow 패키지를 통해 model artifact를 다운로드함.
model artifact: MLflow에 모델이 저장될 때 함께 저장된 메타데이터와 모델 자체의 binary파일.
- “download_model.py” 스크립트를 실행하여 모델을 local 에 다운로드함.

<img width="1458" alt="스크린샷 2023-02-17 오후 5 53 44" src="https://user-images.githubusercontent.com/92080209/219996474-23fe1e03-df0d-4d4d-bb24-111645163ee7.png">


`$ python download_model.py --model-name sk_model --run-id <run-id>`

스크립트 실행 후 디렉토리 안에 “sk_model” 디렉토리가 생성됨

<img width="872" alt="스크린샷 2023-02-17 오후 5 56 21" src="https://user-images.githubusercontent.com/92080209/219996524-79420ce3-37ba-4287-af2f-e6fb720665b3.png">


## Pydantic Model로 스키마의 클래스 작성

```python
# schemas.py
from pydantic import BaseModel

# breast cancer data type에 맞게 작성
class PredictIn(BaseModel):
    mean_radius: float
    mean_texture: float
    mean_perimeter: float
    mean_area: float
    mean_smoothness: float
    mean_compactness: float
    mean_concavity: float
    mean_concave_points: float
    mean_symmetry: float
    mean_fractal_dimension: float
    radius_error: float
    texture_error: float
    perimeter_error: float
    area_error: float
    smoothness_error: float
    compactness_error: float
    concavity_error: float
    concave_points_error: float
    symmetry_error: float
    fractal_dimension_error: float
    worst_radius: float
    worst_texture: float
    worst_perimeter: float
    worst_area: float
    worst_smoothness: float
    worst_compactness: float
    worst_concavity: float
    worst_concave_points: float
    worst_symmetry: float
    worst_fractal_dimension: float

# 반환되는 값(target)을 int 타입으로 작성
class PredictOut(BaseModel):
    target: int
```

## app.py

```python
# app.py
import mlflow
import pandas as pd
from fastapi import FastAPI
from schemas import PredictIn, PredictOut

def get_model():
    model = mlflow.sklearn.load_model(model_uri="./sk_model")
    return model

MODEL = get_model()

# Create a FastAPI instance
app = FastAPI()

@app.post("/predict", response_model=PredictOut)
def predict(data: PredictIn) -> PredictOut:
    df = pd.DataFrame([data.dict()])
    pred = MODEL.predict(df).item()
    # target
    return PredictOut(target=pred)
```

## API 작동 확인

`$ uvicorn app:app --reload`

<img width="1149" alt="스크린샷 2023-02-17 오후 5 57 20" src="https://user-images.githubusercontent.com/92080209/219996607-db3a38b1-2281-4d2f-bdd3-7bd6a79935a9.png">

<img width="715" alt="스크린샷 2023-02-17 오후 5 57 45" src="https://user-images.githubusercontent.com/92080209/219996620-be8f51a6-7292-4f06-9b70-ff823a31ddf7.png">

<img width="1424" alt="스크린샷 2023-02-17 오후 5 59 27" src="https://user-images.githubusercontent.com/92080209/219996628-a9aa2792-89f1-49bd-87b4-a01dde0362f0.png">


- Request Body 의 형태에 알맞게 데이터를 전달하면 Response Body 로 inference 결과가 반환됨.
- 첫 번재 열 데이터 입력 → 결과 target: 1

# 2. Model API on docker Compose

- FastAPI 의 Swagger UI 를 이용하지 않고  `curl` 을 이용하여 API 가 잘 작동하는지 확인할 수 있음.

<img width="1512" alt="스크린샷 2023-02-17 오후 6 43 23" src="https://user-images.githubusercontent.com/92080209/219996764-38e767b9-2ec7-4ff3-a86e-593159a95937.png">





