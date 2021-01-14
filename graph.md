

<br />
<p align="center">
  <h2 align="center">Working with Graph (Neo4j & Neptune) Database in Linux</h2>
</p>


<!-- TABLE OF CONTENTS -->
<br/>
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#description">Description</a>
    </li>
    <li>
      <a href="#working-with-mongodb-community-edition-in-ec2">Working with MongoDB Community Edition in EC2</a>
      <ul>
        <li><a href="#pre-requests">Pre requests</a></li>
        <li><a href="#install-mongodb-community-edition">Install MongoDB Community Edition</a></li>
        <li><a href="#run-mongodb-community-edition">Run MongoDB Community Edition</a></li>
        <li><a href="#working-with-mongodb-from-shell">Working with MongoDB from shell</a></li>
      </ul>
    </li>
    <li>
      <a href="#working-with-aws-managed-nosql-dynamodb">Working with AWS managed NoSQL DynamoDB</a>
      <ul>
        <li><a href="#pre-requests-and-environment-setup">Pre-requests and environment setup</a></li>
        <li><a href="#create-a-dynamodb-table-using-aws-cli">Create a DynamoDB table using aws cli</a></li>
        <li><a href="#working-with-dynamodb">Working with DynamoDB</a></li>
      </ul>
    </li>
  </ol>
</details>
<br/>

## Description

Shows how to create and configure Graph database from a linux shell. <br/>
It covers installing Neo4j, configuring databases in a linux instance and accessing cloud managed Graph AWS Neptune in linux.
<br/>

## Working with Neo4j in EC2


### Pre-requests

1. Create and launch an EC2 instance in AWS console ([reference](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#LaunchInstanceWizard:))
2. SSH login to the instance


### Install Neo4j

1. Install openjdk 11
   ```sh
   sudo apt update
   sudo apt install openjdk-11-jre-headless
   ```
2. Add Neo4j debian package to the linux package manager
   ```sh
   # add package
   wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
   echo 'deb https://debian.neo4j.com stable 4.2' | sudo tee -a /etc/apt/sources.list.d/neo4j.list
   sudo apt update
   
   # verify available Neo4j versions listed
   apt list -a neo4j
   ```
   We should see something like below.
   ```sh
   Listing... Done
   neo4j/stable 1:4.2.2 all
   neo4j/stable 1:4.2.1 all
   neo4j/stable 1:4.2.0 all
   ```
3. Install Neo4j community edition
   ```sh
   sudo apt install neo4j=1:4.2.2
   ```

### Run Neo4j community edition

1. Verify MongoDB running status
   ```sh
   sudo systemctl status neo4j
   ```
   Expected output:
   <img src="https://i.imgur.com/AuyVcrk.jpg"></img>
2. Start Neo4j
   ```sh
   sudo systemctl start neo4j
   ```
3. Stop noe4j
   ```sh
   sudo systemctl stop neo4j
   ```
4. Start Neo4j console
   ```sh
   # This only works when neoj4 is currently stopped.
   sudo neo4j console
   ```


### Working with Neo4j from shell

1. Connect with Neo4j
   ```sh
   mongo # connects with local mongodb, default port is 27017
   mongo --port 28015 # connects with mongo on a specific port
   mongo --host mongodb0.example.com --port 28015 # connects with remote mongodb server
   mongo --username alice --password --authenticationDatabase admin --host mongodb0.examples.com --port 28015 # connect with remote mongodb with authentication
   ```
2. Working with ```mongo``` Shell<br/>
   To display the database you are using,
   ```mongo
   db
   ```
   To create or switch databases,
   ```mongo
   use mydb
   ```
   To insert documents in a database, this also creates a database if no such database exists
   ```mongo
   db.mydb.insert({"name":"Bill", "email":"bill@email.com"})
   ```
   To check database lists,
   ```mongo
   show dbs
   ```
<br/>

## Working with AWS managed NoSQL DynamoDB

### Pre-requests and environment setup

1. Install aws-cli in your linux instance
   ```sh
   sudo apt update
   sudo apt install awscli -y
   ```
2. Configure aws IAM user credentials assuming you created an IAM user and granted DynamoDB access permission ([reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console))
   ```sh
   aws configure
   ```
   <img src="https://i.imgur.com/DPpag3q.jpg"></img>
   Enter access key id and secret key, region where your RDS instance will be located, output format as json.<br/>

### Create a DynamoDB table using aws cli

   ```sh
   aws dynamodb create-table \
    --table-name MusicCollection \
    --attribute-definitions AttributeName=Artist,AttributeType=S AttributeName=SongTitle,AttributeType=S \
    --key-schema AttributeName=Artist,KeyType=HASH AttributeName=SongTitle,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=1,WriteCapacityUnits=1
   ```
   Expected output:
   ```json
    {
        "TableDescription": {
            "AttributeDefinitions": [
                {
                    "AttributeName": "Artist",
                    "AttributeType": "S"
                },
                {
                    "AttributeName": "SongTitle",
                    "AttributeType": "S"
                }
            ],
            "TableName": "MusicCollection",
            "KeySchema": [
                {
                    "AttributeName": "Artist",
                    "KeyType": "HASH"
                },
                {
                    "AttributeName": "SongTitle",
                    "KeyType": "RANGE"
                }
            ],
            "TableStatus": "CREATING",
            "CreationDateTime": 1610587688.742,
            "ProvisionedThroughput": {
                "NumberOfDecreasesToday": 0,
                "ReadCapacityUnits": 1,
                "WriteCapacityUnits": 1
            },
            "TableSizeBytes": 0,
            "ItemCount": 0,
            "TableArn": "arn:aws:dynamodb:us-west-2:867719205611:table/MusicCollection",
            "TableId": "e790f02e-b0b6-4fe8-ac63-ee3c31980dc0"
        }
    }
   ```

### Working with DynamoDB

1. Put item into a DynamoDB table
   ```sh
   aws dynamodb put-item \
    --table-name MusicCollection \
    --item '{
        "Artist": {"S": "No One You Know"},
        "SongTitle": {"S": "Call Me Today"} ,
        "AlbumTitle": {"S": "Somewhat Famous"} 
      }' \
    --return-consumed-capacity TOTAL
   ```
   Response from AWS:
   ```json
   {
       "ConsumedCapacity": {
           "TableName": "MusicCollection",
           "CapacityUnits": 1.0
       }
   }
   ```
2. Verify tables in AWS console
   * [DynamoDB tables](https://us-west-2.console.aws.amazon.com/dynamodbv2/home?region=us-west-2#tables)
   * [Items in a table](https://us-west-2.console.aws.amazon.com/dynamodbv2/home?region=us-west-2#table?name=MusicCollection&initialTableGroup=%23all)

Lets try out!
