import os
import platform
import socket
import getpass
from datetime import datetime

try:
    import mysql.connector
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

def log_scan(cnx, directory_path):
    hostname = platform.node()
    ip_address = socket.gethostbyname(hostname)
    user_name = getpass.getuser()
    date_time_issued = datetime.now()




    cursor = cnx.cursor()
    try:
        add_log = ("INSERT INTO scan_log "
                   "(directory_path, host_name, host_ip, user_name, date_time_issued) "
                   "VALUES (%s, %s, %s, %s, %s)")
        data_log = (directory_path, hostname, ip_address, user_name, date_time_issued)
        cursor.execute(add_log, data_log)
        cnx.commit()
    except mysql.connector.Error as err:
        print(f"Error logging scan: {err}")
    finally:
        cursor.close()