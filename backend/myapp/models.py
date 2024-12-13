from django.db import models

# Create your models here.

class AaplStockData(models.Model):
    time = models.DateTimeField(primary_key=True)  # Maps to TIMESTAMPTZ
    open_price = models.DecimalField(max_digits=20, decimal_places=4)  # Maps to DECIMAL
    close_price = models.DecimalField(max_digits=20, decimal_places=4)  # Maps to DECIMAL
    high_price = models.DecimalField(max_digits=20, decimal_places=4)  # Maps to DECIMAL
    low_price = models.DecimalField(max_digits=20, decimal_places=4)   # Maps to DECIMAL
    volume = models.DecimalField(max_digits=20, decimal_places=4)

    class Meta:
        db_table = 'aapl_stock_data'
        
    @staticmethod
    def get_data_with_moving_average(selling_period: int, buying_period: int):
        query = f"""
            SELECT 
                time,
                open_price,
                close_price,
                high_price,
                low_price,
                volume,
                AVG(close_price) OVER (
                    ORDER BY time 
                    ROWS BETWEEN {selling_period} PRECEDING AND CURRENT ROW
                ) AS selling_moving_average,
                AVG(close_price) OVER (
                    ORDER BY time 
                    ROWS BETWEEN {buying_period} PRECEDING AND CURRENT ROW
                ) AS buying_moving_average
            FROM 
                aapl_stock_data
            ORDER BY 
                time;
        """
        
        stock_data = AaplStockData.objects.raw(query)
        
        # read the selling and buying moving average from the stock_data and set them to the stock_data object
        for stock in stock_data:
            stock.moving_average_selling = stock.__dict__.get('selling_moving_average')
            stock.moving_average_buying = stock.__dict__.get('buying_moving_average')

        return stock_data

