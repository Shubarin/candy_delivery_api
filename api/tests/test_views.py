import json

from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from rest_framework import status

from api.models import Courier, Order, Assign


class TestAPICouriers(TestCase):
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
        cls.correct_post_courier_payload = {"data": [
            {
                "courier_id": 3,
                "courier_type": "bike",
                "regions": [2, 14, 24],
                "working_hours": ["09:00-14:00", "19:00-23:00"]
            },
        ]}

    def test_post_couriers_correct(self):
        """
        Проверка успешного запроса на добавление курьеров.
        Должен вернуть HTTP_201_CREATE
        """
        client = TestAPICouriers.guest_client
        correct_payload = {"data": [
            {
                "courier_id": 3,
                "courier_type": "foot",
                "regions": [2, 14, 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            },
            {
                "courier_id": 4,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            }
        ]}

        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}, {'id': 4}]}, response.data)

    def test_post_couriers_incorrect_courier_type(self):
        """
        Проверка запроса с пустым/некорректным courier_type.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "courier_id": 5,
                "courier_type": "fot",
                "regions": [2, 14, 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            },
            {
                "courier_id": 6,
                "courier_type": "",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            }
        ]}
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_incorrect_regions(self):
        """
        Проверка запроса с пустым и/или некорректным списком regions.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "courier_id": 5,
                "courier_type": "foot",
                "regions": [2, "a", 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            },
            {
                "courier_id": 6,
                "courier_type": "bike",
                "regions": [],
                "working_hours": ["09:00-18:00"]
            }
        ]}
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_incorrect_working_hours(self):
        """
        Проверка запроса с пустым и/или некорректным списком working_hours.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "courier_id": 5,
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["1136-14:06", "09:0611:06"]
            },
            {
                "courier_id": 6,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": []
            }
        ]}
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_incorrect_courier_id(self):
        """
        Проверка запроса с существующим courier_id.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "courier_id": 2,
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            },
            {
                "courier_id": 2,
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            }
        ]}
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_empty(self):
        """
        Проверка пустого запроса. Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": []}
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_empty_item(self):
        """
        Проверка непустого запроса. Но у одного из курьеров нет полей.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "courier_id": 2,
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            },
            {}
        ]}
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_incorrect_extra_field_in(self):
        """
            Проверка запроса с несуществующими полями.
            Должен вернуть HTTP_400_BAD_REQUEST
            """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "courier_id": 4,
                "sleep": 5,  # лишнее поле
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["11:36-14:06", "09:06-11:06"]
            },
        ]}
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_courier_type_correct(self):
        """
        Проверка успешного запроса на редактирование типа курьера.
        Должен вернуть HTTP_200_O
        """
        client = TestAPICouriers.guest_client
        # Создаем курьера, которого будем редактировать
        correct_payload = TestAPICouriers.correct_post_courier_payload
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        old_courier = Courier.objects.get(pk=3)
        correct_edit_payload = {"courier_type": "foot"}
        response = client.patch('/api/v1/couriers/3/',
                                data=json.dumps(correct_edit_payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_courier = Courier.objects.get(pk=3)

        self.assertNotEqual(old_courier.courier_type, new_courier.courier_type)

    def test_patch_regions_correct(self):
        """
        Проверка успешного запроса на редактирование списка районов.
        Должен вернуть HTTP_200_O
        """
        client = TestAPICouriers.guest_client
        # Создаем курьера, которого будем редактировать
        correct_payload = TestAPICouriers.correct_post_courier_payload
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        old_courier = Courier.objects.get(pk=3)
        correct_edit_payload = {"regions": [2]}
        response = client.patch('/api/v1/couriers/3/',
                                data=json.dumps(correct_edit_payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_courier = Courier.objects.get(pk=3)
        self.assertNotEqual(old_courier.regions, new_courier.regions)
        expected_response_data = {
            'courier_id': 3,
            'courier_type': 'bike',
            'regions': ['2'],
            'working_hours': ['09:00-14:00', '19:00-23:00']
        }
        self.assertEqual(expected_response_data, response.data)

    def test_patch_working_hours_correct(self):
        """
        Проверка успешного запроса на редактирование списка часов работы.
        Должен вернуть HTTP_200_O
        """
        client = TestAPICouriers.guest_client
        # Создаем курьера, которого будем редактировать
        correct_payload = TestAPICouriers.correct_post_courier_payload
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        old_courier = Courier.objects.get(pk=3)
        correct_edit_payload = {"working_hours": ["07:00-11:00", "17:00-21:00"]}
        response = client.patch('/api/v1/couriers/3/',
                                data=json.dumps(correct_edit_payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_courier = Courier.objects.get(pk=3)
        self.assertNotEqual(old_courier.working_hours,
                            new_courier.working_hours)

    def test_patch_not_found(self):
        """
        Проверка ошибочного запроса на редактирование курьера (id не существует)
        Должен вернуть HTTP_404_NOT_FOUN
        """

        client = TestAPICouriers.guest_client
        # Создаем курьера, которого будем редактировать
        correct_payload = TestAPICouriers.correct_post_courier_payload
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        correct_edit_payload = {"working_hours": ["07:00-11:00", "17:00-21:00"]}
        response = client.patch('/api/v1/couriers/5/',
                                data=json.dumps(correct_edit_payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_extra_field(self):
        """
        Проверка ошибочного запроса на редактирование курьера
        Передано несуществуеющее поле
        Должен вернуть HTTP_400_BAD_REQUEST
        """

        client = TestAPICouriers.guest_client
        # Создаем курьера, которого будем редактировать
        correct_payload = TestAPICouriers.correct_post_courier_payload
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        incorrect_edit_payload = {"evil": True}
        response = client.patch('/api/v1/couriers/3/',
                                data=json.dumps(incorrect_edit_payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_change_courier_type(self):
        client = TestAPICouriers.guest_client
        # Создаем курьера, которого будем редактировать
        correct_payload = TestAPICouriers.correct_post_courier_payload
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Создаем группу заказов
        correct_payload = {"data": [
            {
                "order_id": 1,
                "weight": 14,
                "region": 2,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 0.23,
                "region": 2,
                "delivery_hours": ["09:00-18:00"]
            }
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # Назначаем заказы нашему курьеру
        # курьер должен был получить заказ id=1, id=2
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 3}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}, {'id': 2}])
        # меняем тип курьера так, чтобы
        # он не мог доставить товар 1
        edit_payload = {'courier_type': 'foot'}
        response = client.patch('/api/v1/couriers/3/',
                                data=json.dumps(edit_payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем доступность первого заказа для других курьеров
        courier = get_object_or_404(Courier, pk=3)
        assign = courier.assign.filter(orders__pk=1)
        # TODO: удалить заказ из назначения
        order = get_object_or_404(Order, pk=1)
        self.assertTrue(order.allow_to_assign)
        self.assertIsNone(order.assign_courier)
        # Проверяем что второй заказ не отменен
        order = get_object_or_404(Order, pk=2)
        self.assertFalse(order.allow_to_assign)
        self.assertEqual(courier, order.assign_courier)


    def test_patch_change_working_hours(self):
        client = TestAPICouriers.guest_client
        # Создаем курьера, которого будем редактировать
        correct_payload = TestAPICouriers.correct_post_courier_payload
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Создаем группу заказов
        correct_payload = {"data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 1,
                "delivery_hours": ["09:00-11:00"]
            },
            {
                "order_id": 2,
                "weight": 1,
                "region": 2,
                "delivery_hours": ["09:00-18:00"]
            }
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # Назначаем заказы нашему курьеру
        # курьер должен был получить заказ id=1, id=2
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 1}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}, {'id': 2}])
        # меняем рабочие часы так, чтобы
        # они не укладывались во время доставки товара 1
        edit_payload = {'working_hours': ['12:00-23:00']}
        response = client.patch('/api/v1/couriers/1/',
                                data=json.dumps(edit_payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем доступность первого заказа для других курьеров
        courier = get_object_or_404(Courier, pk=1)
        assign = courier.assign.filter(orders__pk=1)
        # TODO: удалить заказ из назначения
        order = get_object_or_404(Order, pk=1)
        self.assertTrue(order.allow_to_assign)
        self.assertIsNone(order.assign_courier)
        # Проверяем что второй заказ не отменен
        order = get_object_or_404(Order, pk=2)
        self.assertFalse(order.allow_to_assign)
        self.assertEqual(courier, order.assign_courier)

    def test_patch_change_region(self):
        client = TestAPICouriers.guest_client
        # Создаем курьера, которого будем редактировать
        correct_payload = TestAPICouriers.correct_post_courier_payload
        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Создаем группу заказов
        correct_payload = {"data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 1,
                "region": 2,
                "delivery_hours": ["09:00-18:00"]
            }
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # Назначаем заказы нашему курьеру
        # курьер должен был получить заказ id=1, id=2
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 1}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}, {'id': 2}])
        # меняем регионы так, чтобы первый заказ не обслуживался курьером
        edit_payload = {"regions": [2, 3]}
        response = client.patch('/api/v1/couriers/1/',
                                data=json.dumps(edit_payload),
                                content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем доступность первого заказа для других курьеров
        courier = get_object_or_404(Courier, pk=1)
        assign = courier.assign.filter(orders__pk=1)
        # TODO: удалить заказ из назначения
        order = get_object_or_404(Order, pk=1)
        self.assertTrue(order.allow_to_assign)
        self.assertIsNone(order.assign_courier)
        # Проверяем что второй заказ не отменен
        order = get_object_or_404(Order, pk=2)
        self.assertFalse(order.allow_to_assign)
        self.assertEqual(courier, order.assign_courier)


class TestAPIOrders(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.correct_post_order_payload = {"data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
        ]}

    def test_post_orders_correct(self):
        """
        Проверка успешного запроса на добавление заказов.
        Должен вернуть HTTP_201_CREATE
        """
        client = TestAPIOrders.guest_client
        correct_payload = {"data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            }
        ]}

        response = client.post('/api/v1/orders/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

    def test_post_orders_incorrect_weight(self):
        """
        Проверка запроса с пустым/некорректным weight.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "order_id": 1,
                "weight": 99,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": -15,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": None,
                "region": 1,
                "delivery_hours": ["09:00-18:00"]
            }
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_incorrect_region(self):
        """
        Проверка запроса с пустым и/или некорректным region.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": -12,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 1.4,
                "delivery_hours": ["09:00-18:00"]
            }
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_incorrect_delivery_hours(self):
        """
        Проверка запроса с пустым и/или некорректным delivery_hours.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["0900-18:00"]
            },
            {
                "order_id": 2,
                "weight": 15,
                "region": 1,
                "delivery_hours": []
            }
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_empty(self):
        """Проверка пустого запроса. Должен вернуть HTTP_400_BAD_REQUEST"""
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": []}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_empty_item(self):
        """
        Проверка непустого запроса. Но у одного из заказов нет полей.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
            {}
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_incorrect_extra_field_in(self):
        """
        Проверка запроса с несуществующими полями.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPICouriers.guest_client
        incorrect_payload = {"data": [
            {
                "order_id": 1,
                "weight": 0.23,
                "sleep": 5,
                "region": 12,
                "delivery_hours": ["09:00-18:00"]
            },
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(incorrect_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_assign_incorrect_courier_id(self):
        """
        Проверка неверного запроса на назначение заказов (плохой courier_id).
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        client = TestAPIOrders.guest_client
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

        # Создаем курьеров
        correct_payload = {"data": [
            {
                "courier_id": 3,
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["11:00-14:00", "09:00-10:00"]
            },
            {
                "courier_id": 4,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 5,
                "courier_type": "car",
                "regions": [2, 14, 22, 24],
                "working_hours": ["00:00-21:00"]
            }
        ]}

        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}, {'id': 4}, {'id': 5}]},
                         response.data)

        # назначаем заказы
        # 6 курьер не должен был получить заказов
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 6}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # bad_id курьер не должен был получить заказов
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 'bad_id'}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # None курьер не должен был получить заказов
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": None}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_orders_assign_weight_greatest_allowed_weight_courier(self):
        client = TestAPIOrders.guest_client
        correct_payload = {"data": [
            {
                "order_id": 1,
                "weight": 15,
                "region": 22,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 2,
                "weight": 20,
                "region": 22,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 3,
                "weight": 30,
                "region": 22,
                "delivery_hours": ["09:00-18:00"]
            },
            {
                "order_id": 4,
                "weight": 50,
                "region": 22,
                "delivery_hours": ["09:00-18:00"]
            },
        ]}
        response = client.post('/api/v1/orders/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {'orders': [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}]},
            response.data)

        # Создаем курьеров
        correct_payload = {"data": [
            {
                "courier_id": 1,
                "courier_type": "foot",
                "regions": [22],
                "working_hours": ["00:00-23:59"]
            },
            {
                "courier_id": 2,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["00:00-23:59"]
            },
            {
                "courier_id": 3,
                "courier_type": "car",
                "regions": [22],
                "working_hours": ["00:00-23:59"]
            }
        ]}

        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 1}, {'id': 2}, {'id': 3}]},
                         response.data)

        # назначаем заказы
        # 1 курьер не должен был получить заказов
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 1}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [])

        # 2 курьер должен был получить заказ 1, остальные не проходят по весу
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 2}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # 3 курьер должен был получить заказ 2, 3 остальные не проходят по весу
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 3}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 2}, {'id': 3}])

    def test_post_orders_assign_double_assign(self):
        client = TestAPIOrders.guest_client
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}]},
                         response.data)

        # Назначаем первый заказ
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 3}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # Повторное назначение недоступно
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 3}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [])

    def test_post_orders_assign_correct(self):
        """
        Проверка успешного запроса на назначение заказов.
        Должен вернуть HTTP_200_OK
        """
        client = TestAPIOrders.guest_client
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

        # Создаем курьеров
        correct_payload = {"data": [
            {
                "courier_id": 3,
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["11:00-14:00", "09:00-10:00"]
            },
            {
                "courier_id": 4,
                "courier_type": "bike",
                "regions": [22],
                "working_hours": ["09:00-18:00"]
            },
            {
                "courier_id": 5,
                "courier_type": "car",
                "regions": [2, 14, 22, 24],
                "working_hours": ["00:00-21:00"]
            }
        ]}

        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}, {'id': 4}, {'id': 5}]},
                         response.data)

        # назначаем заказы
        # 3 курьер должен был получить только заказ id=1
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 3}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # 4 курьер должен был получить только заказ id=1
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 4}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 2}])

        # 5 курьер не должен был получить заказов, в ответе нет assign_time
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 5}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [])
        self.assertNotIn('assign_time', response.data)

    def test_post_orders_complete_incorrect_order_id(self):
        client = TestAPIOrders.guest_client
        # завершаем заказы
        correct_payload = {
            "courier_id": 3,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }
        response = client.post('/api/v1/orders/complete/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_complete_incorrect_not_assign_order(self):
        client = TestAPIOrders.guest_client
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # завершаем заказы
        correct_payload = {
            "courier_id": 3,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }
        response = client.post('/api/v1/orders/complete/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_complete_incorrect_courier_id(self):
        client = TestAPIOrders.guest_client
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # завершаем заказы
        correct_payload = {
            "courier_id": 3,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }
        response = client.post('/api/v1/orders/complete/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_complete_incorrect_courier_id_other_order(self):
        client = TestAPIOrders.guest_client
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # Создаем курьера
        correct_payload = {"data": [
            {
                "courier_id": 3,
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["11:00-14:00", "09:00-10:00"]
            },
            {
                "courier_id": 4,
                "courier_type": "foot",
                "regions": [2, 22, 24],
                "working_hours": ["11:00-14:00", "09:00-10:00"]
            }
        ]}

        response = client.post('/api/v1/couriers/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}, {'id': 4}]},
                         response.data)

        # Назначаем заказы
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 3}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])
        # завершаем заказы
        correct_payload = {
            "courier_id": 4,
            "order_id": 1,
            "complete_time": "2021-01-10T10:33:01.42Z"
        }
        response = client.post('/api/v1/orders/complete/',
                               data=json.dumps(correct_payload),
                               content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_complete_correct(self):
        client = TestAPIOrders.guest_client
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}]},
                         response.data)

        # Назначаем заказы
        response = client.post('/api/v1/orders/assign/',
                               data=json.dumps({"courier_id": 3}),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

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
        self.assertEqual(response.data['order_id'], 1)
