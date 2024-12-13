from django.urls import path
from .views import back_test, predict_data, get_report_for_prediction

urlpatterns = [
    path('api/backtest/', back_test, name='back_test'),
    path('api/predict-data', predict_data, name='predict_data'),
    path('api/reports/prediction-data', get_report_for_prediction, name='get_report_for_prediction'),
]