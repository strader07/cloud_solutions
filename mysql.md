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
