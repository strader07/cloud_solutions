<br />
<p align="center">
  <h3 align="center">Working with MySQL in Linux</h3>
</p>

### Description

Shows how to create and configure mysql server in a linux instance. <br/>
It covers installing mysql server, configuring database and tables in an linux instance itself and accessing cloud managed mysql databases.

## MySQL in AWS EC2 instance (Ubuntu 18.04)

### Pre-configuration

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
   <img src="https://i.imgur.com/SGvS339.jpg"></img>
   
   Press y on this prompt, then choose your password level following instructions.
   
   Give a root password and continue, hit y for 'remove anonymous users?'.
   
   Recommend hitting y for 'Disallow root login remotely?' to protect anyone guessing the root password.
   
   Hit y for 'Remove test database and access to it?' and 'Reload privilege tables now?'.

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
   ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'Followme1!';
   ```
   Note: The password string ('Followme1!' in command) must meet the policies depending on the chosed level of strength in step 4 in setup section.<br/>
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

### Running & Stopping MySQL service

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
