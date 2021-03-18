import json

from django.test import TestCase, Client
from rest_framework import status

from api.models import Courier, Order


class TestModelCouriers(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.correct_foot_courier = Courier.objects.create(
            courier_id=1,
            courier_type='foot',
            regions=[1, 2, 3],
            working_hours=['00:00-11:00', '12:00-23:00']
        )
        cls.incorrect_courier = Courier.objects.create(
            courier_id=2,
            courier_type='fit',
            regions=[1, 2, 3, "a"],
            working_hours=['00:00-11:00', 1999, '12:00-23:00']
        )
        cls.guest_client = Client()

    def test_smoke_test(self):
        response = TestModelCouriers.guest_client.get('/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = TestModelCouriers.guest_client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = TestModelCouriers.guest_client.get('/api/v1/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = TestModelCouriers.guest_client.get('/redoc/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_type_courier_id_data(self):
        """
        Проверка типа поля courier_id
        :return:
        """
        courier = TestModelCouriers.correct_foot_courier
        self.assertEquals(courier.courier_id, 1)

    def test_type_data(self):
        """
        Проверка типа поля courier_type
        :return:
        """
        courier = TestModelCouriers.correct_foot_courier
        self.assertIsInstance(courier.courier_type, str)
        self.assertIsInstance(courier.regions, list)
        self.assertIsInstance(courier.working_hours, list)

    def test_correct_value_courier_type(self):
        """
        Проверка, что корректные значения courier_type сохраняются в модель
        :return:
        """
        correct_value = ['foot', 'bike', 'car']
        courier_type = TestModelCouriers.correct_foot_courier.courier_type
        self.assertIn(courier_type, correct_value)

    def test_incorrect_value_courier_type(self):
        """
        Проверка, что некорректные значения courier_type не сохраняются в модель
        :return:
        """
        correct_value = ['foot', 'bike', 'car']
        courier_type = TestModelCouriers.incorrect_courier.courier_type
        self.assertNotIn(courier_type, correct_value)


class TestModelOrders(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.correct_order = Order.objects.create(
            order_id=1,
            weight=0.23,
            region=12,
            delivery_hours=["09:00-18:00"]
        )
        cls.incorrect_order_01 = Order.objects.create(
            order_id=2,
            weight=-0.23,
            region=12,
            delivery_hours=["09:00-18:00"]
        )
        cls.incorrect_order_02 = Order.objects.create(
            order_id=3,
            weight=50.23,
            region=12,
            delivery_hours=["0900-18:00"]
        )
        cls.guest_client = Client()

    def test_type_order_id_data(self):
        """
        Проверка типа поля order_id
        :return:
        """
        order = TestModelOrders.correct_order
        self.assertEquals(order.order_id, 1)

    def test_type_order_data(self):
        """
        Проверка типа полей модели
        :return:
        """
        order = TestModelOrders.correct_order
        self.assertIsInstance(order.weight, float)
        self.assertIsInstance(order.region, int)
        self.assertIsInstance(order.delivery_hours, list)

    def test_correct_value_weight(self):
        """
        Проверка, что корректные значения weight сохраняются в модель
        :return:
        """
        weight = TestModelOrders.correct_order.weight
        self.assertLessEqual(weight, 50)
        self.assertGreaterEqual(weight, 0.01)

    def test_incorrect_value_weight_less(self):
        """
        Проверка, что некорректные значения courier_type несохраняются в модель
        :return:
        """
        weight = TestModelOrders.incorrect_order_01.weight
        self.assertLessEqual(weight, 0.01)

    def test_correct_value_weight_greater(self):
        """
        Проверка, что корректные значения weight сохраняются в модель
        :return:
        """
        weight = TestModelOrders.incorrect_order_02.weight
        self.assertGreaterEqual(weight, 50)
