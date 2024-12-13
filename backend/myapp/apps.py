from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    linearRegressionModelFilepath="myapp/linear_regression_model.pkl"
    
    def ready(self):
        from myapp import background_task
        background_task.start()

def get_linear_regression_model_filepath():
    return MyappConfig.linearRegressionModelFilepath