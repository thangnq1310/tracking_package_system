kafka-topics --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --alter --topic dbserver1.inventory.customers --partitions 3

kafka-topics --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --describe --topic dbserver1.inventory.customers

kafka-consumer-groups --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --describe --group inventory_group

kafka-console-consumer --bootstrap-server kafka1:9092,kafka2:9093,kafka3:9094 --topic dbserver1.inventory.customers --group inventory_group