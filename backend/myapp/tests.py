from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.utils import timezone
from myapp.models import AaplStockData
import decimal
import datetime

# Create your tests here.

class BackTestAPITestCase(APITestCase):

    def test_missing_parameters(self):
        """
        Test that the API returns 400 Bad Request when any parameters are missing.
        """
        url = reverse('back_test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_numeric_parameters(self):
        """
        Test that the API returns 400 Bad Request when any parameters are non-numeric.
        """
        url = reverse('back_test')
        params = {
            'investing_amount': 'abc',
            'sell_period': 'def',
            'buy_period': 'ghi',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_negative_parameters(self):
        """
        Test that the API returns 400 Bad Request when any parameters are negative.
        """
        url = reverse('back_test')
        params = {
            'investing_amount': '-10000',
            'sell_period': '-5',
            'buy_period': '-10',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_parameters(self):
        """
        Test that the API returns 200 OK when valid parameters are provided.
        """
        # Create sample stock data
        dates = [timezone.now() - datetime.timedelta(days=i) for i in range(30)]
        for date in dates:
            AaplStockData.objects.create(
                time=date,
                open_price=decimal.Decimal('100.00'),
                close_price=decimal.Decimal('105.00'),
                high_price=decimal.Decimal('110.00'),
                low_price=decimal.Decimal('95.00'),
                volume=decimal.Decimal('1000')
            )

        url = reverse('back_test')
        params = {
            'investing_amount': '10000',
            'sell_period': '5',
            'buy_period': '10',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profit', response.data)
        self.assertIn('events', response.data)

    def test_zero_investment_amount(self):
        """
        Test that the API handles zero investment amount gracefully.
        """
        # Create sample stock data
        dates = [timezone.now() - datetime.timedelta(days=i) for i in range(30)]
        for date in dates:
            AaplStockData.objects.create(
                time=date,
                open_price=decimal.Decimal('100.00'),
                close_price=decimal.Decimal('105.00'),
                high_price=decimal.Decimal('110.00'),
                low_price=decimal.Decimal('95.00'),
                volume=decimal.Decimal('1000')
            )

        url = reverse('back_test')
        params = {
            'investing_amount': '0',
            'sell_period': '5',
            'buy_period': '10',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profit'], 0)
        self.assertEqual(len(response.data['events']), 0)

    def test_large_investment_amount(self):
        """
        Test the API with a very large investment amount.
        """
        # Create sample stock data
        dates = [timezone.now() - datetime.timedelta(days=i) for i in range(365)]
        for date in dates:
            AaplStockData.objects.create(
                time=date,
                open_price=decimal.Decimal('150.00'),
                close_price=decimal.Decimal('155.00'),
                high_price=decimal.Decimal('160.00'),
                low_price=decimal.Decimal('145.00'),
                volume=decimal.Decimal('5000')
            )

        url = reverse('back_test')
        params = {
            'investing_amount': '10000000',  # Large investment amount
            'sell_period': '20',
            'buy_period': '50',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profit', response.data)
        self.assertIn('events', response.data)

    def test_boundary_conditions(self):
        """
        Test boundary conditions like investing_amount=1, sell_period=1, buy_period=1.
        """
        # Create sample stock data
        dates = [timezone.now() - datetime.timedelta(days=i) for i in range(2)]
        prices = ['100.00', '101.00']
        for i, date in enumerate(dates):
            AaplStockData.objects.create(
                time=date,
                open_price=decimal.Decimal(prices[i]),
                close_price=decimal.Decimal(prices[i]),
                high_price=decimal.Decimal(prices[i]),
                low_price=decimal.Decimal(prices[i]),
                volume=decimal.Decimal('1000')
            )

        url = reverse('back_test')
        params = {
            'investing_amount': '1',
            'sell_period': '1',
            'buy_period': '1',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profit', response.data)
        self.assertIn('events', response.data)

    def test_same_sell_and_buy_period(self):
        """
        Test that the API handles cases where sell_period equals buy_period.
        """
        # Create sample stock data
        dates = [timezone.now() - datetime.timedelta(days=i) for i in range(30)]
        for date in dates:
            AaplStockData.objects.create(
                time=date,
                open_price=decimal.Decimal('120.00'),
                close_price=decimal.Decimal('125.00'),
                high_price=decimal.Decimal('130.00'),
                low_price=decimal.Decimal('115.00'),
                volume=decimal.Decimal('2000')
            )

        url = reverse('back_test')
        params = {
            'investing_amount': '5000',
            'sell_period': '10',
            'buy_period': '10',  # Same periods
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profit', response.data)
        self.assertIn('events', response.data)

    def test_sell_period_greater_than_buy_period(self):
        """
        Test that the API handles cases where sell_period is greater than buy_period.
        """
        # Create sample stock data
        dates = [timezone.now() - datetime.timedelta(days=i) for i in range(60)]
        for date in dates:
            AaplStockData.objects.create(
                time=date,
                open_price=decimal.Decimal('80.00'),
                close_price=decimal.Decimal('85.00'),
                high_price=decimal.Decimal('90.00'),
                low_price=decimal.Decimal('75.00'),
                volume=decimal.Decimal('3000')
            )

        url = reverse('back_test')
        params = {
            'investing_amount': '10000',
            'sell_period': '30',  # Sell period greater than buy period
            'buy_period': '10',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profit', response.data)
        self.assertIn('events', response.data)

    def test_no_stock_data(self):
        """
        Test that the API returns appropriate response when there is no stock data.
        """
        url = reverse('back_test')
        params = {
            'investing_amount': '10000',
            'sell_period': '5',
            'buy_period': '10',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profit'], 0)
        self.assertEqual(len(response.data['events']), 0)

    def test_future_dates(self):
        """
        Test that the API handles future dates in stock data appropriately.
        """
        # Create sample stock data with future dates
        dates = [timezone.now() + datetime.timedelta(days=i) for i in range(30)]
        for date in dates:
            AaplStockData.objects.create(
                time=date,
                open_price=decimal.Decimal('90.00'),
                close_price=decimal.Decimal('95.00'),
                high_price=decimal.Decimal('100.00'),
                low_price=decimal.Decimal('85.00'),
                volume=decimal.Decimal('4000')
            )

        url = reverse('back_test')
        params = {
            'investing_amount': '7000',
            'sell_period': '5',
            'buy_period': '10',
        }
        response = self.client.get(url, params)
        # Assuming future dates should not affect backtesting, adjust assertions accordingly
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profit', response.data)
        self.assertIn('events', response.data)

    def test_invalid_sell_and_buy_periods(self):
        """
        Test that the API returns 400 Bad Request when sell_period or buy_period is zero.
        """
        url = reverse('back_test')
        params = {
            'investing_amount': '5000',
            'sell_period': '0',
            'buy_period': '0',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_integer_periods(self):
        """
        Test that the API returns 400 Bad Request when sell_period or buy_period is a non-integer.
        """
        url = reverse('back_test')
        params = {
            'investing_amount': '5000',
            'sell_period': '5.5',
            'buy_period': '10.1',
        }
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
