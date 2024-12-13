from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from myapp.models import AaplStockData
from myapp.apps import get_linear_regression_model_filepath
import joblib
import pandas as pd
from datetime import timedelta
from django.http import JsonResponse, HttpResponse
import matplotlib.pyplot as plt
import io

# Set the Matplotlib backend to 'Agg'
import matplotlib
matplotlib.use('Agg')

# Create your views here.

@api_view(['GET'])
def back_test(request):
    """
    This function is used to back test the trading strategy
    """
    investing_amount = request.query_params.get('investing_amount', None)
    sell_period = request.query_params.get('sell_period', None)
    buy_period = request.query_params.get('buy_period', None)
    
    # if any of the parameters are missing, return a bad request response
    if investing_amount is None or sell_period is None or buy_period is None:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # if any of the parameters are not a number, return a bad request response
    if not investing_amount.isnumeric() or not sell_period.isnumeric() or not buy_period.isnumeric():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # if any of the selling or buying prices are less than or equal to zero, return a bad request response
    if int(sell_period) <= 0 or int(buy_period) <= 0:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    # if the investment amount is less than 0, return a bad request
    if int(investing_amount) < 0:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    stock_data = AaplStockData.get_data_with_moving_average(int(sell_period), int(buy_period))
    
    # sort the stock data by time
    stock_data = sorted(stock_data, key=lambda x: x.time)
    
    # iterate over the stock data and calculate the profit
    profit = 0
    buy = True
    amount_remaining = int(investing_amount)
    stocks_held = 0
    events = []
    for stock in stock_data:
        if int(investing_amount) == 0:
            break

        if buy and stock.open_price < stock.buying_moving_average:
            stocks_held = int(amount_remaining) // stock.open_price
            amount_remaining = int(amount_remaining) % stock.open_price
            events.append(f"Bought {stocks_held} stocks on {stock.time} for {stock.open_price}")
            buy = False
        elif not buy and stock.close_price > stock.selling_moving_average:
            amount_remaining += int(stocks_held * stock.close_price)
            events.append(f"Sold {stocks_held} stocks on {stock.time} for {stock.close_price}")
            stocks_held = 0
            buy = True

    if stocks_held > 0:
        # sell the stocks at the last price
        amount_remaining += int(stocks_held * stock_data[-1].close_price)
        events.append(f"Sold {stocks_held} stocks on {stock_data[-1].time} for {stock_data[-1].close_price}")
        
    profit = amount_remaining - int(investing_amount)
    response_data = {
        'profit': profit,
        'events': events
    }    

    return Response(status=status.HTTP_200_OK, data=response_data)

@api_view(['GET'])
def predict_data(request):
    """
    This function is used to predict the stock data for the next 30 days
    """

    # load the linear regression model
    model = joblib.load(get_linear_regression_model_filepath())

    # get the latest stock data
    latest_stock_data = AaplStockData.objects.all().order_by('-time').values('close_price', 'time')
    data_df = pd.DataFrame(latest_stock_data)

    # prepare the data for the model
    X_input = data_df['close_price'].values.reshape(-1, 1)
    
    # predict the stock data
    predictions = model.predict(X_input[-30:])
    
    # generate data for the next 30 days
    last_date = data_df['time'].max()
    prediction_dates = [last_date + timedelta(days=i) for i in range(1, 31)]
    
    prediction_response = {
        'symbol': 'AAPL',
        'predictions': [{'date': date.strftime('%Y-%m-%d'), 'predicted_price': price} for date, price in zip(prediction_dates, predictions)]
    }

    return JsonResponse(prediction_response)

@api_view(['GET'])
def get_report_for_prediction(request):
    """
    This function is used to get the report for the prediction
    """
    
    model = joblib.load(get_linear_regression_model_filepath())
    
    # Get the latest stock data
    latest_stock_data = AaplStockData.objects.all().order_by('-time').values('close_price', 'time')
    data_df = pd.DataFrame(list(latest_stock_data))

    # Prepare the data for the model
    X_input = data_df['close_price'].values.reshape(-1, 1)

    # Predict the stock data for the last 30 days
    predictions = model.predict(X_input[-30:])

    # Generate dates for the next 30 days
    last_date = data_df['time'].max()
    prediction_dates = [last_date + timedelta(days=i) for i in range(1, 31)]

    # Filter the last 30 days of actual data
    actual_data = data_df[:30]

    # Prepare the plot
    plt.figure(figsize=(12, 6))

    # Plot actual prices for the last 30 days
    plt.plot(actual_data['time'], actual_data['close_price'], label='Actual Price', color='blue', marker='o')

    # Plot predicted prices for the next 30 days
    plt.plot(prediction_dates, predictions, label='Predicted Price', color='green', linestyle='--', marker='x')

    # Improve x-axis formatting
    plt.gcf().autofmt_xdate()

    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title('Actual vs Predicted Stock Prices')
    plt.legend()

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # Return the image as an HTTP response
    response = HttpResponse(buf, content_type='image/png')
    response['Content-Disposition'] = 'inline; filename="stock_predictions.png"'

    return response
    