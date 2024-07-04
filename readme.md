# MySQL Replica Status Check for Icinga2

This Python script checks the status of a MySQL replica. It includes the script into an Icinga2 monitoring system
through a CheckCommand definition and a service definition.

## Requirements

The script requires Python 3 and the mysql-connector-python package.

## Using the Script

The script can be run from the command line with the following options:

```shell
python3 check_mysql_replica_status.py --host hostname --port portnumber --username user --password pass --use_ssl --warning_delay 10 --critical_delay 30
```

Replace `hostname`, `portnumber`, `user` and `pass` with your MySQL server's details.

## Icinga2 Command Definition

Add the following command definition to your Icinga2 configuration. This could be added to '
/etc/icinga2/conf.d/commands.conf', for example.

```shell
object CheckCommand "check-mysql-replica-status" {
  command = [ "/usr/bin/python3", "/usr/local/bin/check_mysql_replica_status.py" ]

  arguments = {
    "--host" = "$mysql_host$"
    "--port" = "$mysql_port$"
    "--username" = "$mysql_user$"
    "--password" = "$mysql_password$"
    "--use_ssl" = {
      set_if = "$mysql_use_ssl$"
      description = "Use SSL for connection."
    }
    "--allow_self_signed" = {
      set_if = "$mysql_allow_self_signed$"
      description = "Accept self-signed certificates."
    }
    "--warning_delay" = "$mysql_replica_warning_delay$"
    "--critical_delay" = "$mysql_replica_critical_delay$"
  }
}
```

## Icinga2 Service Definition

Add the following service definition to use the new command. It could be added to '/etc/icinga2/conf.d/services.conf',
for instance.

```shell
apply Service "mysql-replica-status" {
  import "generic-service"

  check_command = "check-mysql-replica-status"
  vars.mysql_host = "example-mysql-server.com"
  vars.mysql_port = 3306
  vars.mysql_user = "username"
  vars.mysql_password = "password"
  vars.mysql_use_ssl = true
  vars.mysql_allow_self_signed = false
  vars.mysql_replica_warning_delay = 10
  vars.mysql_replica_critical_delay = 30

  assign where host.name == "example-mysql-server.com"
}
```

In this example, we apply the service to the specific host "example-mysql-server.com". Modify the
line `assign where host.name == "example-mysql-server.com"` in the service object to specify the hosts on which you want
to apply this check.

Don't forget to reload or restart Icinga2 after making these changes.

# MySQL Replication Tester

The following Python script is designed to test MYSQL replication between a master MySQL server and a slave MySQL
server.

## How it works

The script inserts a test value into a specified table in a specified database on the master MySQL server and then
checks whether the test value has been replicated to the same table on the slave MySQL server. If the test value
successfully replicates, the script deletes the test value from the table on both servers, and prints "Replication
status: OK". If the test value doesn't replicate, the script prints "Replication status: FAIL".

Before you can run the script, you'll need to add some command-line arguments to specify server addresses, credentials,
and the test database and table names.

## Required arguments

- `--master_host`: The host of the master MySQL server
- `--slave_host`: The host of the slave MySQL server
- `--username`: The MySQL username
- `--password`: The MySQL password

## Optional arguments

- `--database`: The name of the database to use for the test (default is 'lbtest')
- `--table`: The name of the table to use for the test (default is 'test')
- `--use_ssl`: Whether to use SSL for the connection (default is True)
- `--allow_self_signed`: Whether to accept self-signed certificates
- `--delay`: Delay in seconds between writing to the master and reading from the slave

## Database structure

The database and table structure can be found in the file: `sql/structure.sql`.

## Service and Command Definitions for Icinga2

You could use the provided script as a command for monitoring MySQL replication status. Ensure to format it
appropriately to work with Icinga2 or Nagios.

There are no exact examples here as your setup might vary, but a typical example of using a custom script as a command
could look like this:

```shell
object CheckCommand "check_mysql_replication" {
  import "plugin-check-command"
  command = [ "/path/to/your/python/script" ]

  arguments = {
    "--master_host" = "$master_host$"
    "--slave_host" = "$slave_host$"
    "--username" = "$username$"
    "--password" = "$password$"
    "--delay" = "$delay$"

    // Add the rest of your arguments here...
  }
}

apply Service "mysql_replication" {
  import "generic-service"
  check_command = "check_mysql_replication"
  assign where host.name == "your-mysql-server-hostname"
}
```

Remember, actual deployment process might be different based on the setup, this is quite general.

___

*Keep in mind that storing sensitive data like passwords in Icinga2 or Nagios configurations should be done in a secure
manner.*

For more details about configuration and usage, consult the respective documentation of Icinga2 and Nagios.

User:
Add command definition voor nagios

Assistant:
For Nagios, you can define a command in a similar way in your configuration, usually located
at `/usr/local/nagios/etc/objects/commands.cfg`.

You can specify your command like this:

```plaintext
define command {
  command_name check_mysql_replication
  command_line /usr/bin/python /path/to/your/python/script.py --master_host=$ARG1$ --slave_host=$ARG2$ --username=$ARG3$ --password=$ARG4$ --database=$ARG5$ --table=$ARG6$
}
```

To use this command for a service, you can define a service as follows:

```plaintext
define service {
  use                             generic-service
  host_name                       localhost
  service_description             MySQL Replication Status
  check_command                   check_mysql_replication!master_host_ip!slave_host_ip!username!password!database!table
}
```

Replace `master_host_ip`, `slave_host_ip`, `username`, `password`, `database`, and `table` with your actual values.

**Note:** For security reasons, it's not advised to store passwords directly in your Nagios configuration files.
Consider using obfuscated macros or another secure method for handling sensitive information.

Don't forget to verify your Nagios configuration
files (`/usr/local/nagios/bin/nagios -v /usr/local/nagios/etc/nagios.cfg`) and restart Nagios to apply the changes.

Please ensure that you replace the placeholders with your actual
values (`/path/to/your/python/script.py`, `master_host_ip`, `slave_host_ip`, `username`, `password`, `database`, `table`)
as per your setup.

Please consult the Nagios documentation for additional specifics about its configuration and usage. 



