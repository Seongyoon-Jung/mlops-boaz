# 3. Model Registry

# 1. MLflow Setup

![스크린샷 2023-02-05 오후 4.57.02.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/9f68ac43-8d51-485c-9905-06f2a7e0ac0d/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2023-02-05_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_4.57.02.png)

## docker-compse.yaml

### mlflow-backend-store

- image : postgres 이미지 사용
- environment: (환경변수 설정)
    - POSTGRES_USER: DB에 접근하기 위한 비밀번호
    - POSTGRES_PASSWORD: DB에 접근하기 위한 비밀번호
    - POSTGRES_DB:DB 이름 설정
- healthcheck: DB 서버가 잘 띄워졌는지 확인하기 위해 상태 체크

```docker
# docker-compose.yaml
version: "3"

services:
  mlflow-backend-store:
    image: postgres:14.0
    container_name: mlflow-backend-store
    environment:
      POSTGRES_USER: mlflowuser
      POSTGRES_PASSWORD: mlflowpassword
      POSTGRES_DB: mlflowdatabase
    healthcheck:
      test: ["CMD", "pg_isready", "-q", "-U", "mlflowuser", "-d", "mlflowdatabase"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### mlflow-artifact-store

- image: minio/minio 이미지 사용
- port: 호스트와 컨테이너의 포트 설정
    - MinIO API 포트를 9000으로 포트 포워딩
    - MInIO의 Console 포트를 9001으로 포트 포워딩
- environment:
    - MINIO_ROOT_USER: MinIO에 접근하기 위한 사용자 이름
    - MINIO_ROOT_PASSWORD: 비밀번호
- command:
    - MinIO 서버를 실행시키는 명령어 추가
    - `—console-address`를 통해 컨테이너의 9001포트로 MinIO에 접근할 수 있도록 주소를 열어줌.

```docker
version: "3"

services:
	. 
	.
	.
  mlflow-artifact-store:
    image: minio/minio
    container_name: mlflow-artifact-store
    ports:
      - 9000:9000
      - 9001:9001
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: miniostorage
    command: server /data/minio --console-address :9001
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
```

<Artifact Store>

Artifact Store는 mlflow에서 학습된 모델을 저장하는 Model Registry로써 이용하기 위한 스토리지 서버.

→ 아티팩트는 잡이 완료된 후에도 데이터를 유지할 수 있게 해준다. 아티팩트는 워크플로우 실행 중 생산된 파일, 파일의 컬렉션이다. Job 중간에 Artifact를 사용하여 데이터를 통과시킬 수 있으며, 워크 플로우 실행이 끝난 후에도 빌드 혹은 테스트 결과를 보존할 수 있다.

<MinIO- Minimal Object Storage>

MinIO는 AWS S3 SDK와 호환되는 오픈소스 오브젝트 스토리지 서버 제품이다. 오브젝트 스토리지를 사용하고 있기 때문에 파일에 대한 직접적인 수정은 불가능하며, 항상 덮어쓰는 방식이 사용된다. GO로 제작됨.

- MinIO Server: 클라우드 스토리지 서버(오브젝트 스토리지)를 구성할 수 있다.
- MinIO Client: “MinIO Server, AWS S3, GCS” 등에 연결하며  파일 업로드 및 관리 등의 기능을 제공한다.
- MinIO Library: 개발자를 위하여 Go, Java, Python 등 SDK를 제공하는 라이브러리이다.

→ MinIO 서버를 사용하는 이유: MLflow에서는 AWS S3을 저장하기 위한 스토리지로 사용하도록 권장하고 있기 떄문에 MInIO를 사용한다.

### MLflow Server

- depends_on: MLflow가 띄어지기 전에 POSTGRESQL DB 서버와 MinIO 서버를 먼저 띄우도록 한다.
- ports:
    - 5001:5000 포트를 설정한다.
- environment
    - AWS_ACCESS_KEY_ID: AWS S3의 credential 정보, MinIO의 “MINIO_ROOT_USER와 동일
    - AWS_SECRET_ACCESS_KEY: AWS S3의 credential 정보, MINIO_ROOT_PASSWORD와 동일
    - MLFLOW_S3_ENDPOINT_URL:AWS S3의 주소를 설정, MinIO 주소와 같음
- command: MinIO 초기 버켓을 설정하고 MLflow 서버 실행

```docker
version: "3"

services:
	.
	.
	.
  mlflow-server:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: mlflow-server
    depends_on:
      mlflow-backend-store:
        condition: service_healthy
      mlflow-artifact-store:
        condition: service_healthy
    ports:
      - 5001:5000
    environment:
      AWS_ACCESS_KEY_ID: minio
      AWS_SECRET_ACCESS_KEY: miniostorage
      MLFLOW_S3_ENDPOINT_URL: http://mlflow-artifact-store:9000
    command:
      - /bin/sh
      - -c
      - |
        mc config host add mlflowminio http://mlflow-artifact-store:9000 minio miniostorage &&
        mc mb --ignore-existing mlflowminio/mlflow
        mlflow server \
        --backend-store-uri postgresql://mlflowuser:mlflowpassword@mlflow-backend-store/mlflow \
        --default-artifact-root s3://mlflow/ \
        --host 0.0.0.0
```

`$ docker compose up -d` 실행

- 실행 결과 확인
    
    localhost:9001
    
    ![스크린샷 2023-02-05 오후 4.02.25.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/72dadabf-ef86-4598-8e35-364c26c2801b/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2023-02-05_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_4.02.25.png)
    
    localhost:5001
    
    ![스크린샷 2023-02-05 오후 4.04.26.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/6ffa8d3d-9c84-4728-893b-24b7e5f06d64/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2023-02-05_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_4.04.26.png)
    

# 2. Save Model to Registry

패키지 설치

`$ pip install boto3==1.26.8 mlflow==1.30.0 scikit-learn`

```docker
# save_model_to_registry.py
import os
from argparse import ArgumentParser

import mlflow
import pandas as pd
import psycopg2
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# 0. set mlflow environments
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5001"
os.environ["AWS_ACCESS_KEY_ID"] = "minio"
os.environ["AWS_SECRET_ACCESS_KEY"] = "miniostorage"

```

`os.environ["MLFLOW_S3_ENDPOINT_URL"]`  : 모델을 저장할 스토리지 주소
`os.environ["MLFLOW_TRACKING_URI"]`  : 정보를 저장하기 위해 연결한 MLflow 서버 주소
`os.environ["AWS_ACCESS_KEY_ID"]`  : MinIO에 접근하기 위한 아이디
`os.environ["AWS_SECRET_ACCESS_KEY"]`  : MinIO에 접근하기 위한 비밀번호

MLflow는 정보를 저장하기 위해 experiment와 run을 사용함.

- experiment : MLflow 에서 정보를 관리하기 위해 나누는 일종의 directory.
- run : experiment에 저장되는 모델 실험 결과. run에 실제 정보들이 저장되게 되며, experiment/run 의 구조로 저장됨.

→ MLflow 는 정보 저장에 관련된 스크립트를 실행 할 때 명시된 experiment에 run 을 동적으로 생성
이 때, 각각의 run 은 unique 한 해쉬값인 run_id를 부여받게 되며, 이를 이용하여 저장된 후에도 해당 정보에 접근할 수 있음.

```docker
.
.
.
# 3. save model
parser = ArgumentParser()
parser.add_argument("--model-name", dest="model_name", type=str, default="sk_model")
args = parser.parse_args()

# experiment 설정
mlflow.set_experiment("new-exp")

signature = mlflow.models.signature.infer_signature(model_input=X_train, model_output=train_pred)
input_sample = X_train.iloc[:10]

# run을 생성하고 정보 저장.
with mlflow.start_run():
    mlflow.log_metrics({"train_acc": train_acc, "valid_acc": valid_acc})
    mlflow.sklearn.log_model(
        sk_model=model_pipeline,
        artifact_path=args.model_name,
        signature=signature,
        input_example=input_sample,
    )

# 4. save data
df.to_csv("data.csv", index=False
```

`$ python save_model_to_registry.py --model-name "sk_model”`

- 실행 결과
    
    ![스크린샷 2023-02-05 오후 4.24.26.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/c2582a84-b181-43ba-81e7-74b19d11e95b/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2023-02-05_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_4.24.26.png)
    
    모델 저장 결
    
    ![스크린샷 2023-02-05 오후 4.27.59.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/34067a6e-f96e-4931-aaaf-fb4dbdb83724/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2023-02-05_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_4.27.59.png)
    

# 3. Load Model from registry

```docker
# load_model_from_registry.py
import os
from argparse import ArgumentParser

import mlflow
import pandas as pd
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# 0. set mlflow environments
os.environ["MLFLOW_S3_ENDPOINT_URL"] = "http://localhost:9000"
os.environ["MLFLOW_TRACKING_URI"] = "http://localhost:5001"
os.environ["AWS_ACCESS_KEY_ID"] = "minio"
os.environ["AWS_SECRET_ACCESS_KEY"] = "miniostorage"

# 1. load model from mlflow
parser = ArgumentParser()
parser.add_argument("--model-name", dest="model_name", type=str, default="sk_model")
parser.add_argument("--run-id", dest="run_id", type=str)
args = parser.parse_args()

model_pipeline = mlflow.sklearn.load_model(f"runs:/{args.run_id}/{args.model_name}")

```

 `mlflow.sklearn.load_model` 함수를 사용하여 이전에 저장한 모델을 불러옴. 모델을 포함하고 있는 “run_id”와 모델을 저장할 때 설정했던 모델 이름을 받을 수 있도록 외부 변수를 설정.

```docker

. 
.
.
#2. get data
df = pd.read_csv("data.csv")

X = df.drop(["id", "timestamp", "target"], axis="columns")
y = df["target"]
X_train, X_valid, y_train, y_valid = train_test_split(X, y, train_size=0.8, random_state=2022)

# 3. predict results
train_pred = model_pipeline.predict(X_train)
valid_pred = model_pipeline.predict(X_valid)

train_acc = accuracy_score(y_true=y_train, y_pred=train_pred)
valid_acc = accuracy_score(y_true=y_valid, y_pred=valid_pred)

print("Train Accuracy :", train_acc)
print("Valid Accuracy :", valid_acc)
```

`$ python load_model_from_registry.py --model-name "sk_model" --run-id "RUN_ID”`

- 실행 결과
