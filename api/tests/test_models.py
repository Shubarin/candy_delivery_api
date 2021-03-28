from api.models import Courier, Order
from api.tests.fixtures.fixture_api import MixinAPI
from django.test import TestCase
from rest_framework import status


class TestModelCouriers(TestCase, MixinAPI):
    def test_smoke_test(self):
        """Проверка доступности основных узлов"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get('/redoc/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_correct_value_courier_type(self):
        """Корректные значения courier_type сохраняются в модель"""
        types = ['foot', 'bike', 'car']
        payload = {'data': [{'regions': [2],
                             'working_hours': ['11:30-14:00']}]}
        for i, courier_type in enumerate(types, 4):
            payload['data'][0]['courier_id'] = i
            payload['data'][0]['courier_type'] = courier_type
            response = self.request_post_couriers(payload)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            courier_type = Courier.objects.get(courier_id=i).courier_type
            self.assertIn(courier_type, types)

    def test_incorrect_value_courier_type(self):
        """Некорректные значения courier_type не сохраняются в модель"""
        types = ['foo', 'bar', 1234, None, []]
        payload = {'data': [{'regions': [2],
                             'working_hours': ['11:30-14:00']}]}
        for i, courier_type in enumerate(types, 4):
            payload['data'][0]['courier_id'] = i
            payload['data'][0]['courier_type'] = courier_type
            response = self.request_post_couriers(payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_correct_value_regions(self):
        """Корректные значения regions сохраняются в модель"""
        regions = [[1], [1, 2, 3], [10000, 10001]]
        payload = {'data': [{'courier_type': 'foot',
                             'working_hours': ['11:30-14:00']}]}
        for i, region in enumerate(regions, 4):
            payload['data'][0]['courier_id'] = i
            payload['data'][0]['regions'] = region
            response = self.request_post_couriers(payload)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            reg_li = [int(x)
                      for x in Courier.objects.get(courier_id=i).regions]
            self.assertIn(reg_li, regions)

    def test_incorrect_value_regions(self):
        """Некорректные значения regions  не сохраняются в модель"""
        regions = [[], ['1, 2, 3'], [0], [-1],
                   [None], None, 1, -1, 0, 100, 'a']
        payload = {'data': [{'courier_type': 'car',
                             'working_hours': ['11:30-14:00']}]}
        for i, region in enumerate(regions, 4):
            payload['data'][0]['courier_id'] = i
            payload['data'][0]['regions'] = region
            response = self.request_post_couriers(payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_correct_value_working_hours(self):
        """Корректные значения working_hours сохраняются в модель"""
        working_hours = [['00:00-23:59'], ['00:00-12:00', '12:01-23:59']]
        payload = {'data': [{'courier_type': 'foot', 'regions': [1]}]}
        for i, hours in enumerate(working_hours, 4):
            payload['data'][0]['courier_id'] = i
            payload['data'][0]['working_hours'] = hours
            response = self.request_post_couriers(payload)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            hours_ = Courier.objects.get(courier_id=i).working_hours
            self.assertIn(hours_, working_hours)

    def test_incorrect_value_working_hours(self):
        """Некорректные значения working_hours не сохраняются в модель"""
        working_hours = [[], ['00:00-1200'], ['0000-12:00'], ['0000-1200'],
                         ['00:0012:00'], ['00001200'], ['Foo-Bar'], ['Foo:Ba'],
                         [12], [None], 'foo-bar', None, 123, '00:00-12:00',
                         ['17:00-12:00'], ['12:00-00:01'], ['00:00-24:01']]
        payload = {'data': [{'courier_type': 'foot', 'regions': [1]}]}
        for i, hours in enumerate(working_hours, 4):
            payload['data'][0]['courier_id'] = i
            payload['data'][0]['working_hours'] = hours
            response = self.request_post_couriers(payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_max_weight(self):
        """Функция get_max_weight возвращает корректные значения"""
        expected_data = {'foot': 10, 'bike': 15, 'car': 50}
        for key, expected_val in expected_data.items():
            self.assertEqual(Courier.get_max_weight(key), expected_val)

    def test_can_take_weight(self):
        """Функция can_take_weight возвращает корректные значения"""
        payload = {'data': [{'regions': [2], 'working_hours': ['11:30-14:00'],
                             'courier_id': 1, 'courier_type': 'foot'}]}
        self.request_post_couriers(payload)
        courier = Courier.objects.get(pk=1)
        payload = {'data': [{'region': 2, 'delivery_hours': ['11:30-14:00'],
                             'order_id': 1, 'weight': 1},
                            {'region': 2, 'delivery_hours': ['11:30-14:00'],
                             'order_id': 2, 'weight': 11}]}
        self.request_post_orders(payload)
        order = Order.objects.get(pk=1)
        self.assertTrue(courier.can_take_weight(order))
        order = Order.objects.get(pk=2)
        self.assertFalse(courier.can_take_weight(order))


class TestModelOrders(TestCase, MixinAPI):
    def test_correct_value_weight(self):
        """Корректные значения weight сохраняются в модель"""
        weights = [0.01, 50, 49]
        payload = {'data': [{'region': 2, 'delivery_hours': ['11:30-14:00']}]}
        for i, weight in enumerate(weights, 1):
            payload['data'][0]['order_id'] = i
            payload['data'][0]['weight'] = weight
            response = self.request_post_orders(payload)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            weight_ = float(Order.objects.get(order_id=i).weight)
            self.assertIn(weight_, weights)

    def test_incorrect_value_weight(self):
        """Некорректные значения weight не сохраняются в модель"""
        weights = [0, -50, 50.0001, 'foo', 0.00001, 1000, -1000, [], [1], None]
        payload = {'data': [{'region': 2, 'delivery_hours': ['11:30-14:00']}]}
        for i, weight in enumerate(weights, 1):
            payload['data'][0]['order_id'] = i
            payload['data'][0]['weight'] = weight
            response = self.request_post_orders(payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_correct_value_region(self):
        """Корректные значения region сохраняются в модель"""
        regions = [1, 2, 10000, 10001]
        payload = {'data': [{'weight': 1, 'delivery_hours': ['09:00-14:00']}]}
        for i, region in enumerate(regions, 4):
            payload['data'][0]['order_id'] = i
            payload['data'][0]['region'] = region
            response = self.request_post_orders(payload)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            region_ = Order.objects.get(order_id=i).region
            self.assertIn(region_, regions)

    def test_incorrect_value_region(self):
        """Некорректные значения region не сохраняются в модель"""
        regions = [0, -2, 1.2, None, 'foo', [], [1]]
        payload = {'data': [{'weight': 1, 'delivery_hours': ['09:00-14:00']}]}
        for i, region in enumerate(regions, 4):
            payload['data'][0]['order_id'] = i
            payload['data'][0]['region'] = region
            response = self.request_post_orders(payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_correct_delivery_hours(self):
        """Корректные значения delivery_hours сохраняются в модель"""
        delivery_hours = [['00:00-23:59'], ['00:00-12:00', '12:01-23:59']]
        payload = {'data': [{'region': 2, 'weight': 1}]}
        for i, hours in enumerate(delivery_hours, 1):
            payload['data'][0]['order_id'] = i
            payload['data'][0]['delivery_hours'] = hours
            response = self.request_post_orders(payload)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            hours_ = Order.objects.get(order_id=i).delivery_hours
            self.assertIn(hours_, delivery_hours)

    def test_incorrect_delivery_hours(self):
        """Неорректные значения delivery_hours не сохраняются в модель"""
        delivery_hours = [[], ['00:00-1200'], ['0000-12:00'], ['0000-1200'],
                          ['00:0012:00'], ['00001200'], ['Foo-Bar'],
                          ['Foo:Bar'], [12], [None], 'foo-bar',
                          None, 123, '00:00-12:00', ['00:00-24:00']]
        payload = {'data': [{'region': 2, 'weight': 1}]}
        for i, hours in enumerate(delivery_hours, 1):
            payload['data'][0]['order_id'] = i
            payload['data'][0]['delivery_hours'] = hours
            response = self.request_post_orders(payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_assign_cancel(self):
        """тест для проверки отмены назначения заказа"""
        payload = {'data': [{'regions': [2], 'working_hours': ['11:30-14:00'],
                             'courier_id': 1, 'courier_type': 'foot'}]}
        self.request_post_couriers(payload)
        payload = {'data': [{'region': 2, 'delivery_hours': ['11:30-14:00'],
                             'order_id': 1, 'weight': 1},
                            {'region': 2, 'delivery_hours': ['11:30-14:00'],
                             'order_id': 2, 'weight': 11}]}
        self.request_post_orders(payload)
        order = Order.objects.get(pk=1)
        self.request_post_orders_assign({'courier_id': 1})
        order.cancel_assign()
        self.assertIsNone(order.assign_courier)
        self.assertTrue(order.allow_to_assign)
