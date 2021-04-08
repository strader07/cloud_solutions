import json
import requests
import boto3
from decimal import Decimal


def handler(event, context):
    # TODO implement
    symbol = "AAPL"
    interval = "1h"
    api = ""
    output = 1

    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&apikey={api}&outputsize={output}"
    try:
        data = requests.get(url).json()["values"][0]
    except Exception as e:
        print(e)

    ddb = "aapl_hourly_prices"
    client = boto3.resource("dynamodb")
    table = client.Table(ddb)
    data["open"] = Decimal(data["open"])
    data["high"] = Decimal(data["high"])
    data["low"] = Decimal(data["low"])
    data["close"] = Decimal(data["close"])

    item = {
        "ID": data["datetime"],
        "open": data["open"],
        "high": data["high"],
        "low": data["low"],
        "close": data["close"],
        "volume": data["volume"]
    }

    try:
        res = table.put_item(
            Item=item
        )
        print(res)
    except Exception as e:
        print(e)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
