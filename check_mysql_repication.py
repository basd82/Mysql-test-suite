#
#
#  @copyright      Copyright (c) 2024  B.F. van den Dikkenberg All rights reserved.
#  @license        GNU General Public License version 2 or later
#

import argparse
import mysql.connector
import configparser


def check_replication_status(args):
    # Initialize SSL setting
    ssl_disabled = {'disabled': True} if not args.use_ssl else {'ca': '/etc/ssl/certs/ca-certificates.crt',
                                                                'verify_cert': not args.allow_self_signed}

    # Read from configuration file if provided
    config = {}
    if args.options_file:
        config_parser = configparser.ConfigParser()
        config_parser.read(args.options_file)
        config = dict(config_parser['client'])

    # Override with command-line options
    if args.username: config['user'] = args.username
    if args.password: config['password'] = args.password
    if args.host: config['host'] = args.host
    if args.port: config['port'] = args.port
    if args.socket: config['unix_socket'] = args.socket
    config['client_flags'] = [mysql.connector.constants.ClientFlag.SSL]
    config['ssl_disabled'] = ssl_disabled

    response_msg = ""

    try:
        # Establish MySQL connection
        cnx = mysql.connector.connect(**config)

        cursor = cnx.cursor()
        # Execute the query to get the MySQL version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]

        # Depending on version string execute the right query
        if "8.0" in version or "8.4" in version:
            cursor.execute("SHOW REPLICA STATUS")
        else:
            cursor.execute("SHOW SLAVE STATUS")

        # Fetch the status
        status = cursor.fetchone()

        # process status to check the delay, I/O and SQL threads etc.
        if status is not None:
            # maps the status to a dictionary
            status_dict = dict(zip(cursor.column_names, status))

            # Check if the replica IO and SQL threads are running
            io_running = status_dict.get('Replica_IO_Running') or status_dict.get('Slave_IO_Running')
            sql_running = status_dict.get('Replica_SQL_Running') or status_dict.get('Slave_SQL_Running')

            # Retrieve and print the source server
            source_server = status_dict.get('Source_Host') or status_dict.get('Master_Host')

            # Check SSL status
            ssl_allowed = status_dict.get('Source_SSL_Allowed') or "No"

            delay_val = 'Seconds_Behind_Source' if "8.0" in version or "8.4" in version else 'Seconds_Behind_Master'

            if delay_val in status_dict:
                delay = status_dict[delay_val]

                if delay > args.critical_delay:
                    delay_status = "CRITICAL: Replica replication delay is over the critical delay"
                elif delay > args.warning_delay:
                    delay_status = "WARNING: Replica replication delay is over the warning delay"
                else:
                    delay_status = "OK: Replica replication delay is within acceptable thresholds"

                response_msg = f"IO: {io_running}, SQL: {sql_running}, Server: {source_server}, SSL: {ssl_allowed}, Delay: {delay}, {delay_status}"

            else:
                response_msg = "ERROR: Couldn't find 'Seconds_Behind_Master' or 'Seconds_Behind_Source' in the replica or slave status response!"
        else:
            response_msg = "ERROR: No replication status available!"

    except mysql.connector.Error as err:
        response_msg = f"ERROR: Something went wrong: {str(err)}"

    finally:
        # Close cursor and connection
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

    print(response_msg)


def main():
    parser = argparse.ArgumentParser(description='Check MySQL replica status.')
    parser.add_argument('--options_file', type=str,
                        help='Path to mysql client options file containing connection credentials')
    parser.add_argument('--host', type=str, help='Hostname/IP')
    parser.add_argument('--port', type=int, help='MySQL port')
    parser.add_argument('--use_ssl', action='store_true', help='Use SSL connection')
    parser.add_argument('--allow_self_signed', action='store_true', help='Accept self signed certificates')
    parser.add_argument('--socket', type=str, help='Path to local mysqld socket')
    parser.add_argument('--username', type=str, help='MySQL username')
    parser.add_argument('--password', type=str, help='MySQL password')
    parser.add_argument('--warning_delay', type=int, default=10,
                        help='Warning delay of replica replication behind source (in seconds)')
    parser.add_argument('--critical_delay', type=int, default=30,
                        help='Critical delay of replica replication behind source (in seconds)')

    args = parser.parse_args()
    check_replication_status(args)


if __name__ == "__main__":
    main()