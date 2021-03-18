import json

from django.test import TestCase, Client
from rest_framework import status

from api.models import Courier


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

    def test_model_type_courier_id_data(self):
        """
        Проверка типа поля courier_id
        :return:
        """
        courier = TestModelCouriers.correct_foot_courier
        self.assertEquals(courier.courier_id, 1)

    def test_model_type_courier_type_data(self):
        """
        Проверка типа поля courier_type
        :return:
        """
        courier = TestModelCouriers.correct_foot_courier
        self.assertEquals(courier.courier_type, 'foot')
        self.assertEquals(courier.regions, [1, 2, 3])
        self.assertEquals(courier.working_hours, ['00:00-11:00', '12:00-23:00'])

    def test_model_type_regions_data(self):
        """
        Проверка типа поля regions
        :return:
        """
        courier = TestModelCouriers.correct_foot_courier
        self.assertEquals(courier.regions, [1, 2, 3])
        self.assertEquals(courier.working_hours, ['00:00-11:00', '12:00-23:00'])

    def test_model_type_working_hours_data(self):
        """
        Проверка типа поля working_hours
        :return:
        """
        courier = TestModelCouriers.correct_foot_courier
        self.assertEquals(courier.working_hours, ['00:00-11:00', '12:00-23:00'])

    def test_model_correct_value_courier_type(self):
        """
        Проверка, что корректные значения courier_type сохраняются в модель
        :return:
        """
        correct_value = ['foot', 'bike', 'car']
        courier_type = TestModelCouriers.correct_foot_courier.courier_type
        self.assertIn(courier_type, correct_value)

    def test_model_incorrect_value_courier_type(self):
        """
        Проверка, что некорректные значения courier_type не сохраняются в модель
        :return:
        """
        correct_value = ['foot', 'bike', 'car']
        courier_type = TestModelCouriers.incorrect_courier.courier_type
        self.assertNotIn(courier_type, correct_value)
