from api.tests.fixtures.fixture_api import MixinAPI
from django.test import TestCase


class URLTests(TestCase, MixinAPI):
    def setUp(self) -> None:
        self.courier = {'data': [
            {
                'courier_id': 3,
                'courier_type': 'foot',
                'regions': [2, 14, 22, 24],
                'working_hours': ['11:36-14:06', '09:06-11:06']
            },
        ]}
        self.order = {'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'region': 22,
                'delivery_hours': ['09:00-18:00']
            }
        ]}

    def test_root_api_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/."""
        response = self.client.get('/api/v1/')
        self.assertEqual(response.status_code, 200)

    def test_couriers_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/couriers/."""
        response = self.request_post_couriers(self.courier)
        self.assertEqual(response.status_code, 201)

    def test_couriers_detail_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/couriers/."""
        self.request_post_couriers(self.courier)
        response = self.client.get('/api/v1/couriers/3/')
        self.assertEqual(response.status_code, 200)

    def test_orders_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/orders/."""
        response = self.request_post_orders(self.order)
        self.assertEqual(response.status_code, 201)

    def test_orders_assign_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/orders/assign."""
        self.request_post_couriers(self.courier)
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)

    def test_orders_complete_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/orders/complete."""
        # Создаем группу заказов
        self.request_post_orders(self.order)
        # Создаем курьера
        self.request_post_couriers(self.courier)
        # Назначаем заказы
        self.request_post_orders_assign({'courier_id': 3})
        # завершаем заказы
        payload = {
            'courier_id': 3,
            'order_id': 1,
            'complete_time': '2021-08-10T10:33:01.42Z'
        }
        response = self.request_post_orders_complete(payload)
        self.assertEqual(response.status_code, 200)
