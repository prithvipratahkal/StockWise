import pg8000
import requests

def connect_to_db():
    try:
        connection = pg8000.connect(
            user="postgres",
            password="mypassword",
            host="localhost",
            port=5432,
            database="stock_closing_data"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT version();")

        version = cursor.fetchone()

        print(f"PostgreSQL version: {version[0]}")

        # Close the cursor and connection
        cursor.close()
        connection.close()
        print("Connection closed.")
    except Exception as e:
        print(f"Error: {e}")

def import_daily_stock_data():
    API_KEY = '4QWSOQKY36QC47K9'
    url = 'https://www.alphavantage.co/query'

    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': 'AAPl',
        'outputsize': 'compact',
        'apikey': API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()

        time_series = data.get("Time Series (Daily)", {})

        # extract the current date's data
        date = next(iter(time_series))
        first_entry_data = time_series[date]

        print(f"Date: {date}")
        print(f"Data: {first_entry_data}")

        # Extract the required fields
        open_price = float(first_entry_data.get('1. open', 0))
        high_price = float(first_entry_data.get('2. high', 0))
        low_price = float(first_entry_data.get('3. low', 0))
        close_price = float(first_entry_data.get('4. close', 0))
        volume = int(first_entry_data.get('5. volume', 0))

        insert_query = '''
            INSERT INTO aapl_stock_data (timestamp, open_price, close_price, high_price, low_price, volume)
            VALUES (%s, %s, %s, %s, %s, %s);
        '''

        cursor.execute(insert_query, (
            date,
            open_price,
            close_price,
            high_price,
            low_price,
            volume
        ))
        connection.commit()

        print("Data inserted successfully.")


if __name__ == '__main__': 
   connect_to_db()
   import_daily_stock_data()