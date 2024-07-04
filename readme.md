# MySQL Replica Status Check for Icinga2

This Python script checks the status of a MySQL replica. It includes the script into an Icinga2 monitoring system through a CheckCommand definition and a service definition.

## Requirements

The script requires Python 3 and the mysql-connector-python package.

## Using the Script

The script can be run from the command line with the following options:

```shell
python3 check_mysql_replica_status.py --host hostname --port portnumber --username user --password pass --use_ssl --warning_delay 10 --critical_delay 30
```

Replace `hostname`, `portnumber`, `user` and `pass` with your MySQL server's details.

## Icinga2 Command Definition

Add the following command definition to your Icinga2 configuration. This could be added to '/etc/icinga2/conf.d/commands.conf', for example.

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

Add the following service definition to use the new command. It could be added to '/etc/icinga2/conf.d/services.conf', for instance.

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

In this example, we apply the service to the specific host "example-mysql-server.com". Modify the line `assign where host.name == "example-mysql-server.com"` in the service object to specify the hosts on which you want to apply this check.

Don't forget to reload or restart Icinga2 after making these changes.