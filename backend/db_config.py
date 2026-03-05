import mysql.connector

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="va@family",
            database="petcare"
        )
        return connection
    except mysql.connector.Error as err:
        print("Database connection error:", err)
        return None