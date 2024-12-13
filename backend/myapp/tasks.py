from datetime import datetime, timezone
import logging
from myapp.models import AaplStockData
from myapp.apps import get_linear_regression_model_filepath
import os
import requests
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib


def update_latest_stock_data():
    logging.info(f"Updating latest stock data running at {datetime.now()}")

    # get the latest stock data time
    latest_stock_data = AaplStockData.objects.latest('time')
    latest_stock_time = latest_stock_data.time

    # get the latest stock data
    data = get_stock_data(latest_stock_time)
    if data is None:
        logging.info("No new data available")
        return
    
    stock_data_list = []
    for date, values in data.items():
        stock_data_list.append(
            AaplStockData(
                time=date,
                open_price=values.get('1. open'),
                close_price=values.get('4. close'),
                high_price=values.get('2. high'),
                low_price=values.get('3. low'),
                volume=values.get('5. volume')
            )
        )
    
    # sort the data by time
    stock_data_list.sort(key=lambda x: x.time)

    # iterate over the data and insert it into the database
    for stock_data in stock_data_list:
        logging.info(f"Inserting data for time: {stock_data.time}")
        stock_data.save()

    
def get_stock_data(since_time: datetime):
    logging.info("Fetching data from Alpha vantage api")

    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    url = 'https://www.alphavantage.co/query'

    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': 'AAPL',
        'outputsize': 'compact',
        'apikey': api_key
    }

    response = requests.get(url, params=params)
    logging.info(f"Alpha vantage api response status code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        
        daily_data = data.get('Time Series (Daily)', {})
        data_since_given_time = {}
        for time, stock_data in daily_data.items():
            time = datetime.strptime(time, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if time > since_time:
                data_since_given_time[time] = stock_data
        
        return data_since_given_time

    logging.info(f'Error fetching data from Alpha vantage api. Response status code: {response.status_code}')
    return None

def train_linear_regression_model():
    # get all the stock data
    all_stock_data = AaplStockData.objects.all()
    data_df = pd.DataFrame(list(all_stock_data.values('time', 'close_price')))
    
    # preprocess the data
    data_df['previous_day'] = data_df['close_price'].shift(1)
    data_df.dropna(inplace=True)
    
    # define features (X) and target (Y)
    X = data_df[['previous_day']].values
    Y = data_df['close_price'].values
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, shuffle=False)

    # Initialize and train the Linear Regression model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    joblib.dump(model, get_linear_regression_model_filepath())
