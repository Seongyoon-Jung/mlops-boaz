# Chapter 7. Kafka

# 6주차_kafka

<img width="632" alt="스크린샷 2023-02-26 오후 5 38 42" src="https://user-images.githubusercontent.com/92080209/221400575-d3302b39-aae7-41df-b4b0-1895e191d712.png">

 4주차의 Stream Serving을 구현하기 위해서 실시간으로 데이터를 전달할 수 있는 데이터 파이프라인을 구축해야한다. 이번 주차에서는 Kafka를 사용하여 데이터 파이프라인을 구축해본다.

# Kafka System

```docker
# kafka-docker-compose.yaml
version: "3"

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.3.0
    container_name: zookeeper
    ports:
      - 2181:2181
    environment:
      ZOOKEEPER_SERVER_ID: 1
      ZOOKEEPER_CLIENT_PORT: 2181

  broker:
    image: confluentinc/cp-kafka:7.3.0
    container_name: broker
    depends_on:
      - zookeeper
    ports:
      - 9092:9092
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://broker:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0

  schema-registry:
    image: confluentinc/cp-schema-registry:7.3.0
    container_name: schema-registry
    depends_on:
      - broker
    ports:
      - 8081:8081
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: broker:29092
      SCHEMA_REGISTRY_LISTENERS: http://schema-registry:8081

  connect:
    build:
      context: .
      dockerfile: connect.Dockerfile
    container_name: connect
    depends_on:
      - broker
      - schema-registry
    ports:
      - 8083:8083
    environment:
      CONNECT_BOOTSTRAP_SERVERS: broker:29092
      CONNECT_REST_ADVERTISED_HOST_NAME: connect
      CONNECT_GROUP_ID: docker-connect-group
      CONNECT_CONFIG_STORAGE_TOPIC: docker-connect-configs
      CONNECT_CONFIG_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_OFFSET_STORAGE_TOPIC: docker-connect-offsets
      CONNECT_OFFSET_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_STATUS_STORAGE_TOPIC: docker-connect-status
      CONNECT_STATUS_STORAGE_REPLICATION_FACTOR: 1
      CONNECT_KEY_CONVERTER: org.apache.kafka.connect.storage.StringConverter
      CONNECT_VALUE_CONVERTER: org.apache.kafka.connect.json.JsonConverter
      CONNECT_VALUE_CONVERTER_SCHEMA_REGISTRY_URL: http://schema-registry:8081

networks:
  default:
    name: mlops-network
    external: true
```

`kafka-docker-compose.yaml` 을 통해 Zookeeper&Broker, Schema Registry, connect를 생성함.

`docker compose -p part7-kafka -f kafka-docker-compose.yaml up -d` 

- -p : project name
- -f: file name

docker compose 를 사용해 위의 서비스를 실행함.

실행 결과>

![스크린샷 2023-02-25 오후 11 38 25](https://user-images.githubusercontent.com/92080209/221400606-1868e8a2-a7f9-4c2d-891c-c08fc3431e05.png)


# Source Connector

 해당 챕터를 시작하기에 앞서 part1의 DB를 이용함.

<img width="596" alt="스크린샷 2023-02-26 오후 3 41 08" src="https://user-images.githubusercontent.com/92080209/221400625-8d055a1d-5fed-40da-be17-67b558666f5a.png">


```json
# source_connector.json
{
    "name": "postgres-source-connector",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector",
        "connection.url": "jdbc:postgresql://postgres-server:5432/mydatabase",
        "connection.user": "myuser",
        "connection.password": "mypassword",
        "table.whitelist": "iris_data",
        "topic.prefix": "postgres-source-",
        "topic.creation.default.partitions": 1,
        "topic.creation.default.replication.factor": 1,
        "mode": "incrementing",
        "incrementing.column.name": "id",
        "tasks.max": 2,
        "transforms": "TimestampConverter",
        "transforms.TimestampConverter.type": "org.apache.kafka.connect.transforms.TimestampConverter$Value",
        "transforms.TimestampConverter.field": "timestamp",
        "transforms.TimestampConverter.format": "yyyy-MM-dd HH:mm:ss.S",
        "transforms.TimestampConverter.target.type": "string"
    }
}
```

source connector 을 json 파일로 설정함.

`$ curl -X POST [http://localhost:8083/connectors](http://localhost:8083/connectors) -H "Content-Type: application/json" -d @source_connector.json`

curl을 이용하여 connect의 REST API에 POST method로 보냄.

`$ kcat -L -b localhost:9092`

<img width="407" alt="스크린샷 2023-02-26 오후 2 52 22" src="https://user-images.githubusercontent.com/92080209/221400641-31b1ed36-759f-474b-ae22-c0778c823b36.png">


 kcat 명령어를 이용하여 모든 토픽 리스트를 확인한다.
결과값 중간에 “postgres-source-iris_data” 라는 새로운 토픽이 생성된 것을 확인할 수 있다.

`$ kcat -b localhost:9092 -t postgres-source-iris_data`

<img width="1496" alt="스크린샷 2023-02-26 오후 2 52 53" src="https://user-images.githubusercontent.com/92080209/221400649-cbe644cc-3d85-4cb0-bfb1-93923d3919bc.png">


kcat 명령어를 이용하여 해당 토픽에 데이터가 쌓이고 있는 것을 확인한다.

<img width="1496" alt="스크린샷 2023-02-26 오후 2 52 53" src="https://user-images.githubusercontent.com/92080209/221400705-90899b21-26b7-46e7-b690-ba8b1fb3bd60.png">


<aside>
💡 kcat?
→ kafka cat의 뜻으로 Apach kafka의 producer와 consumer도구이다.
* consumer 모드에서 kcat은 주제 및 파티션에서 메세지를 읽고 출력한다.
* producer 모드에서는 표준 입력(stdin)에서 메세지를 읽고, topic에 대해서 데이터를 보낼 수 있다.
* 메타데이터 목록 모드( -L)에서 kcat은 Kafka cluster와 topic, partition, replica 및 동기화 복제본(ISR)의 현재 상태를 표시합니다.

</aside>

# Sink Connector

```docker
# target-docker-compose.yaml
version: "3"

services:
  target-postgres-server:
    image: postgres:14.0
    container_name: target-postgres-server
    ports:
      - 5433:5432
    environment:
      POSTGRES_USER: targetuser
      POSTGRES_PASSWORD: targetpassword
      POSTGRES_DB: targetdatabase
    healthcheck:
      test: ["CMD", "pg_isready", "-q", "-U", "targetuser", "-d", "targetdatabase"]
      interval: 10s
      timeout: 5s
      retries: 5

  table-creator:
    build:
      context: .
      dockerfile: target.Dockerfile
    container_name: table-creator
    depends_on:
      target-postgres-server:
        condition: service_healthy

networks:
  default:
    name: mlops-network
    external: true
```

위 docker compose 파일을 이용해 Target DB 서버와 Table Creator를 띄운다.

```json
# sink_connector.json
{
    "name": "postgres-sink-connector",
    "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "connection.url": "jdbc:postgresql://target-postgres-server:5432/targetdatabase",
        "connection.user": "targetuser",
        "connection.password": "targetpassword",
        "table.name.format": "iris_data",
        "topics": "postgres-source-iris_data",
        "auto.create": false,
        "auto.evolve": false,
        "tasks.max": 2,
        "transforms": "TimestampConverter",
        "transforms.TimestampConverter.type": "org.apache.kafka.connect.transforms.TimestampConverter$Value",
        "transforms.TimestampConverter.field": "timestamp",
        "transforms.TimestampConverter.format": "yyyy-MM-dd HH:mm:ss.S",
        "transforms.TimestampConverter.target.type": "Timestamp"
    }
}
```

`$ curl -X POST [http://localhost:8083/connectors](http://localhost:8083/connectors) -H "Content-Type: application/json" -d @sink_connector.json`

- Sink Connector를 생성하는 json 파일을 curl 을 이용하여 connect의 REST API에 POST method로 보낸다.

psql을 이용하여 Target DB에 접속하고 iris_data  테이블에 있는 데이터를 

확인한다.

<img width="814" alt="스크린샷 2023-02-26 오후 3 03 50" src="https://user-images.githubusercontent.com/92080209/221400692-5f76788c-d6b5-49e2-8c07-a7c3b33c4e40.png">


---

## Connect

- Connect는 데이터 시스템과 kafka간의 데이터를 확장 가능하고, 안전한 방법으로 streaming하기 위한 도구. 때문에 데이터를 어디에서 가져오고, 어디에 전달하는지 알려주는 Connector를 정의해야함.
- Connect 와 Connector는 다른 역할을 수행한다. Connect 는 프레임워크이고 Connector 는 그 안에서 돌아가는 플러그인.

## Source Connector

- Source System의 데이터를 broker의 topic으로 publish하는 connector.
- Producer의 역할을 하는 Connector

## Sink Connector

- Broker의 topic에 있는 데이터를 subscribe하여 target system에 전달하는 connector.

<img width="831" alt="스크린샷 2023-02-26 오후 5 21 57" src="https://user-images.githubusercontent.com/92080209/221400734-482ce0fe-6223-4499-8974-7af174e77a57.png">


## Source, Sink Connector의 장점

- Producer/ Consumer와 연결되어 있는 Server가 100개, 1000개… 더 많아 지면 이에 따라 Producer와 Consumer가 늘어날 수 있다. 하지만, kafka connect를 연결하는 것만으로도 이에 대한 비용을 줄일 수 있다.
- Connector 에 대한 설정 파일로 각 Server가 kafka broker와 연결할 수 있다.
- Source Connector 의 경우, Connector 의 유형, 연결할 URL, user 와 password, 테이블 이름, 토픽의 파티션 수, Replication Factor 수 등을 설정해주면 Connect 에서 인스턴스로 생성할 수 있다.
