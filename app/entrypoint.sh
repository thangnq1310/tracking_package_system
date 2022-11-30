#!/bin/bash
curl --location --request POST 'debezium:8083/connectors/' \
--header 'Accept: application/json' \
--header 'Content-Type: application/json' \
--data-raw '{
    "name": "logistic-connector",
    "config": {
        "connector.class": "io.debezium.connector.mysql.MySqlConnector",
        "tasks.max": "1",
        "database.hostname": "mysql_kafka",
        "database.port": "3306",
        "database.user": "root",
        "database.password": "It235711",
        "database.allowPublicKeyRetrieval":"true",
        "database.server.id": "184054",
        "topic.prefix": "connector",
        "database.include.list": "logistic",
        "schema.history.internal.kafka.bootstrap.servers": "kafka1:9092,kafka2:9093,kafka3:9094",
        "schema.history.internal.kafka.topic": "schemahistory.logistic"
    }
}'