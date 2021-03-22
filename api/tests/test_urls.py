import json

from django.test import TestCase, Client


class URLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_root_api_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/."""
        response = self.guest_client.get('/api/v1/')
        self.assertEqual(response.status_code, 200)

    def test_couriers_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/couriers/."""
        correct_payload = {"data": [
            {
                "courier_id": 3,
                "courier_type": "foot",
                "regions": [2, 14, 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            },
        ]}
        response = self.guest_client.post('/api/v1/couriers/',
                                          data=json.dumps(correct_payload),
                                          content_type='application/json')
        self.assertEqual(response.status_code, 201)

    def test_couriers_detail_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/couriers/."""
        correct_payload = {"data": [
            {
                "courier_id": 3,
                "courier_type": "foot",
                "regions": [2, 14, 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            },
        ]}

        self.guest_client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        response = self.guest_client.get('/api/v1/couriers/3/')
        self.assertEqual(response.status_code, 200)

    def test_orders_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/orders/."""
        response = self.guest_client.get('/api/v1/orders/')
        self.assertEqual(response.status_code, 200)

    def test_orders_assign_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/orders/assign."""
        correct_payload = {"data": [
            {
                "courier_id": 3,
                "courier_type": "foot",
                "regions": [2, 14, 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            },
        ]}
        self.guest_client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        response = self.guest_client.post('/api/v1/orders/assign/',
                                          data=json.dumps({"courier_id": 3}),
                                          content_type='application/json')
        self.assertEqual(response.status_code, 200)

    def test_orders_complete_url_exists_at_desired_location(self):
        """Проверка доступности адреса /api/v1/orders/complete."""
        client = self.guest_client
        # Создаем группу заказов
        correct_payload = {"data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 22,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 22,
                "delivery_hours": ["09:00-18:00"]
            }
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')

        # Создаем курьера
        correct_payload = {"data": [
            {
                "courier_id": 3,
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["11:00-14:00", "09:00-10:00"]
            }
        ]}

        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')

        # Назначаем заказы
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 3}),
                               content_type='application/json')
        # завершаем заказы
        correct_payload = {
            "courier_id": 3,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }
        response = client.post('/api/v1/orders/complete/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
