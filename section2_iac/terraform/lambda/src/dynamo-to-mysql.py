
import json
import re
import boto3
import pymysql
import logging
import sys

rds_host = "34.215.41.201"
name = "admin"
password = "Layerstack1!"
db_name = "testdb"
port = 3306

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(host=rds_host, user=name,
                           passwd=password, db=db_name)
except Exception as e:
    print(e)
    sys.exit()

reserved_fields = ["uid", "_id", "_type", "_source", "_all", "_parent",
                   "_fieldnames", "_routing", "_index", "_size", "_timestamp", "_ttl"]


def handler(event, context):

    # Loop over the DynamoDB Stream records
    for record in event['Records']:

        print("new record", record)

        try:

            if record['eventName'] == "INSERT":
                insert_document(record)

        except Exception as e:
            print("Failed to process:")
            print(json.dumps(record))
            print("ERROR: " + repr(e))
            continue


# Process INSERT events
def insert_document(record):
    table = getTable(record)
    print("Dynamo Table: " + table)

    # Unmarshal the DynamoDB JSON to a normal JSON
    doc = json.dumps(unmarshalJson(record['dynamodb']['NewImage']))
    doc = json.loads(doc)
    print(doc)

    datetime = doc["ID"]
    _open = doc["open"]
    _low = doc["low"]
    _high = doc["high"]
    _close = doc["close"]
    if _open > _close:
        res = {"status": "OK", "job": "Not inserted"}
        print(res)
        return res

    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS AAPL1H (id INT PRIMARY KEY AUTO_INCREMENT, datetime varchar(255) NOT NULL, open decimal(10, 2) NOT NULL, high decimal(10, 2) NOT NULL, low decimal(10, 2) NOT NULL, close decimal(10, 2) NOT NULL);")
        cur.execute(
            f"INSERT INTO AAPL1H (datetime, open, high, low, close) VALUES ('{datetime}', {_open}, {_high}, {_low}, {_close});")
        conn.commit()
        print("Item successfully inserted")

    return "OK"


# Return the dynamoDB table that received the event. Lower case it
def getTable(record):
    p = re.compile('arn:aws:dynamodb:.*?:.*?:table/([0-9a-zA-Z_-]+)/.+')
    m = p.match(record['eventSourceARN'])
    if m is None:
        raise Exception("Table not found in SourceARN")
    return m.group(1).lower()


# Unmarshal a JSON that is DynamoDB formatted
def unmarshalJson(node):
    data = {}
    data["M"] = node
    return unmarshalValue(data, True)

# ForceNum will force float or Integer to


def unmarshalValue(node, forceNum=False):
    for key, value in list(node.items()):
        if (key == "NULL"):
            return None
        if (key == "S" or key == "BOOL"):
            return value
        if (key == "N"):
            if (forceNum):
                return int_or_float(value)
            return value
        if (key == "M"):
            data = {}
            for key1, value1 in list(value.items()):
                if key1 in reserved_fields:
                    key1 = key1.replace("_", "__", 1)
                data[key1] = unmarshalValue(value1, True)
            return data
        if (key == "BS" or key == "L"):
            data = []
            for item in value:
                data.append(unmarshalValue(item))
            return data
        if (key == "SS"):
            data = []
            for item in value:
                data.append(item)
            return data
        if (key == "NS"):
            data = []
            for item in value:
                if (forceNum):
                    data.append(int_or_float(item))
                else:
                    data.append(item)
            return data

# Detect number type and return the correct one


def int_or_float(s):
    try:
        return int(s)
    except ValueError:
        return float(s)
