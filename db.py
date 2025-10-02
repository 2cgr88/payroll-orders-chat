import pymysql
from config import Config

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = pymysql.connect(
            host=Config.DB_CONFIG['host'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password'],
            database=Config.DB_CONFIG['database'],
            port=Config.DB_CONFIG['port'],
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except pymysql.Error as e:
        print(f"Database connection error: {e}")
        raise

def execute_query(query, params=None, fetch_one=False):
    """Execute a query and return results"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            if fetch_one:
                return cursor.fetchone()
            return cursor.fetchall()
    finally:
        connection.close()

def execute_update(query, params=None):
    """Execute an INSERT, UPDATE, or DELETE query"""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            connection.commit()
            return cursor.rowcount
    finally:
        connection.close()
