from apscheduler.schedulers.background import BackgroundScheduler
from myapp.tasks import update_latest_stock_data, train_linear_regression_model
from datetime import datetime
import logging

def start():
    scheduler = BackgroundScheduler()
    date_string = '2024-10-19 09:56:00'
    run_date = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
    scheduler.add_job(update_latest_stock_data, 'cron', hour=0, minute=0) # run every day at midnight
    scheduler.add_job(train_linear_regression_model, 'date', run_date=run_date) # run every day at 1 am
    scheduler.start()
    logging.info("Scheduler started")
