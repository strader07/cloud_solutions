

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
        <li><a href="#install-neo4j">Install Neo4j</a></li>
        <li><a href="#run-neo4j-community-edition">Run Neo4j community edition</a></li>
        <li><a href="#working-with-neo4j-from-cypher-shell">Working with Neo4j from cypher-shell</a></li>
      </ul>
    </li>
    <li>
      <a href="#working-with-aws-managed-graph-neptune">Working with AWS managed Graph Neptune</a>
      <ul>
        <li><a href="#pre-requests-and-environment-setup">Pre-requests and environment setup</a></li>
        <li><a href="#create-a-neptune-database-instance-using-aws-cli">Create a Neptune Database instance using aws cli</a></li>
        <li><a href="#working-with-neptune">Working with Neptune</a></li>
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
   # community edition
   sudo apt install neo4j=1:4.2.2
   
   # enterprise edition
   sudo apt install neo4j-enterprise=1:4.2.2
   ```

### Run Neo4j community edition

1. Verify Neoj4 running status
   ```sh
   sudo systemctl status neo4j
   ```
   Expected output:
   <img src="https://i.imgur.com/AuyVcrk.jpg"></img>
2. Start Neo4j
   ```sh
   sudo systemctl start neo4j
   # or restart with
   sudo systemctl restart neo4j
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
4. Edit Neo4j database configurations
   ```sh
   sudo nano /etc/neo4j/neo4j.conf
   ```
   Add or uncomment following lines for your first configuration.
   ```
   dbms.default_listen_address=0.0.0.0
   dbms.connector.bolt.listen_address=:7687
   dbms.connector.http.listen_address=:7474
   ```
   Exit nano editor hit "ctrl + x" and "enter" to save the changes.<br/>
   After editing the configuration file, restart the service to invoke the changes.
   ```
   sudo systemctl restart neo4j
   ```


### Working with Neo4j from cypher-shell
cypher-shell is installed along with neo4j installation.<br/>

1. Login to the server (cypher-shell)
   ```sh
   # initial username and passowrd - 'neo4j', 'neo4j'
   sudo cypher-shell -u neo4j -p neo4j
   ```
   Set up a new password on prompt.<br/>
   
   Or login using a web browser - [http://52.88.242.226:7474/browser](http://52.88.242.226:7474/browser)<br/>
   Or if you are setting neo4j in local - [http://localhost:7474/browser](http://localhost:7474/browser)
   
2. Working with ```cypher-shell``` query<br/>
   Note: all cypher-shell queries come with semi-colon.<br/>

   To display all the databases,
   ```cypher-shell
   # individual database
   SHOW DATABASE neo4j;
   
   # all databases
   SHOW DATABASES;
   ```
   By default, we have following two databases.<br/>
   <img src="https://i.imgur.com/ge7PAEu.jpg"></img><br/>
   
   Additional commands for database show<br/>
   ```cypher-shell
   SHOW DEFAULT DATABASE;
   ```

   To create databases,
   ```cypher-shell
   # This only works with neo4j enterprise edition
   CREATE DATABASE sales;
   SHOW DATABASES;
   ```
   To switch a database,
   ```cypher-shell
   :use sales
   ```
   To create or replace a database,
   ```cypher-shell
   CREATE OR REPLACE DATABASE sales;
   ```
   To retreive records,
   ```cypher-shell
   match (n) return count(n) as countNode;
   ```
   To start and stop a database,
   ```cypher-shell
   STOP DATABASE sales;
   START DATABASE sales;
   ```
   To remove a database,
   ```cypher-shell
   DROP DATABASE sales;
   ```
<br/>

## Working with AWS managed Graph Neptune

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

### Create a Neptune Database instance using aws cli

### Working with Neptune

Lets try out!
