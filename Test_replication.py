#
#
#  @copyright      Copyright (c) 2024  B.F. van den Dikkenberg All rights reserved.
#  @license        GNU General Public License version 2 or later
#
import argparse
import mysql.connector
import datetime


def test_replication(args):
    value_to_insert = str(datetime.datetime.now())
    status_message = ''

    cnx_master = cnx_slave = cursor_master = cursor_slave = None

    try:
        # Connection configuration
        config = {
            'user': args.username,
            'password': args.password,
            'database': args.database,
            'use_pure': True,
            'ssl_disabled': not args.use_ssl
        }
        if args.use_ssl and args.allow_self_signed:
            config['ssl_verify_cert'] = False

        # Connect to the master
        config['host'] = args.master_host
        cnx_master = mysql.connector.connect(**config)
        cursor_master = cnx_master.cursor()

        # Execute the insertion to the master
        cursor_master.execute(f"INSERT INTO {args.table} (value) VALUES (%s)", (value_to_insert,))
        cnx_master.commit()

        # Now connect to the slave
        config['host'] = args.slave_host
        cnx_slave = mysql.connector.connect(**config)
        cursor_slave = cnx_slave.cursor()

        # Check if the new value has replicated to the slave
        cursor_slave.execute(f"SELECT * FROM {args.table} WHERE value = %s", (value_to_insert,))
        row = cursor_slave.fetchone()

        if row is not None:
            status_message = 'Replication status: OK'
            # Remove the value from the test table on both master and slave
            cursor_master.execute(f"DELETE FROM {args.table} WHERE value = %s", (value_to_insert,))
            cnx_master.commit()
            cursor_slave.execute(f"DELETE FROM {args.table} WHERE value = %s", (value_to_insert,))
            cnx_slave.commit()
        else:
            status_message = 'Replication status: FAIL'
    except mysql.connector.Error as err:
        status_message = 'An error occurred: {}'.format(err)
    finally:
        if cnx_master and cnx_master.is_connected():
            cursor_master.close()
            cnx_master.close()

        if cnx_slave and cnx_slave.is_connected():
            cursor_slave.close()
            cnx_slave.close()

    print(status_message)


def main():
    parser = argparse.ArgumentParser(description='Test MySQL replication.')
    parser.add_argument('--master_host', type=str, help='Master MySQL server host')
    parser.add_argument('--slave_host', type=str, help='Slave MySQL server host')
    parser.add_argument('--username', type=str, help='MySQL username')
    parser.add_argument('--password', type=str, help='MySQL password')
    parser.add_argument('--database', type=str, default='lbtest', help='Database name')
    parser.add_argument('--table', type=str, default='test', help='Table name')
    parser.add_argument('--use_ssl', action='store_true', default=True, help='Use SSL for connection')
    parser.add_argument('--allow_self_signed', action='store_true', help='Accept self-signed certificates')

    args = parser.parse_args()

    test_replication(args)


if __name__ == "__main__":
    main()

