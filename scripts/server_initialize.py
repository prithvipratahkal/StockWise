import requests
import pandas as pd
import pg8000
from datetime import datetime, timedelta

def import_data():
    API_KEY = '4QWSOQKY36QC47K9'
    url = 'https://www.alphavantage.co/query'

    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': 'AAPl',
        'outputsize': 'full',
        'apikey': API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        create_table()
        data = response.json()

        time_series = data.get('Time Series (Daily)', {})
        df = pd.DataFrame.from_dict(time_series, orient='index')
            

        # first_10_entries = df.head(10)
        # print("First 10 entries:")
        # print(first_10_entries)

def create_table():
    try:
        connection = pg8000.connect(
            user="postgres",
            password="mypassword",
            host="localhost",
            port=5432,
            database="stock_closing_data"
        )

        print("connection established")
        cursor = connection.cursor()

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS aapl_stock_data (
            timestamp TIMESTAMPTZ PRIMARY KEY,
            open_price DECIMAL,
            close_price DECIMAL,
            high_price DECIMALN,
            low_price DECIMAL,
            volume DECIMAL
        );
        '''

        cursor.execute(create_table_query)
        connection.commit()

        print("Table 'aapl_stock_data' created successfully.")

        create_hypertable_query = '''
            SELECT create_hypertable('aapl_stock_data', 'timestamp');
        '''

        cursor.execute(create_hypertable_query)
        connection.commit()

        print("Hypertable created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the cursor and connection
        if cursor is not None:
            cursor.close()
        if connection is not None:
            connection.close()
        print("PostgreSQL connection closed.")

if __name__ == '__main__': 
    create_table()



