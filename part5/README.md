# 4주차_Model Deployment/ FastAPI

# 1. REST API

학습이 완료된 모델을 다른 사람이 사용할 수 있도록 하기 위해서는? 
→ 저장된 모델과 추론에 사용된 코드를 사용자에게 전달하면 됨.

하지만, 로컬에서 모델을 사용할 때, 모델의 크기가 커서, 또는 설치되어 있는 패키지 버전이 달라서 등 다양한 문제가 발생할 수 있음.

이를 해결하기 위해 모델을 실행할 수 있는 환경으로 데이터를 전송하고, 그에 대한 응답을 사용자가 받는 방식의 구조를 사용. 이를 **Request-Respose 방식**이라고 불림.

![스크린샷 2023-02-13 오후 5 19 33](https://user-images.githubusercontent.com/92080209/218406152-ea96b5d3-f4d3-4ed1-b1c6-d00599707105.png)

출처: [https://phpenthusiast.com/blog/what-is-rest-api](https://phpenthusiast.com/blog/what-is-rest-api)

Request-Response를 하기 위해서는 요청과 응답을 어떻게 할 것인가에 대해서 사전에 정의하는 절차가 필요함. 이 절차중 가장 대표적인 방법을 REST API 이다.

## 1.1. RestAPI - Representational State Transfer API

 2000년도 로이 필딩 박사학위 논문에서 최초로 소개됨. 그는 **웹의 장점을 최대한 활용**할 수 있는 아키텍처로써 REST를 발표함.

- 웹 기반 애플리케이션에서 클라이언트와 서버 간의 통신을 위한 아키텍처 중 하나.
- 자원을 이름으로 구분하여 해당 자원의 상태를 주고 받는 모든 것을 의미.
- 클라이언트가 URI(Uniform Resource Identifier)를 통해 서버에 요청을 보내고, 서버는 요청에 대한 응답으로 HTTP 상태 코드와 함께 데이터를 전송함. 이때 데이터는 일반적으로 xml, json 형식으로 표현됨.
    - HTTP URI: 이를 통해 자원(Resource)을 명시함. (URI ⊃ URL)
- REST API는 HTTP 프로토콜을 기반으로 하므로, HTTP 메소드인 GET, POST, PUT, DELETE 등을 사용하여 클라이언트와 서버 간의 행동을 정의한다.

<aside>
💡 API( Application Programming Interface)
 응용프로그램에서 서비스나 기능을 제공하는 인터페이스를 의미함. API는 소프트웨어 컴포넌트들이 상호작용할 수 있는 규격을 제공하며, 다른 응용프로그램이나 개발자가 해당 서비스를 호출하여 사용할 수 있게 해줌.

</aside>

# 2. FastAPI를 이용해 간단한 API 만들기

```python
# main.py
from fastapi import FastAPI

# Create a FastAPI instance, FastAPI 객체 생성
app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
```

실행:   `$ uvicorn main:app —reload`

- uvicorn:
 FastAPI를 실행하는 웹서버 실행 command line tool
- main:
작성한 main.py
- app:
main.py에서 생성한 객체인 `app = FastAPI()` 를 의미
- —reload:
코드가 바뀌었을 때 서버가 재시작할 수 있도록 해주는 옵션

```python
# path_param.py
from fastapi import FastAPI

# Create a FastAPI instance
app = FastAPI()

@app.get("/items/{item_id}")
def read_item(item_id: int):
        return {"item_id": item_id}
```

실행:   `$ uvicorn main:app —reload`

- path operation
`@app.get("/items/{item_id}")`  : 해당 path로 가서 get operation을 수행.
- path parameter
`{item_id}` 의 값을 Path Parameter라고 함. 입력된 값은 function에 argument로 전달되어 함수가 호출됨.

## 2.1. Query Parameter

 Query Parameter 는 function parameter 로는 사용되지만 Path Operation 에 포함되지 않아 Path Parameter 라고 할 수 없는 parameter 를 의미함.

```python
# query_param.py
from fastapi import FastAPI

# Create a FastAPI instance
app = FastAPI()

fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]

@app.get("/items/")
def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]
```

실행 : `$ uvicorn query_param:app --reload`

- function에 patameter로 들어있는 skip과 limit이 Path Operation인 `@app.get("/items/")` 에는 없음.
- Query는 URL에서 `?` 뒤에 key-value 쌍의 형태로 나타나고, `&` 로 구분되어 사용됨.
    - 위 코드에서는 [`http://localhost:8000/items/?skip=0&limit=10`](http://localhost:8000/items/?skip=0&limit=10) 와 같은 형태로 사용.
- Query Parameter 는 path의 고정된 부분이 아니기 떄문에 optional로 사용될 수 있고, 따라서 기본값을 가질 수 있음
    - 위 코드에서의 기본값은 `skip = 0`, `limit = 10`
- Required Query Parameter: 값을 입력받아야만 하는 Query Parameter
    
    ```python
    @app.get("/items/{item_id}")
    def read_user_item(item_id: str, needy: str):
            item = {"item_id": item_id, "needy": needy}
            return item
    ```
    
    함수에 기본값에 대한 정의가 없음 따라서 `?` 뒤에 parameter를 입력해줘야 함. 
    
    →  [`http://localhost:8000/items/foo-item?needy=someneedy`](http://localhost:8000/items/foo-item?needy=someneedy)
    
    # 3. FastAPI CRUD
    
    ```python
    # crud_path.py
    from fastapi import FastAPI, HTTPException
    
    # Create a FastAPI instance
    app = FastAPI()
    
    # User database
    USER_DB = {}
    
    # Fail response
    NAME_NOT_FOUND = HTTPException(status_code=400, detail="Name not found.")
    
    @app.post("/users/name/{name}/nickname/{nickname}")
    def create_user(name: str, nickname: str):
        USER_DB[name] = nickname
        return {"status": "success"}
    
    @app.get("/users/name/{name}")
    def read_user(name: str):
        if name not in USER_DB:
            raise NAME_NOT_FOUND
        return {"nickname": USER_DB[name]}
    
    @app.put("/users/name/{name}/nickname/{nickname}")
    def update_user(name: str, nickname: str):
        if name not in USER_DB:
            raise NAME_NOT_FOUND
        USER_DB[name] = nickname
        return {"status": "success"}
    
    @app.delete("/users/name/{name}")
    def delete_user(name: str):
        if name not in USER_DB:
            raise NAME_NOT_FOUND
        del USER_DB[name]
        return {"status": "success"}
    ```
    
- Create - `post`
: `name`, `nickname` 입력받아 `USER_DB`에 정보를 저장하고 상태 정보를 return
- Read - `get` 
: `name`을 입력 받아 `nickname`을 찾고 이를 return
- Update - `put` 
: `name`, `nickname`을 입력 받아 `USER_DB`의 정보를 업데이트하고 상태 정보를 return
- Delete - `delete` 
: `name`을 입력받아 `USER_DB`에서 정보를 삭제하고 상태 정보를 return

실행:  `$ uvicorn crud_path:app --reload`

- 결과: [`http://localhost:8000/docs`](http://localhost:8000/docs)
    ![스크린샷 2023-02-13 오후 4 47 07](https://user-images.githubusercontent.com/92080209/218405655-a95c1520-ee46-4f34-b232-2e9c1c6d17db.png)

    

## 3.1. FastAPI CRUD (Pydantic)

Request Body 는 client 에서 API 로 전송하는 데이터를 의미. 반대로 Response Body 는 API 가 client 로 전송하는 데이터를 의미 함.

→  client 와 API 사이에 데이터를 주고 받을 때 데이터의 형식을 지정해 줄 수 있는데, 이를 위해 Pydantic Model 을 사용함.

```python
# crud_pydantic.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class CreateIn(BaseModel):
    name: str
    nickname: str

class CreateOut(BaseModel):
    status: str
    id: int

# Create a FastAPI instance
app = FastAPI()

# User database
USER_DB = {}

# Fail response
NAME_NOT_FOUND = HTTPException(status_code=400, detail="Name not found.")

@app.post("/users", response_model=CreateOut)
def create_user(user: CreateIn):
    USER_DB[user.name] = user.nickname
    user_dict = user.dict()
    user_dict["status"] = "success"
    user_dict["id"] = len(USER_DB)
    return user_dict

@app.get("/users")
def read_user(name: str):
    if name not in USER_DB:
        raise NAME_NOT_FOUND
    return {"nickname": USER_DB[name]}

@app.put("/users")
def update_user(name: str, nickname: str):
    if name not in USER_DB:
        raise NAME_NOT_FOUND
    USER_DB[name] = nickname
    return {"status": "success"}

@app.delete("/users")
def delete_user(name: str):
    if name not in USER_DB:
        raise NAME_NOT_FOUND
    del USER_DB[name]
    return {"status": "success"}
```

- `class CreateIn(BaseModel)` 
: 입력받아야 하는 데이터의 형태를 지정하는 클래스
- `class CreateOut(BaseModel)` 
: 반환하고자 하는 데이터의 형태를 지정하는 클래스
- `create_user(user: CreateIn)` 
: parameter 로 `user` 를 입력 받고, type 은 `CreateIn`
    - `USER_DB[user.name] = user.nickname` : Pydantic Model 에 선언된 변수를 사용하여 DB 에 사용자 정보를 저장
    - Response Body 에 필요한 변수는 `response_model`로 지정된 `CreateOut`모델의 변수인 `status`와 `id` 이므로 이 변수들의 값을 저장

실행: `$ uvicorn crud_pydantic:app --reload`

- 결과
    ![스크린샷 2023-02-13 오후 5 09 17](https://user-images.githubusercontent.com/92080209/218405702-abbcac51-d9df-4ea5-811f-26cfd564f319.png)

    

<aside>
💡 Swagger UI
 Swagger UI는 OpenAPI 스펙으로 작성된 RESTful API의 시각화 도이다. 개발자는 Swagger UI를 사용하여 API의 엔드포인트, 매개변수, 요청 및 응답 본문 등을 살펴보고 테스트할 수 있다. Swagger UI는 인터랙티브한 UI를 제공하여 개발자가 API를 쉽게 이해하고 사용할 수 있도록 도와준다. 또한 Swagger UI는 문서 생성 기능을 제공하여 API에 대한 자동화된 문서를 생성할 수 있다.

</aside>
