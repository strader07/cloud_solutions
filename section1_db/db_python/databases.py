
import pandas as pd
import numpy as np
import json
import uuid

import pymysql
from sqlalchemy import create_engine
from pymongo import MongoClient
from neo4j import GraphDatabase

import boto3


def test_ec2_mysql():
    print("\n\nTesting connection with EC2 mysql database!\n")

    _user = 'admin'
    _pwd = 'Layerstack1!'
    _host = '34.215.41.201'
    _db = 'testdb'

    try:
        conn = create_engine(f'mysql+pymysql://{_user}:{_pwd}@{_host}/{_db}').connect()
    except Exception as e:
        print(e)
        return 0

    print("\nReading from a file")
    df = pd.read_csv('data/sample.csv')

    print("\nWriting data to the database")
    df.to_sql("UserDetails", conn, if_exists='replace', index=False, method='multi')
    print("Successfully written to database")

    print("\nReading data from the database")
    df = pd.read_sql("UserDetails", conn)
    print("Success reading from MySQL db")

    return 0


def test_rds_mysql():

    print("\n\nTesting connection with AWS managed RDS mysql database!\n")

    _user = 'admin'
    _pwd = 'Adminpassword1!'
    _host = 'testmysqldbinstance.cj90nrslvzqi.us-west-2.rds.amazonaws.com'
    _db = 'testdb'

    try:
        conn = create_engine(f'mysql+pymysql://{_user}:{_pwd}@{_host}/{_db}').connect()
    except Exception as e:
        print(e)
        conn = pymysql.connect(host=_host,
                       user=_user,
                       password=_pwd)
        conn.cursor().execute('create database testdb')
        conn = create_engine(f'mysql+pymysql://{_user}:{_pwd}@{_host}/{_db}').connect()

    print("\nReading from a file")
    df = pd.read_csv('data/sample.csv')

    print("\nWriting data to the database")
    df.to_sql("UserDetails", conn, if_exists='replace', index=False, method='multi')
    print("Successfully written to database")

    print("\nReading data from the database")
    df = pd.read_sql("UserDetails", conn)
    print("Success reading from MySQL db")

    return 0


def test_dynamodb():
    print("\n\nTesting DynamoDB!\n")
    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    ddb_table = "UserDetails"
    swoonpr = dynamodb.Table(ddb_table)

    df = pd.read_csv("data/sample.csv")
    df = df.fillna("")
    df = df.drop_duplicates().reset_index(drop=True)

    print("\nWriting data to a dynamodb table")
    items = df.to_dict("records")
    ids = []
    names = []
    for item in items:
        _uuid_str = "|".join([str(x) for x in list(item.values())])
        item["ID"] = str(uuid.uuid5(uuid.NAMESPACE_X500, _uuid_str))
        item["Name"] = item["FirstName"] + " " + item["LastName"]
    
        try:
            res = swoonpr.put_item(
                Item = item
            )
            print(f"Successly inserted - ID: {item['ID']}")
            ids.append(item["ID"])
            names.append(item["Name"])
        
        except Exception as e:
            print(item["ID"], ": ", e)
            return False

    print("Successfully inserted all items")

    print("\nReading data (10 items) from a dynamodb table")
    for _id, name in zip(ids[:5], names[:5]):
        res = swoonpr.get_item(Key={
            "ID": _id,
            "Name": name
        })
        print(res)
    print("Successfully loaded items from a dynamodb table")


def test_mongodb():
    print("\n\nTesting MongoDB!\n")
    mongo_host = "34.215.41.201"
    mongo_port = 27017
    db_name = "testdb"
    collection_name = "userDetails"

    client = MongoClient(f"mongodb://{mongo_host}:{mongo_port}/")
    db = client[db_name]
    collection = db[collection_name]
    print(collection)
    
    df = pd.read_csv("data/sample.csv")
    df = df.fillna("")
    items = df.to_dict("records")

    print("\n Writing items to mongo db")
    res = collection.insert_many(items)
    print(f"Successfully written all items - {res.inserted_ids}")

    print("\n Finding items in mongodb")
    res = collection.find()
    for item in res:
        print(item)


def test_neo4j():
    print("\n\nTesting Neo4j Graph Database!\n")
    neo4j_host = "52.88.242.226"
    neo4j_port = 7687
    user = "neo4j"
    db_name = "neo4j"
    password = "Layerstack1!"
    
    uri = f"neo4j://{neo4j_host}:{neo4j_port}"
    driver = GraphDatabase.driver(uri, auth=(user, password))
    session = driver.session(database=db_name)

    print("\n Writing data to a graph database.")
    query_string = '''
    LOAD CSV WITH HEADERS FROM
    'https://achanbucket.s3-us-west-2.amazonaws.com/sample.csv'
    AS line
    CREATE (:UserDetails {FirstName: line.FirstName, LastName: line.LastName, ZipCode: line.ZipCode})
    '''
    res = session.run(query_string)
    print(f"Successfully written items to the graph database")

    print("\n Reading data from Neo4j")
    query_string = '''
    MATCH (u:UserDetails)
    RETURN DISTINCT u.FirstName, u.LastName, u.ZipCode
    ORDER BY u.FirstName
    '''
    res = session.run(query_string)
    for item in res:
        print(item)
    print(f"\nSuccessfully loaded items")


def main():
    test_ec2_mysql()
    test_rds_mysql()
    test_mongodb()
    test_dynamodb()
    test_neo4j()


main()
