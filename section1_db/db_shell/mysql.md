<br />
<p align="center">
  <h2 align="center">Working with MySQL in Linux</h2>
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
      <a href="#working-with-mysql-server-in-ec2">Working with MySQL server in EC2</a>
      <ul>
        <li><a href="#pre-requests">Pre requests</a></li>
        <li><a href="#setup-mysql-server">Setup mysql server</a></li>
        <li><a href="#configure-root-to-use-mysql-shell">Configure root to use MySQL shell</a></li>
        <li><a href="#run-and-stop-mysql-service">Run and stop MySQL service</a></li>
        <li><a href="#working-with-mysql-users-databses-and-tables-from-shell">Working with MySQL users, databses, and tables from shell</a></li>
      </ul>
    </li>
    <li>
      <a href="#working-with-aws-managed-rds">Working with AWS managed RDS</a>
      <ul>
        <li><a href="#pre-requests-and-environment-setup">Pre-requests and environment setup</a></li>
        <li><a href="#create-a-rds-instance-using-aws-cli">Create a RDS instance using aws cli</a></li>
        <li><a href="#working-with-mysql-database-in-rds-instances">Working with MySQL database in RDS instances</a></li>
      </ul>
    </li>
  </ol>
</details>
<br/>

## Description

Shows how to create and configure mysql server in a linux instance. <br/>
It covers installing mysql server, configuring database and tables in an linux instance itself and accessing cloud managed mysql databases.

## Working with MySQL server in EC2


### Pre-requests

1. Create and launch an EC2 instance in AWS console ([reference](https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#LaunchInstanceWizard:))
2. SSH login to the instance


### Setup mysql server

1. Update the local repository index
   ```sh
   sudo apt update
   ```
2. Install mysql server with apt
   ```sh
   sudo apt install mysql-server -y
   ```
3. Verify installation
   ```sh
   mysql --version
   ```
   Expected output <br/>
   <img src="https://i.imgur.com/AqKqvd4.jpg"></img>
4. Security configurations
   ```sh
   sudo mysql_secure_installation
   ```
   <img src="https://i.imgur.com/SGvS339.jpg"></img><br/>
   Press y on this prompt, then choose your password level following instructions.<br/>
   Give a root password and continue, hit y for 'remove anonymous users?'.<br/>
   Recommend hitting y for 'Disallow root login remotely?' to protect anyone guessing the root password.<br/>
   Hit y for 'Remove test database and access to it?' and 'Reload privilege tables now?'.<br/>


### Configure root to use MySQL shell

1. Start MySQL shell
   ```sh
   sudo mysql
   ```
   Now we should be in MySQL shell and what we enter there is SQL queries until we exit.<br/>
   Note: sql commands are followed by semi-colon (;)
2. Check authenticatin method for MySQL users
   ```sql
   SELECT user,authentication_string,plugin,host FROM mysql.user;
   ```
   <img src="https://i.imgur.com/ZATsYQ0.jpg"></img>
3. Change root auth method
   ```sql
   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Layerstack1!';
   ```
   Note: The password string ('Layerstack1!' in command) must meet the policies depending on the chosed level of strength in step 4 in setup section.<br/>
   Remind:<br/>
   <strong>LOW</strong> Length >= 8 characters.<br/>
   <strong>MEDIUM</strong> Length >= 8, numeric, mixed case, and special characters.<br/>
   <strong>STRONG</strong> Length >= 8, numeric, mixed case, special characters and dictionary file.<br/>
4. Grand the changes
   ```sql
   FLUSH PRIVILEGES;
   ```
5. Re-check auth methods to see if changes are applied
   ```sql
   SELECT user,authentication_string,plugin,host FROM mysql.user;
   ```
   Now we should see the following table.
   <img src="https://i.imgur.com/SsvkgVi.jpg"></img>
6. Exit MySQL shell
   ```sql
   exit
   ```


### Run and stop MySQL service

1. Check the status
   ```sh
   systemctl status mysql.service
   ```
   <img src="https://i.imgur.com/c7vCn6C.png"></img>
   If we see something different than above...
2. Run the service
   ```sh
   sudo systemctl start mysql
   ```
3. Stop the service
   ```sh
   sudo systemctl stop mysql
   ```


### Working with MySQL users, databses, and tables from shell

1. Login to mysql shell with root user
   ```sh
   mysql -u root -p
   ```
2. Create a new user - sql command
   ```sql
   CREATE USER 'new_user'@'localhost' IDENTIFIED BY 'new_password';
   ```
   Note: replace 'new_user' and 'new_password' with your own
3. Create a new database, a table, loading db and table info
   ```sql
   CREATE DATABASE testdb; # creates a database named 'testdb'
   SHOW DATABASES; # shows all the databases
   USE testdb; # selects the database 'testdb' as the current database
   SELECT DATABASE(); # shows which database is selected currently
   
   CREATE TABLE pets (name VARCHAR(20), owner VARCHAR(20), species VARCHAR(20), sex CHAR(1), birth DATE, death DATE); # creates a table 'pets' within the selected db
   SHOW TABLES; # shows tables in the current db
   DESCRIBE pets; # shows table info
   ```
4. Granting a user permissions on MySQL
   ```sql
   GRANT ALL PRIVILEGES ON *.* TO 'new_user'@'localhost';
   ```
   Syntax: [GRANT/REVOKE] [permission] [db_name].[table_name] TO [user]@[db_host] (PRIVILEGES is an optional parameter)<br/>
   Action: It gives/revokes a user on 'db_host' a specific permission on a database 'db_name' table 'table_name'<br/>
   A list of permission:<br/>
    <strong>ALL</strong> – Allow complete access to a specific database. If a database is not specified, then allow complete access to the entirety of MySQL.<br/>
    <strong>CREATE</strong> – Allow a user to create databases and tables.<br/>
    <strong>DELETE</strong> – Allow a user to delete rows from a table.<br/>
    <strong>DROP</strong> – Allow a user to drop databases and tables.<br/>
    <strong>EXECUTE</strong> – Allow a user to execute stored routines.<br/>
    <strong>GRANT OPTION</strong> – Allow a user to grant or remove another user’s privileges.<br/>
    <strong>INSERT</strong> – Allow a user to insert rows from a table.<br/>
    <strong>SELECT</strong> – Allow a user to select data from a database.<br/>
    <strong>SHOW DATABASES</strong> - Allow a user to view a list of all databases.<br/>
    <strong>UPDATE</strong> – Allow a user to update rows in a table.<br/>
5. Grand the changes
   ```sql
   FLUSH PRIVILEGES;
   ```
6. Exit the sql shell
   ```sql
   exit;
   ```
<br/>

## Working with AWS managed RDS

### Pre-requests and environment setup

1. Install aws-cli in your linux instance
   ```sh
   sudo apt update
   sudo apt install awscli -y
   ```
2. Configure aws IAM user credentials assuming you created an IAM user and granted RDS access permission ([reference](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html#id_users_create_console))
   ```sh
   aws configure
   ```
   <img src="https://i.imgur.com/DPpag3q.jpg"></img>
   Enter access key id and secret key, region where your RDS instance will be located, output format as json.<br/>

### Create a RDS instance using aws cli

   ```sh
   aws rds create-db-instance --engine mysql --engine-version 8.0.20 --db-instance-identifier testmysqldbinstance --allocated-storage 20 --db-instance-class db.t2.micro --master-username admin --master-user-password Adminpassword1! --backup-retention-period 0 --storage-type standard --port 3306 --publicly-accessible
   ```
   For the full arguments reference, please visit [here](https://docs.aws.amazon.com/cli/latest/reference/rds/create-db-instance.html?highlight=performance%20insights).

### Working with MySQL database in RDS instances

1. Connecting to an RDS instance from linux shell
   ```sh
   mysql -h testmysqldbinstance.cj90nrslvzqi.us-west-2.rds.amazonaws.com -P 3306 -u admin -p
   ```
   To connect RDS instance from a linux server or from a local with the above command, we will need to invoke a permission to access the RDS instace to this source ip address.<br/>
   We do this in AWS security group configuration for the security group attached to the RDS instance.
2. Working with databases, tables within the RDS instance.<br/>
   Above command will let us land on MySQL shell and we will be able to do sql queries to work with databases and tables there.<br/>
   This is the same as what we covered above for on-premise MySQL server.<br/>

Lets try out!
