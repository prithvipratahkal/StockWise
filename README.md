# StockWise

This project aims to develop a Django-based backend system for financial data analysis, with a focus on API integration, database management, and basic financial backtesting. The system will fetch daily stock data from Alpha Vantage and store it in a PostgreSQL database. With this historical data, users can test simple investment strategies to see how their decisions would have performed in the past. Additionally, the system integrates a pre-trained machine learning model to predict future stock prices, giving users both a look back at the past and a glimpse into potential future trends.

The goal is to create a straightforward, user-friendly system that focuses on three key areas:

- Building a robust Django application for API data handling.
- Providing a basic tool for backtesting investment strategies.
- Offering stock price predictions using an existing machine learning model.

## Deliverables achieved
1. Fetch Financial Data
   - I am able to get the data related to the stock symbol and store the data in the postgresql database.
   - Installed timescale plugin for postgres as the data is timeseries and it would be easier on the database to do time queries.
   - Implemented a one time backfill script that has to be run for the environment setup which fetches all the stock data from past 2 years and write it to the stock data table.
   - Implemented a daily cron job that fetches the latest stock data of AAPL from the alphavantage and stores it in the db. This ensures that the data is always up to date on a daily basis
2. Backtesting Module
   - Implemented a new rest api endpoint at '/api/backtest' which takes the parameters such as investing_amount, buy_period, sell_period as mentioned in the requirement document.
   - This API queries the timeseries database and gets the required metrics for us such as moving average for every day since the past 2 years.
   - Implemented a core business logic to use the above metrics and the parameters provided by the user to calculate the total profit and list of events that could have happened with this strategy mentioned in the requirement document.
   - Added necessary test cases to test this endpoint thoroughly ensuring various scenarios are well tested.
3. Machine Learning Integration
   - Since the ML part of the project is irrelavant to this project setup, I have chosen to train the most basic linear regression model without worrying about the accuracy.
   - Created a background task using the Django framework which will run the task every day at 1AM which is right after fetching the latest stock data. This task will retrain the model and generate a new `.pkl` file based on the newly available data.
   - Implemented a new rest api endpoint which will trigger the predictions of the stock data for the next 30 days and includes that in the reponse of the API.
4. Report Generation
   - Implemented a new api endpoint which generates a HTTP response that includes the visualization of how the last 30 days of stock price and next 30 days of predicted data alongside.
   - Generated the reports using the Matplotlib.
5. Deployment
   - Implemented docker files which are required to dockerise the application and deploy it on any container environment.
   - Due to time constraint, it was not possible to move forward with deploying the code on AWS, setting up CI/CD pipelines.
   - Including the detailed explanation on how to build, start, run and test the application and its endpoints.

## Installation

To set up the project locally, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone git@github.com:prithvipratahkal/Blockhouse-project.git
   cd Blockhouse
   ```

2. **Create and activate a virtual environment:**

   It's important to use a virtual environment to keep dependencies isolated.

   For Unix/macOS:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   For Windows:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install the required dependencies:**

   Once the virtual environment is activated, install the necessary libraries listed in `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database:**

   If needed, migrate the database to set up the required tables:

   ```bash
   python manage.py migrate
   ```

5. **Run the project:**

   After completing the setup, you can run the Django development server:

   ```bash
   python manage.py runserver
   ```

## Setting up PostgreSQL in Docker

Note: Due to time constraints, I was not able to setup PostgreSQL in AWS, so I have done that locally using docker.

To set up a PostgreSQL instance using Docker, follow these steps:

1. **Run PostgreSQL in Docker**:
   
   Run the following command to start PostgreSQL and expose port 5432:

   ```bash
   docker run --name stock-closing-data -e POSTGRES_PASSWORD=<password> -p 5432:5432 -d postgres
   ```

2. **Connect to PostgreSQL and create a database**:

   After starting the container, connect to PostgreSQL using the following command:

   ```bash
   docker exec -it stock-closing-data psql -U postgres
   ```

   Once connected, create the database:
 
   ```sql
   CREATE DATABASE stock_closing_data;
   ```

Now you have a PostgreSQL or TimescaleDB instance running in Docker with a database named `stock_closing_data`.



## Database Schema for Stock Data

This section describes the schema used for storing daily stock data for Apple Inc. (AAPL) in a PostgreSQL database:

- **time**: A timestamp field that serves as the primary key for each record. It stores the date and time for when the stock data was recorded, mapped to PostgreSQL’s `TIMESTAMPTZ` type to handle time zones.
  
- **open_price**: A decimal field that captures the stock's opening price on the recorded day. This field is mapped to a `DECIMAL` type in PostgreSQL to ensure accuracy for financial data.
  
- **close_price**: A decimal field for the stock's closing price at the end of the day, also stored as a `DECIMAL` type.

- **high_price**: A decimal field representing the highest price the stock reached during the day, stored as `DECIMAL`.

- **low_price**: A decimal field representing the lowest price of the stock during the day, stored as `DECIMAL`.

- **volume**: A decimal field capturing the total trading volume for the stock on the recorded day. 

The schema is structured to ensure precise handling of financial data, and it is optimized for querying stock price trends and trading volumes over time. The table is named `aapl_stock_data` in the PostgreSQL database.



## API Endpoints: 


### API Endpoint: `/api/backtest/`

This API endpoint allows users to simulate a simple trading strategy by backtesting historical stock data. The user provides specific parameters to guide the strategy, and the system uses historical data to calculate potential profit or loss based on those rules.

#### HTTP Method: `GET`

#### Query Parameters:
- **investing_amount** (required): The amount of money the user is investing in the stock (e.g., $1000). This parameter should be a positive numeric value representing the initial capital.
- **buy_period** (required): The moving average period (e.g., 50 days) used to determine when to buy the stock. The strategy will trigger a buy when the stock price dips below this average.
- **sell_period** (required): The moving average period (e.g., 200 days) used to determine when to sell the stock. The strategy will trigger a sell when the stock price rises above this average.

#### Functionality:
1. **Validate Input Parameters**: 
   - The API first checks whether the required query parameters (`investing_amount`, `buy_period`, and `sell_period`) are provided and are valid numeric values.
   - If any of these parameters are missing or invalid, the API returns a 400 Bad Request response with appropriate error messages.

2. **Fetch Historical Stock Data**:
   - The API retrieves historical stock price data for Apple Inc. (AAPL) from the database. This data includes close prices, open prices, and the relevant moving averages for each day.

3. **Simulate Trading Strategy**:
   - The backtesting logic simulates a trading strategy based on the user-provided buy and sell periods. The basic strategy is as follows:
     - Buy stock when the price falls below the buy period's moving average.
     - Sell stock when the price exceeds the sell period's moving average.
   - The system tracks when trades are made and calculates the profit or loss for each trade.

4. **Calculate Profit**:
   - After completing the simulation, the API calculates the overall profit (or loss) by comparing the final amount of money after all trades to the initial investing amount.

5. **Return Backtest Results**:
   - The API returns a JSON response that includes:
     - The total profit or loss from the backtest.

#### Response:
- **Status Code**: `200 OK`
- **Response Body**:
  - `profit`: The net profit or loss from the backtest.

#### Example Response:
```json
{
  "profit": 1200,
}
```

#### Workflow:
1. The user sends a GET request to `/api/backtest/` with the required query parameters (`investing_amount`, `buy_period`, and `sell_period`).
2. The API validates the inputs and performs the backtest using historical stock data.
3. The system calculates the profit or loss and returns a detailed summary of the trades that occurred during the backtest.


---

### API Endpoint: `/api/predict/`

This API endpoint provides predictions for future stock prices based on a pre-trained machine learning model. It forecasts the stock prices for the next 30 days using a linear regression model trained on historical data.

#### HTTP Method: `GET`

#### Functionality:
1. **Load Pre-trained Model**:
   - The API loads a pre-trained linear regression model from a file, which has been trained on historical stock price data. This model is used to predict the future stock prices.

2. **Fetch Historical Stock Data**:
   - The API retrieves the latest stock data from the database. This data includes the most recent close prices for the stock, which are used as input for the model.

3. **Prepare Data for Prediction**:
   - The API processes the historical stock data and reshapes it as required by the machine learning model. The last 30 days of stock prices are used as input to predict future prices.

4. **Generate Predictions**:
   - The linear regression model predicts stock prices for the next 30 days based on the input data.
   - The predicted stock prices are generated for each day over the next 30-day period.

5. **Return Predictions**:
   - The API returns a JSON response that includes:
     - The stock symbol (e.g., AAPL).
     - A list of predicted stock prices for the next 30 days, along with the corresponding dates.

#### Response:
- **Status Code**: `200 OK`
- **Response Body**:
  - `symbol`: The stock symbol for which predictions are made (e.g., AAPL).
  - `predictions`: A list of predicted stock prices for the next 30 days, along with the dates.

#### Example Response:
```json
{
  "symbol": "AAPL",
  "predictions": [
    {
            "date": "2024-10-19",
            "predicted_price": 168.79841595935096
        },
        {
            "date": "2024-10-20",
            "predicted_price": 168.56038644677184
        },
  ]
}
```

#### Workflow:
1. The user sends a GET request to `/api/predict/`.
2. The API retrieves the latest stock data and prepares it for the pre-trained model.
3. The model predicts the stock prices for the next 30 days, and the API returns these predictions in a structured JSON format.



### Public API Endpoint: `/api/prediction/report/`

This API generates a visual report comparing actual stock prices for the last 30 days with predicted prices for the next 30 days using a pre-trained linear regression model. The result is returned as a PNG image.

#### HTTP Method: `GET`

#### Functionality:
This endpoint provides users with a comprehensive visual report that includes both historical and predicted stock prices. The report includes the following steps:
1. **Load Pre-trained Model**:
   The API starts by loading a pre-trained linear regression model from a file to make stock price predictions.

2. **Fetch Latest Stock Data**:
   The API retrieves the most recent stock data from the database, including close prices and their corresponding timestamps. This data is used for both making predictions and plotting actual historical prices.

3. **Prepare Input Data for Prediction**:
   The API processes the stock data and prepares the last 30 days of close prices as input to the linear regression model.

4. **Predict Stock Prices for the Next 30 Days**:
   Using the pre-trained model, the API predicts the stock prices for the next 30 days based on the most recent historical data.

5. **Generate Prediction Dates**:
   The API generates dates for the next 30 days to correspond with the predicted stock prices.

6. **Plot the Actual and Predicted Prices**:
   - **Actual Prices**: Plotted for the last 30 days, shown in blue with circular markers.
   - **Predicted Prices**: Plotted for the upcoming 30 days, shown in green with dashed lines and cross markers.
   The plot provides a visual comparison between historical and predicted stock prices.

7. **Save Plot and Return as PNG**:
   The API generates a plot with labeled axes, a title, and a legend. The plot is then saved as a PNG image and returned as an HTTP response, allowing the user to view the visual report directly in their browser or download it.

#### Response:
- **Status Code**: `200 OK`
- **Content Type**: `image/png`
- The response contains the generated plot as an inline image.

#### Example Workflow:
1. The user sends a `GET` request to `/api/prediction/report/`.
2. The API retrieves the most recent 30 days of actual stock data from the database.
3. It applies the pre-trained model to predict stock prices for the next 30 days.
4. A visual report is generated, comparing the actual stock prices (last 30 days) and predicted stock prices (next 30 days).
5. The user receives a PNG image with a well-labeled plot, including:
   - Actual stock prices shown as a blue line with markers.
   - Predicted stock prices shown as a green dashed line with cross markers.
6. The plot helps users visualize the predicted trends in stock prices and compare them with recent historical data.

#### Description of Visual Plot:
- **X-Axis**: Represents the dates (both historical and predicted).
- **Y-Axis**: Represents the stock price in USD.
- **Actual Prices**: Displayed with a solid blue line for the last 30 days of stock data, using circular markers for each data point.
- **Predicted Prices**: Displayed with a dashed green line for the next 30 days, using cross markers to indicate predictions.
- **Title**: "Actual vs Predicted Stock Prices".
- **Legend**: Helps differentiate between actual and predicted prices.
- **Formatting**: The plot uses a clean format with rotated dates on the X-axis for better readability.

#### Example of the API Output (visualized):
When you call this endpoint, you’ll receive a visual comparison of how the stock has performed in the last 30 days and the predicted prices for the next 30 days, based on the model’s analysis.



## Backfill Stock Data on Server Initialization

The script(scripts/backfill_two_years_data.py) runs during the server initialization process and is designed to backfill stock data for the past two years into the database. It fetches historical stock data from the Alpha Vantage API and stores it in a PostgreSQL database using the `pg8000` driver. The script ensures that all data starting from a specific date (in this case, January 1, 2022) is fetched and saved into the database.

#### Functionality Overview

1. **Fetch Stock Data from Alpha Vantage API**:
   - The script interacts with the Alpha Vantage API to retrieve historical stock data for a specific symbol (AAPL in this case).
   - It uses the `TIME_SERIES_DAILY` function to get daily stock prices including the open, close, high, low, and volume data.
   - API requests are parameterized with the API key stored in environment variables for security.
   - The response from the API is parsed to extract the relevant stock data.

2. **Database Connection**:
   - The script establishes a connection to a PostgreSQL database using the `pg8000` library.
   - The database credentials, including the username, password, host, port, and database name, are retrieved from environment variables.
   - Once the connection is established, a cursor is created to execute SQL queries.

3. **Backfill Logic**:
   - The script iterates over the historical stock data and filters only the records from `2022-01-01` onwards.
   - It prepares an SQL `INSERT` query to store the stock data into the database.
   - For each valid date, it extracts the stock prices (open, close, high, low) and volume, and inserts the data into the `aapl_stock_data` table.
   - If any errors occur during data insertion, they are logged for debugging purposes.

4. **Data Commit and Cleanup**:
   - After all data has been inserted, the script commits the transaction to ensure that the changes are saved in the database.
   - Finally, the database cursor and connection are closed to release resources.

#### Key Components:

- **`get_stock_data()`**:
   - Fetches daily stock data for AAPL from the Alpha Vantage API.
   - Uses environment variables for the API key to ensure security.
   - Handles API responses and logs the status.

- **`get_db_connection()`**:
   - Establishes a connection to the PostgreSQL database using credentials from environment variables.
   - Logs the connection status and user details (excluding sensitive information).

- **`backfill_two_years_data()`**:
   - Handles the backfill process by:
     - Fetching stock data from the Alpha Vantage API.
     - Filtering data to only include records from `2022-01-01` onwards.
     - Preparing SQL queries to insert the data into the `aapl_stock_data` table.
     - Committing the transaction and logging any errors during the process.

#### Usage:

This script is executed when the server is initialized to ensure that the stock data table is pre-populated with the past two years of data.

```bash
# Command to run the script
python backfill_stock_data.py
```

Ensure that the following environment variables are set before running the script:

- `ALPHA_VANTAGE_API_KEY`: The API key for accessing Alpha Vantage.
- `POSTGRES_USER`: The username for PostgreSQL.
- `POSTGRES_PASSWORD`: The password for PostgreSQL.
- `POSTGRES_HOST`: The PostgreSQL host address.
- `POSTGRES_PORT`: The PostgreSQL port (default is 5432).
- `POSTGRES_DB`: The name of the database to connect to.

#### Example Log Output:

```
INFO:root:Fetching data from Alpha Vantage API
INFO:root:Alpha Vantage API response status code: 200
INFO:root:Establishing database connection
INFO:root:Database connection established
INFO:root:Inserting stock data for date: 2022-01-02, open_price: 150.25, close_price: 155.00, high_price: 157.00, low_price: 149.50, volume: 100000
INFO:root:Stock data inserted successfully
INFO:root:PostgreSQL connection closed.
```

This logging helps track the progress of data backfilling and provides useful information for debugging in case of any issues.



### Background Task: Daily Stock Data Update and Model Retraining

This project includes two automatic tasks that run every day to ensure stock data is always up-to-date and the stock price prediction model is regularly retrained. These tasks run in the background and are scheduled to execute at specific times.

#### Daily Tasks:

1. **Stock Data Fetching (Runs at Midnight)**:
   - Every day at **midnight (00:00)**, the system fetches the latest stock data for Apple Inc. (AAPL) from the Alpha Vantage API.
   - The fetched data includes details like open price, close price, high price, low price, and volume for the day.
   - If there are any missing entries from previous days (due to server downtime or other issues), the system backfills the data for those missing days.
   - This ensures that the database is always complete with no missing stock data.

2. **Model Retraining (Runs at 1 AM)**:
   - Every day at **1:00 AM**, the system retrains the stock price prediction model using the most up-to-date data.
   - The model is a **Linear Regression** model, which predicts future stock prices based on the previous day’s closing price.
   - After training, the model is saved as a `.pkl` file so it can be used later for making predictions.

#### How the Tasks Work:

1. **Stock Data Update Task**:
   - The `update_latest_stock_data` function is responsible for fetching and updating the stock data.
   - It runs every day at midnight and collects the latest stock prices from the Alpha Vantage API.
   - If any data is missing from previous days, it automatically fills those gaps.

2. **Model Retraining Task**:
   - The `train_linear_regression_model` function is scheduled to run every day at 1 AM.
   - This task gathers all the stock data stored in the database and prepares it for model training.
   - The model is trained using the previous day’s stock price to predict the next day’s price.
   - After training, the model is saved in a `.pkl` file, which can be loaded whenever stock price predictions are needed.

#### Code Breakdown:

```python
def train_linear_regression_model():
    # Get all the stock data
    all_stock_data = AaplStockData.objects.all()
    data_df = pd.DataFrame(list(all_stock_data.values('time', 'close_price')))
    
    # Preprocess the data
    data_df['previous_day'] = data_df['close_price'].shift(1)
    data_df.dropna(inplace=True)
    
    # Define features (X) and target (Y)
    X = data_df[['previous_day']].values
    Y = data_df['close_price'].values
    
    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, shuffle=False)

    # Initialize and train the Linear Regression model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Save the model to a file
    joblib.dump(model, get_linear_regression_model_filepath())
```

#### Scheduling the Tasks:

The scheduling is handled using the `apscheduler` library. Here’s how the scheduler is set up:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from myapp.tasks import update_latest_stock_data, train_linear_regression_model
from datetime import datetime
import logging

def start():
    scheduler = BackgroundScheduler()
    
    # Schedule the daily task to fetch stock data at midnight
    scheduler.add_job(update_latest_stock_data, 'cron', hour=0, minute=0) 
    
    # Schedule the model retraining task to run at 1 AM
    scheduler.add_job(train_linear_regression_model, 'cron', hour=1, minute=0)
    
    scheduler.start()
    logging.info("Scheduler started")
```

#### Summary:

- **Stock Data Update Task**: Runs every day at midnight to fetch and backfill stock data.
- **Model Retraining Task**: Runs every day at 1 AM to retrain the stock price prediction model.
- Both tasks are automated and require no manual intervention after being set up.

#### Logging Example:

```
INFO:root:Scheduler started
INFO:root:Stock data update task triggered for 2024-10-20
INFO:root:Stock data updated successfully for 2024-10-20
INFO:root:Linear regression model training started at 2024-10-20 01:00
INFO:root:Model training completed successfully
```

By automating these tasks, the system ensures that stock data is always up-to-date and the model is retrained daily to provide more accurate predictions.

