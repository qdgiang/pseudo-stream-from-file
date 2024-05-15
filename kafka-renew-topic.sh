# delete old topics
kafka-topics.sh --delete --topic pseudo-stream --bootstrap-server localhost:9092
# create new topics
kafka-topics.sh --create --topic pseudo-stream --partitions 3 --replication-factor 2 --bootstrap-server localhost:9092