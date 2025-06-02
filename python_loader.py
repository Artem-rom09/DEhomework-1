import mysql.connector
from mysql.connector import Error
import pandas as pd
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'), 
    'database': os.getenv('DB_DATABASE', 'my_ad_data'),
    'user': os.getenv('DB_USER', 'me'),
    'password': os.getenv('DB_PASSWORD', 'artem228')
}

CSV_FILES = {
    'advertisers': 'advertisers.csv',
    'users': 'users_normalized.csv',
    'interests': 'interests.csv',
    'campaigns': 'campaigns_normalized.csv',
    'impressions': 'impressions.csv',
    'clicks': 'clicks.csv',
    'userinterests': 'user_interests.csv'
}


LOAD_ORDER = [
    'advertisers',
    'users',
    'interests',
    'campaigns',
    'impressions',
    'clicks',
    'userinterests'
]

def connect_db():
    """Встановлює з'єднання з базою даних MySQL."""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            allow_local_infile=True
        )
        if conn.is_connected():
            print(f"Успішно підключено до бази даних '{DB_CONFIG['database']}'")
            return conn
    except Error as e:
        print(f"Помилка при підключенні до MySQL: {e}")
        return None

def execute_query(connection, query, params=None):
    """Виконує SQL-запит."""
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        return True
    except Error as e:
        print(f"Помилка виконання запиту: {query}\nПомилка: {e}")
        return False
    finally:
        cursor.close()

def load_data_from_csv(connection, table_name, csv_file_path):

    try:
        abs_csv_path = csv_file_path
        if not os.path.exists(abs_csv_path):
            print(abs_csv_path)
            print(f"file not found: {csv_file_path}")
            return False

        print(f"Очищення таблиці '{table_name}'...")
        execute_query(connection, f"SET FOREIGN_KEY_CHECKS = 0;")
        execute_query(connection, f"TRUNCATE TABLE `{table_name}`")
        execute_query(connection, f"SET FOREIGN_KEY_CHECKS = 1;")


        load_query = f"""
        LOAD DATA LOCAL INFILE '{abs_csv_path}'
        INTO TABLE `{table_name}`
        FIELDS TERMINATED BY ','
        ENCLOSED BY '\"'
        LINES TERMINATED BY '\\n'
        IGNORE 1 ROWS;
        """
        print(f"Завантаження даних у таблицю '{table_name}' з '{csv_file_path}'...")
        if execute_query(connection, load_query):
            print(f"Дані успішно завантажено в таблицю '{table_name}'.")
            return True
        else:
            print(f"Не вдалося завантажити дані в таблицю '{table_name}'.")
            return False
    except Exception as e:
        print(f"Загальна помилка при завантаженні '{table_name}': {e}")
        return False


def main():
    conn = connect_db()
    if conn:
        for table_alias in LOAD_ORDER:
            csv_file = CSV_FILES[table_alias]
            table_name = table_alias
            if not load_data_from_csv(conn, table_name, csv_file):
                print(f"Завантаження зупинено через помилку в таблиці '{table_name}'.")
                break
        conn.close()
        print("З'єднання з базою даних закрито.")
    else:
        print("Не вдалося встановити з'єднання з базою даних. Завантаження неможливе.")

if __name__ == '__main__':
    main()
