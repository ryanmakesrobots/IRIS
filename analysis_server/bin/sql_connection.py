import pymysql
import config

def create_connection():
    try:
        connection = pymysql.connect(config.sqlserverip, config.sqlusername, config.sqlpassword, config.sqlserverdb)
        c = connection.cursor()
        return connection, c
    except Exception as e:
        print(f'no connection made: {e}')