kafka-topics --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --alter --topic connector.logistic.packages --partitions 3

kafka-topics --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --describe --topic connector.logistic.packages

kafka-consumer-groups --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --describe --group package_group

kafka-consumer-groups --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --list

kafka-console-consumer --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --topic connector.logistic.packages --group package_group

kafka-topics --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --list

#!bin/bash

# Cleanup
# docker stop master slave
# docker rm master slave
# rm -rf master/data/*
# rm -rf slave/data/*
# docker network rm replicanet

docker-compose down -v 
sudo rm -rf ./db/master/data/*
sudo rm -rf ./db/slave/data/*
docker-compose build
docker-compose up -d

# Build
# docker network create replicanet

# docker run -d --name=master --net=replicanet --hostname=master -p 3307:3306 -v $PWD/master/data:/var/lib/mysql \
# -v $PWD/master/conf/mysql.conf.cnf:/etc/mysql/conf.d/mysql.conf.cnf -e MYSQL_ROOT_PASSWORD=123456 mysql/mysql-server:8.0 --server-id=1 --log-bin='mysql-bin-1.log' --binlog_format=ROW

# docker run -d --name=slave --net=replicanet --hostname=slave -p 3308:3306 -v $PWD/slave/data:/var/lib/mysql \
# -v $PWD/slave/conf/mysql.conf.cnf:/etc/mysql/conf.d/mysql.conf.cnf -e MYSQL_ROOT_PASSWORD=123456 mysql/mysql-server:8.0 --server-id=2

MASTER_CONTAINER=master
SLAVE_CONTAINER=slave
PASSWORD=It235711

until docker exec -it ${MASTER_CONTAINER} mysql -uroot -p${PASSWORD} \
  -e "CREATE USER 'slave'@'%' IDENTIFIED BY '${PASSWORD}';" \
  -e "GRANT REPLICATION SLAVE ON *.* TO 'slave'@'%';" \
  -e "SHOW MASTER STATUS;"
do
    echo "Waiting for master database connection..."
    sleep 1
done

MS_STATUS=`docker exec ${MASTER_CONTAINER} sh -c "mysql -u root -p${PASSWORD} -e 'SHOW MASTER STATUS' -s"`
CURRENT_LOG=`echo $MS_STATUS | tail -n 1 | awk '{print $1}'`
CURRENT_POS=`echo $MS_STATUS | tail -n 1 | awk '{print $2}'`

echo $CURRENT_LOG
echo $CURRENT_POS

until docker exec -it ${SLAVE_CONTAINER} mysql -uroot -p${PASSWORD} \
    -e "CHANGE MASTER TO MASTER_HOST='${MASTER_CONTAINER}', MASTER_USER='${SLAVE_CONTAINER}', \
      MASTER_PASSWORD='${PASSWORD}', MASTER_LOG_FILE='$CURRENT_LOG', MASTER_LOG_POS=$CURRENT_POS, GET_MASTER_PUBLIC_KEY=1;"
do
    echo "Waiting for slave database connection..."
    sleep 1
done

docker exec -it ${SLAVE_CONTAINER} mysql -uroot -p${PASSWORD} -e "START SLAVE;"

docker exec -it ${SLAVE_CONTAINER} mysql -uroot -p${PASSWORD} -e "SHOW SLAVE STATUS\G"

docker exec -it ${MASTER_CONTAINER} mysql -uroot -p${PASSWORD} - 

docker exec -it ${SLAVE_CONTAINER} mysql -uroot -p${PASSWORD} -e "SHOW DATABASES;"