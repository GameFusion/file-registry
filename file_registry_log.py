# Andreas Carlen
# 04/01/2024

import registry_database

cnx = registry_database.get_database_connection()

def read_and_print_log(cnx):
    cursor = cnx.cursor()

    try:
        query = "SELECT * FROM scan_log"
        cursor.execute(query)

        # Fetch all the rows in the result set
        rows = cursor.fetchall()

        # Print the log entries
        for row in rows:
            print(f"Directory Path: {row[1]}, Host Name: {row[2]}, Host IP: {row[3]}, User Name: {row[4]}, Date and Time Issued: {row[5]}")
            #print("id", row[0])
            #print("path", row[1])
            #print("host", row[2])
            #print("ip", row[3])
            #print("user ", row[4])
            #print("Date ", row[5])
        #print(rows)
    except mysql.connector.Error as err:
        print(f"Error reading log: {err}")

    finally:
        cursor.close()

read_and_print_log(cnx)
