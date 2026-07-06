from db import *

print(load_alerts().head())
print(load_metrics().head())
print(load_kafka_logs().head())
print(load_api_logs().head())