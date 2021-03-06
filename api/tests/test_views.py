import datetime

from api.models import Assign, Courier, Order
from api.tests.fixtures.fixture_api import MixinAPI
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from rest_framework import status


class TestAPICouriers(TestCase, MixinAPI):
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
            regions=[1, 2, 3, 'a'],
            working_hours=['00:00-11:00', 1999, '12:00-23:00']
        )
        cls.guest_client = Client()
        cls.correct_post_courier_payload = {'data': [
            {
                'courier_id': 3,
                'courier_type': 'bike',
                'regions': [2, 14, 24],
                'working_hours': ['09:00-14:00', '19:00-23:00']
            },
        ]}
        cls.data_courier_3_foot_4_bike = {'data': [
            {
                'courier_id': 3,
                'courier_type': 'foot',
                'regions': [2, 14, 24],
                'working_hours': ['11:36-14:06', '09:06-11:06']
            },
            {
                'courier_id': 4,
                'courier_type': 'bike',
                'regions': [22],
                'working_hours': ['09:00-18:00']
            }
        ]}
        cls.orders_correct = {'data': [
            {
                'order_id': 101,
                'weight': 0.23,
                'region': 2,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 102,
                'weight': 1,
                'region': 2,
                'delivery_hours': ['09:00-18:00']
            }
        ]}

    def test_post_couriers_correct(self):
        """
        Проверка успешного запроса на добавление курьеров.
        Должен вернуть HTTP_201_CREATE
        """
        payload = TestAPICouriers.data_courier_3_foot_4_bike
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}, {'id': 4}]}, response.data)

    def test_post_couriers_incorrect_courier_type(self):
        """
        Проверка запроса с пустым/некорректным courier_type.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'courier_id': 5,
                'courier_type': 'fot',
                'regions': [2, 14, 24],
                'working_hours': ['11:36-14:06', '09:06-11:06']
            },
            {
                'courier_id': 6,
                'courier_type': '',
                'regions': [22],
                'working_hours': ['09:00-18:00']
            }
        ]}
        response = self.request_post_couriers(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_incorrect_regions(self):
        """
        Проверка запроса с пустым и/или некорректным списком regions.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'courier_id': 5,
                'courier_type': 'foot',
                'regions': [2, 'a', 24],
                'working_hours': ['11:36-14:06', '09:06-11:06']
            },
            {
                'courier_id': 6,
                'courier_type': 'bike',
                'regions': [],
                'working_hours': ['09:00-18:00']
            }
        ]}
        response = self.request_post_couriers(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_incorrect_working_hours(self):
        """
        Проверка запроса с пустым и/или некорректным списком working_hours.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'courier_id': 5,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['1136-14:06', '09:0611:06']
            },
            {
                'courier_id': 6,
                'courier_type': 'bike',
                'regions': [22],
                'working_hours': []
            }
        ]}
        response = self.request_post_couriers(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_incorrect_courier_id(self):
        """
        Проверка запроса с существующим courier_id.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'courier_id': 2,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:36-14:06', '09:06-11:06']
            },
            {
                'courier_id': 2,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:36-14:06', '09:06-11:06']
            }
        ]}
        response = self.request_post_couriers(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_empty(self):
        """Проверка пустого запроса. Должен вернуть HTTP_400_BAD_REQUEST"""
        incorrect_payload = {'data': []}
        response = self.request_post_couriers(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_empty_item(self):
        """
        Проверка непустого запроса. Но у одного из курьеров нет полей.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'courier_id': 2,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:36-14:06', '09:06-11:06']
            },
            {}
        ]}
        response = self.request_post_couriers(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_couriers_incorrect_extra_field_in(self):
        """
        Проверка запроса с несуществующими полями.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'courier_id': 4,
                'sleep': 5,  # лишнее поле
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:36-14:06', '09:06-11:06']
            },
        ]}
        response = self.request_post_couriers(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_courier_type_correct(self):
        """
        Проверка успешного запроса на редактирование типа курьера.
        Должен вернуть HTTP_200_O
        """
        # Создаем курьера, которого будем редактировать
        payload = TestAPICouriers.correct_post_courier_payload
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        old_courier = Courier.objects.get(pk=3)
        response = self.request_patch_courier({'courier_type': 'foot'}, 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_courier = Courier.objects.get(pk=3)

        self.assertNotEqual(old_courier.courier_type, new_courier.courier_type)

    def test_patch_regions_correct(self):
        """
        Проверка успешного запроса на редактирование списка районов.
        Должен вернуть HTTP_200_O
        """
        # Создаем курьера, которого будем редактировать
        payload = TestAPICouriers.correct_post_courier_payload
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        old_courier = Courier.objects.get(pk=3)
        response = self.request_patch_courier({'regions': [2]}, 3)
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

    def test_patch_regions_after_assign_orders_with_delete_order(self):
        """Назначается развоз, курьер меняет свой тип,
        из развоза удаляется заказ
        """
        # Создаем курьера, которого будем редактировать
        payload = TestAPICouriers.correct_post_courier_payload
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        old_courier = Courier.objects.get(pk=3)
        response = self.request_patch_courier({'regions': [2]}, 3)
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
        # Создаем курьера, которого будем редактировать
        payload = TestAPICouriers.correct_post_courier_payload
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        old_courier = Courier.objects.get(pk=3)
        correct_edit_payload = {'working_hours': ['07:00-11:00',
                                                  '17:00-21:00']}
        response = self.request_patch_courier(correct_edit_payload, 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_courier = Courier.objects.get(pk=3)
        self.assertNotEqual(old_courier.working_hours,
                            new_courier.working_hours)

    def test_patch_not_found(self):
        """
        Проверка ошибочного запроса на редактирование курьера
        (id не существует). Должен вернуть HTTP_404_NOT_FOUN
        """
        # Создаем курьера, которого будем редактировать
        payload = TestAPICouriers.correct_post_courier_payload
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        correct_edit_payload = {'working_hours': ['07:00-11:00',
                                                  '17:00-21:00']}
        response = self.request_patch_courier(correct_edit_payload, 6)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_extra_field(self):
        """
        Проверка ошибочного запроса на редактирование курьера.
        Передано несуществуеющее поле. Должен вернуть HTTP_400_BAD_REQUEST
        """
        # Создаем курьера, которого будем редактировать
        payload = TestAPICouriers.correct_post_courier_payload
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.request_patch_courier({'evil': True}, 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_change_courier_type(self):
        # Создаем курьера, которого будем редактировать
        payload = TestAPICouriers.correct_post_courier_payload
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Создаем группу заказов
        payload = {'data': [
            {
                'order_id': 1,
                'weight': 14,
                'region': 2,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 2,
                'weight': 0.23,
                'region': 2,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        response = self.request_post_orders(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # Назначаем заказы нашему курьеру
        # курьер должен был получить заказ id=1, id=2
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}, {'id': 2}])
        # меняем тип курьера так, чтобы
        # он не мог доставить товар 1
        response = self.request_patch_courier({'courier_type': 'foot'}, 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем доступность первого заказа для других курьеров
        courier = get_object_or_404(Courier, pk=3)
        order = get_object_or_404(Order, pk=1)
        self.assertTrue(order.allow_to_assign)
        self.assertIsNone(order.assign_courier)
        # Проверяем что второй заказ не отменен
        order = get_object_or_404(Order, pk=2)
        self.assertFalse(order.allow_to_assign)
        self.assertEqual(courier, order.assign_courier)

    def test_patch_change_working_hours(self):
        """
        Назначается развоз, курьер меняет свои часы работы,
        из развоза удаляется заказ, который больше не подходит курьеру
        """
        # Создаем курьера, которого будем редактировать
        payload = TestAPICouriers.correct_post_courier_payload
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Создаем группу заказов
        payload = {'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'region': 1,
                'delivery_hours': ['09:00-11:00']
            },
            {
                'order_id': 2,
                'weight': 1,
                'region': 2,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        response = self.request_post_orders(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # Назначаем заказы нашему курьеру
        # курьер должен был получить заказ id=1, id=2
        response = self.request_post_orders_assign({'courier_id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}, {'id': 2}])
        # меняем рабочие часы так, чтобы
        # они не укладывались во время доставки товара 1
        edit_payload = {'working_hours': ['12:00-23:00']}
        response = self.request_patch_courier(edit_payload, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем доступность первого заказа для других курьеров
        courier = get_object_or_404(Courier, pk=1)
        order = get_object_or_404(Order, pk=1)
        self.assertTrue(order.allow_to_assign)
        self.assertIsNone(order.assign_courier)
        # Проверяем что второй заказ не отменен
        order = get_object_or_404(Order, pk=2)
        self.assertFalse(order.allow_to_assign)
        self.assertEqual(courier, order.assign_courier)

        edit_payload = {'working_hours': ['21:00-23:00']}
        response = self.request_patch_courier(edit_payload, 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверка что развоз корректно завершен
        self.assertTrue(courier.assign.first().is_complete)

    def test_patch_change_region(self):
        """
        Назначается развоз, курьер меняет свои районы доставки,
        из развоза удаляется заказ, который больше не подходит курьеру
        """
        # Создаем курьера, которого будем редактировать
        payload = {'data': [
            {
                'courier_id': 30,
                'courier_type': 'bike',
                'regions': [1, 2, 14, 24],
                'working_hours': ['09:00-14:00', '19:00-23:00']
            },
        ]}
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Создаем группу заказов
        payload = {'data': [
            {
                'order_id': 10,
                'weight': 0.23,
                'region': 1,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 20,
                'weight': 1,
                'region': 2,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        response = self.request_post_orders(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 10}, {'id': 20}]}, response.data)
        # Назначаем заказы нашему курьеру
        # курьер должен был получить заказ id=10, id=20
        response = self.request_post_orders_assign({'courier_id': 30})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 10}, {'id': 20}])
        # меняем регионы так, чтобы первый заказ не обслуживался курьером
        response = self.request_patch_courier({'regions': [2, 3]}, 30)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем доступность первого заказа для других курьеров
        courier = get_object_or_404(Courier, pk=30)
        # Проверяем что заказ удалился из назначения
        self.assertEqual(courier.assign.first().orders.first().pk, 20)
        order = get_object_or_404(Order, pk=10)
        self.assertTrue(order.allow_to_assign)
        self.assertIsNone(order.assign_courier)
        # Проверяем что второй заказ не отменен
        order = get_object_or_404(Order, pk=20)
        self.assertFalse(order.allow_to_assign)
        self.assertEqual(courier, order.assign_courier)

    def test_courier_detail_without_orders(self):
        """У курьера без завершенных заказов нет рейтинга и зарплаты"""
        payload = self.correct_post_courier_payload
        self.request_post_couriers(payload)

        # Заказы не созданы и не назначены
        response = self.request_get_couriers_detail(3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        orders_from_courier = Order.objects.filter(assign_courier__pk=3)
        self.assertEqual(len(orders_from_courier), 0)
        self.assertNotIn('rating', response.data)
        self.assertNotIn('earning', response.data)

        # Заказы созданы, назначены, но не выполнены
        payload = self.orders_correct
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})
        response = self.request_get_couriers_detail(3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        orders_from_courier = Order.objects.filter(assign_courier__pk=3)
        self.assertEqual(len(orders_from_courier), 2)
        self.assertNotIn('rating', response.data)
        self.assertNotIn('earning', response.data)

    def test_courier_detail_with_one_no_complete_order(self):
        """Курьер выполнил один заказ, но не завершил весь развоз"""
        payload = self.correct_post_courier_payload
        self.request_post_couriers(payload)
        # Создаем и назначаем заказы
        payload = self.orders_correct
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        assign = Assign.objects.get(courier__pk=3)
        orders = assign.orders.all()
        self.assertEqual(len(orders), 2)

        # Завершаем один заказ с id = 1
        payload = {'courier_id': 3, 'order_id': 1,
                   'complete_time': '2021-08-10T10:33:01.42Z'}
        self.request_post_orders_complete(payload)
        self.assertFalse(assign.is_complete)

        response = self.request_get_couriers_detail(3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn('rating', response.data)
        self.assertNotIn('earning', response.data)

    def test_courier_detail_with_one_complete_assign(self):
        """Курьер выполнил один полный развоз"""
        payload = self.correct_post_courier_payload
        self.request_post_couriers(payload)
        # Создаем и назначаем заказы
        payload = self.orders_correct
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Завершаем один заказ с id = 1
        format_datetime = '%Y-%m-%dT%H:%M:%S.%f%z'
        now = datetime.datetime.now() + datetime.timedelta(minutes=3)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 101, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Завершаем один заказ с id = 2
        now = datetime.datetime.now() + datetime.timedelta(minutes=5)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 102, 'complete_time': now}
        self.request_post_orders_complete(payload)

        assign = Assign.objects.get(courier__pk=3)
        self.assertTrue(assign.is_complete)

        response = self.request_get_couriers_detail(3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rating', response.data)
        self.assertIn('earning', response.data)
        # Зарплата велокурьера за один полный развоз 1 * 500 * 5
        self.assertEqual(response.data['earning'], 2500)
        # Рейтинг с минимальным средним временем развоза 150 секунд ~ 4.79
        self.assertEqual(response.data['rating'], 4.79)

    def test_courier_detail_with_one_complete_assign_and_one_no_complete(self):
        """
        Курьер выполнил один полный развоз и
        получил назначение на второй, но не выполнил его.
        Незавершенный развоз и заказы не влияют на рейтинг и зарплату.
        """
        payload = self.correct_post_courier_payload
        self.request_post_couriers(payload)
        # Создаем и назначаем заказы
        payload = self.orders_correct
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Завершаем один заказ с id = 1
        format_datetime = '%Y-%m-%dT%H:%M:%S.%f%z'
        now = datetime.datetime.now() + datetime.timedelta(minutes=3)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 101, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Завершаем один заказ с id = 2
        now = datetime.datetime.now() + datetime.timedelta(minutes=5)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 102, 'complete_time': now}
        self.request_post_orders_complete(payload)

        assign = Assign.objects.get(courier__pk=3)
        self.assertTrue(assign.is_complete)

        # Формируем второе назначение
        payload = {'data': [
            {
                'order_id': 103,
                'weight': 0.23,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 104,
                'weight': 1,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Незавершенный развоз и заказы не влияют на рейтинг
        response = self.request_get_couriers_detail(3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rating', response.data)
        self.assertIn('earning', response.data)
        # Зарплата велокурьера за один полный развоз 1 * 500 * 5
        self.assertEqual(response.data['earning'], 2500)
        # Рейтинг с минимальным средним временем развоза 150 секунд ~ 4.79
        self.assertEqual(response.data['rating'], 4.79)

    def test_courier_detail_with_one_complete_assign_and_one_partial(self):
        """
        Курьер выполнил один полный развоз и получил назначение на второй,
        но не выполнил его. Незавершенный развоз не влияет на зарплату.
        Завершенный заказ влияет на рейтинг.
        """
        payload = self.correct_post_courier_payload
        self.request_post_couriers(payload)
        # Создаем и назначаем заказы
        payload = self.orders_correct
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Завершаем один заказ с id = 101
        format_datetime = '%Y-%m-%dT%H:%M:%S.%f%z'
        now = datetime.datetime.now() + datetime.timedelta(minutes=3)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 101, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Завершаем один заказ с id = 102
        now = datetime.datetime.now() + datetime.timedelta(minutes=5)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 102, 'complete_time': now}
        self.request_post_orders_complete(payload)

        assign = Assign.objects.get(courier__pk=3)
        self.assertTrue(assign.is_complete)

        # Формируем второе назначение
        payload = {'data': [
            {
                'order_id': 103,
                'weight': 0.23,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 104,
                'weight': 1,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Завершаем один заказ с id = 103
        now = datetime.datetime.now() + datetime.timedelta(minutes=1)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 103, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Незавершенный развоз и заказы не влияют на зарплату
        # но влияют на рейтинг
        response = self.request_get_couriers_detail(3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rating', response.data)
        self.assertIn('earning', response.data)
        # Зарплата велокурьера за один полный развоз 1 * 500 * 5
        self.assertEqual(response.data['earning'], 2500)
        # Рейтинг с минимальным средним временем развоза 60 секунд ~ 4.92
        self.assertEqual(response.data['rating'], 4.92)

    def test_courier_detail_with_two_complete_assign(self):
        """Курьер выполнил два развоза. Зарплата и рейтинг учитывают оба"""
        payload = self.correct_post_courier_payload
        self.request_post_couriers(payload)
        # Создаем и назначаем заказы
        payload = self.orders_correct
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Завершаем один заказ с id = 101
        format_datetime = '%Y-%m-%dT%H:%M:%S.%f%z'
        now = datetime.datetime.now() + datetime.timedelta(minutes=3)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 101, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Завершаем один заказ с id = 102
        now = datetime.datetime.now() + datetime.timedelta(minutes=5)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 102, 'complete_time': now}
        self.request_post_orders_complete(payload)

        assign = Assign.objects.get(courier__pk=3)
        self.assertTrue(assign.is_complete)

        # Формируем второе назначение
        payload = {'data': [
            {
                'order_id': 103,
                'weight': 0.23,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 104,
                'weight': 1,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Завершаем один заказ с id = 103
        now = datetime.datetime.now() + datetime.timedelta(minutes=1)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 103, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Завершаем один заказ с id = 104
        now = datetime.datetime.now() + datetime.timedelta(minutes=2)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 104, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Незавершенный развоз и заказы не влияют на зарплату
        # но влияют на рейтинг
        response = self.request_get_couriers_detail(3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rating', response.data)
        self.assertIn('earning', response.data)
        # Зарплата велокурьера за один полный развоз 2 * 500 * 5
        self.assertEqual(response.data['earning'], 5000)
        # Рейтинг с минимальным средним временем развоза 60 секунд ~ 4.92
        self.assertEqual(response.data['rating'], 4.92)

    def test_courier_detail_with_two_complete_assign_change_type_courier(self):
        """
        Курьер выполнил один развоз на велотранспорте, а второй на машине.
        Зарплата учитывает оба типа транспортного средства
        """
        payload = self.correct_post_courier_payload
        self.request_post_couriers(payload)
        # Создаем и назначаем заказы
        payload = self.orders_correct
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Завершаем один заказ с id = 101
        format_datetime = '%Y-%m-%dT%H:%M:%S.%f%z'
        now = datetime.datetime.now() + datetime.timedelta(minutes=3)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 101, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Завершаем один заказ с id = 102
        now = datetime.datetime.now() + datetime.timedelta(minutes=5)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 102, 'complete_time': now}
        self.request_post_orders_complete(payload)

        assign = Assign.objects.get(courier__pk=3)
        self.assertTrue(assign.is_complete)

        # меняем тип курьера
        response = self.request_patch_courier({'courier_type': 'car'}, 3)

        # Формируем второе назначение
        payload = {'data': [
            {
                'order_id': 103,
                'weight': 0.23,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 104,
                'weight': 1,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Завершаем один заказ с id = 103
        now = datetime.datetime.now() + datetime.timedelta(minutes=1)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 103, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Завершаем один заказ с id = 104
        now = datetime.datetime.now() + datetime.timedelta(minutes=2)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 104, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Незавершенный развоз и заказы не влияют на зарплату
        # но влияют на рейтинг
        response = self.request_get_couriers_detail(3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rating', response.data)
        self.assertIn('earning', response.data)

        # Зарплата велокурьера за один полный развоз на велосипеде 1 * 500 * 5
        # И один полный развоз на машине 1 * 500 * 9
        self.assertEqual(response.data['earning'], 7000)
        # Рейтинг с минимальным средним временем развоза 60 секунд ~ 4.92
        self.assertEqual(response.data['rating'], 4.92)

    def test_courier_detail_one_assign_change_type_courier(self):
        """
        Курьер выполнил один развоз пешком, на велотранспорте и на машине.
        Зарплата учитывает все типы транспортного средства
        """
        payload = self.correct_post_courier_payload
        self.request_post_couriers(payload)
        # Создаем и назначаем заказы
        payload = {'data': [
            {
                'order_id': 101,
                'weight': 0.23,
                'region': 2,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 102,
                'weight': 1,
                'region': 2,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 103,
                'weight': 0.23,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 104,
                'weight': 1,
                'region': 14,
                'delivery_hours': ['09:00-18:00']
            }
        ]}

        self.request_post_orders(payload)
        self.request_post_orders_assign({'courier_id': 3})

        # Завершаем один заказ с id = 101
        format_datetime = '%Y-%m-%dT%H:%M:%S.%f%z'
        now = datetime.datetime.now() + datetime.timedelta(minutes=3)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 101, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # меняем тип курьера
        response = self.request_patch_courier({'courier_type': 'foot'}, 3)

        # Завершаем один заказ с id = 102
        now = datetime.datetime.now() + datetime.timedelta(minutes=5)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 102, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # меняем тип курьера
        response = self.request_patch_courier({'courier_type': 'car'}, 3)

        # Завершаем один заказ с id = 103
        now = datetime.datetime.now() + datetime.timedelta(minutes=1)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 103, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Завершаем один заказ с id = 104
        now = datetime.datetime.now() + datetime.timedelta(minutes=2)
        now = datetime.datetime.strftime(now, format_datetime)[:-4] + 'Z'
        payload = {'courier_id': 3, 'order_id': 104, 'complete_time': now}
        self.request_post_orders_complete(payload)

        # Незавершенный развоз и заказы не влияют на зарплату
        # но влияют на рейтинг
        response = self.request_get_couriers_detail(3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rating', response.data)
        self.assertIn('earning', response.data)

        # Зарплата велокурьера за один полный развоз:
        # 5 * 500 = 2500, не учитывает смену типа т/с
        self.assertEqual(response.data['earning'], 2500)
        # Рейтинг с минимальным средним временем развоза 60 секунд ~ 4.92
        self.assertEqual(response.data['rating'], 4.92)


class TestAPIOrders(TestCase, MixinAPI):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.correct_post_order_payload = {'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'region': 12,
                'delivery_hours': ['09:00-18:00']
            },
        ]}
        cls.complete_data = {
            'courier_id': 3,
            'order_id': 1,
            'complete_time': '2021-08-10T10:33:01.42Z'
        }
        cls.orders_1_2_test = {'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'region': 22,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 2,
                'weight': 15,
                'region': 22,
                'delivery_hours': ['09:00-18:00']
            }
        ]}

    def test_post_orders_correct(self):
        """
        Проверка успешного запроса на добавление заказов.
        Должен вернуть HTTP_201_CREATE
        """
        payload = TestAPIOrders.orders_1_2_test
        response = self.request_post_orders(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

    def test_post_orders_incorrect_weight(self):
        """
        Проверка запроса с пустым/некорректным weight.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'order_id': 1,
                'weight': 99,
                'region': 12,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 2,
                'weight': -15,
                'region': 1,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 3,
                'weight': None,
                'region': 1,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        response = self.request_post_orders(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_incorrect_region(self):
        """
        Проверка запроса с пустым и/или некорректным region.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'region': -12,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 2,
                'weight': 15,
                'region': 1.4,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        response = self.request_post_orders(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_incorrect_delivery_hours(self):
        """
        Проверка запроса с пустым и/или некорректным delivery_hours.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'region': 12,
                'delivery_hours': ['0900-18:00']
            },
            {
                'order_id': 2,
                'weight': 15,
                'region': 1,
                'delivery_hours': []
            }
        ]}
        response = self.request_post_orders(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_empty(self):
        """Проверка пустого запроса. Должен вернуть HTTP_400_BAD_REQUEST"""
        incorrect_payload = {'data': []}
        response = self.request_post_orders(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_empty_item(self):
        """
        Проверка непустого запроса. Но у одного из заказов нет полей.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'region': 12,
                'delivery_hours': ['09:00-18:00']
            },
            {}
        ]}
        response = self.request_post_orders(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_incorrect_extra_field_in(self):
        """
        Проверка запроса с несуществующими полями.
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        incorrect_payload = {'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'sleep': 5,
                'region': 12,
                'delivery_hours': ['09:00-18:00']
            },
        ]}
        response = self.request_post_orders(incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_assign_incorrect_courier_id(self):
        """
        Проверка неверного запроса на назначение заказов (плохой courier_id).
        Должен вернуть HTTP_400_BAD_REQUEST
        """
        # Создаем группу заказов
        payload = TestAPIOrders.orders_1_2_test
        response = self.request_post_orders(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

        # Создаем курьеров
        payload = self.data_courier_3_foot_4_bike
        payload['data'].append(
            {
                'courier_id': 5,
                'courier_type': 'car',
                'regions': [2, 14, 22, 24],
                'working_hours': ['00:00-21:00']
            }
        )
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}, {'id': 4}, {'id': 5}]},
                         response.data)

        # назначаем заказы
        # 6 курьер  и остальные из списка не должны получить заказов
        test_case = [6, 1000, 'bad_id', None, []]
        for case in test_case:
            response = self.request_post_orders_assign({'courier_id': case})
            self.assertEqual(response.status_code, 400)

    def test_post_orders_assign_weight_greatest_allowed_weight_courier(self):
        """Заказы превосходящие доступный вес курьера не назначаются"""
        payload = {'data': [
            {
                'order_id': 1,
                'weight': 15,
                'region': 22,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 2,
                'weight': 20,
                'region': 22,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 3,
                'weight': 30,
                'region': 22,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 4,
                'weight': 50,
                'region': 22,
                'delivery_hours': ['09:00-18:00']
            },
        ]}
        response = self.request_post_orders(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            {'orders': [{'id': 1}, {'id': 2}, {'id': 3}, {'id': 4}]},
            response.data)

        # Создаем курьеров
        payload = {'data': [
            {
                'courier_id': 1,
                'courier_type': 'foot',
                'regions': [22],
                'working_hours': ['00:00-23:59']
            },
            {
                'courier_id': 2,
                'courier_type': 'bike',
                'regions': [22],
                'working_hours': ['00:00-23:59']
            },
            {
                'courier_id': 3,
                'courier_type': 'car',
                'regions': [22],
                'working_hours': ['00:00-23:59']
            }
        ]}
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 1}, {'id': 2}, {'id': 3}]},
                         response.data)

        # назначаем заказы
        # 1 курьер не должен был получить заказов
        response = self.request_post_orders_assign({'courier_id': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [])

        # 2 курьер должен был получить заказ 1, остальные не проходят по весу
        response = self.request_post_orders_assign({'courier_id': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # 3 курьер должен был получить заказ 2, 3 остальные не проходят по весу
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 2}, {'id': 3}])

    def test_post_orders_assign_double_assign(self):
        """Заказы не назначаются повторно"""
        # Создаем группу заказов
        payload = TestAPIOrders.orders_1_2_test
        response = self.request_post_orders(payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

        # Создаем курьера
        payload = {'data': [
            {
                'courier_id': 3,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:00-14:00', '09:00-10:00']
            }
        ]}
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}]},
                         response.data)

        # Назначаем первый заказ
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # Повторное назначение недоступно,
        # возвращается список незавершенных заказов из развоза
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

    def test_post_orders_assign_correct(self):
        """
        Проверка успешного запроса на назначение заказов.
        Должен вернуть HTTP_200_OK
        """
        # Создаем группу заказов
        payload = TestAPIOrders.orders_1_2_test
        response = self.request_post_orders(payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

        # Создаем курьеров
        payload = {'data': [
            {
                'courier_id': 3,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:00-14:00', '09:00-10:00']
            },
            {
                'courier_id': 4,
                'courier_type': 'bike',
                'regions': [22],
                'working_hours': ['09:00-18:00']
            },
            {
                'courier_id': 5,
                'courier_type': 'car',
                'regions': [2, 14, 22, 24],
                'working_hours': ['00:00-21:00']
            }
        ]}
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}, {'id': 4}, {'id': 5}]},
                         response.data)

        # назначаем заказы
        # 3 курьер должен был получить только заказ id=1
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # 4 курьер должен был получить только заказ id=2
        response = self.request_post_orders_assign({'courier_id': 4})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 2}])

        # 5 курьер не должен был получить заказов, в ответе нет assign_time
        response = self.request_post_orders_assign({'courier_id': 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [])
        self.assertNotIn('assign_time', response.data)

    def test_assign_to_cancel_order(self):
        """Отмененный заказ доступен для других курьеров"""
        # Создаем группу заказов
        payload = TestAPIOrders.orders_1_2_test
        response = self.request_post_orders(payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

        # Создаем курьеров
        payload = {'data': [
            {
                'courier_id': 3,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:00-14:00', '09:00-10:00']
            },
            {
                'courier_id': 4,
                'courier_type': 'bike',
                'regions': [22],
                'working_hours': ['09:00-18:00']
            },
            {
                'courier_id': 5,
                'courier_type': 'car',
                'regions': [2, 14, 22, 24],
                'working_hours': ['00:00-21:00']
            }
        ]}
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}, {'id': 4}, {'id': 5}]},
                         response.data)

        # назначаем заказы
        # 3 курьер должен был получить только заказ id=1
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # Отменяем заказ id=1
        order = Order.objects.get(pk=1)
        order.cancel_assign()

        # 5 курьер должен был получить заказы id=1, 2
        response = self.request_post_orders_assign({'courier_id': 5})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 2}, {'id': 1}])

    def test_assign_to_courier_with_non_complete_assign(self):
        """Нельзя назначить новый развоз, если курьер не завершил предыдущий"""
        # Создаем группу заказов
        payload = {'data': [
            {
                'order_id': 1,
                'weight': 0.23,
                'region': 22,
                'delivery_hours': ['09:00-18:00']
            },
            {
                'order_id': 2,
                'weight': 9.78,
                'region': 22,
                'delivery_hours': ['09:00-18:00']
            }
        ]}
        response = self.request_post_orders(payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

        # Создаем курьеров
        payload = {'data': [
            {
                'courier_id': 300,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:00-14:00', '09:00-10:00']
            },
            {
                'courier_id': 4,
                'courier_type': 'bike',
                'regions': [22],
                'working_hours': ['09:00-18:00']
            },
            {
                'courier_id': 5,
                'courier_type': 'car',
                'regions': [2, 14, 22, 24],
                'working_hours': ['00:00-21:00']
            }
        ]}
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 300}, {'id': 4}, {'id': 5}]},
                         response.data)
        # назначаем заказы
        # 3 курьер должен был получить только заказ id=1
        response = self.request_post_orders_assign({'courier_id': 300})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # 3 курьер не должен получить заказ id=2
        response = self.request_post_orders_assign({'courier_id': 300})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # завершаем развоз из одного заказа
        correct_payload = {
            'courier_id': 300,
            'order_id': 1,
            'complete_time': '2021-08-10T10:33:01.42Z'
        }
        self.request_post_orders_complete(correct_payload)

        # 3 курьер должен получить заказ id=2
        response = self.request_post_orders_assign({'courier_id': 300})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 2}])

        # Первый развоз завершен, а второй нет
        courier = Courier.objects.get(pk=300)
        assign = courier.assign.all()
        self.assertEqual([a.is_complete for a in assign], [True, False])

    def test_post_orders_complete_incorrect_order_id(self):
        """Некорректное завершение, заказ не существует"""
        correct_payload = TestAPIOrders.complete_data
        response = self.request_post_orders_complete(correct_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_complete_incorrect_not_assign_order(self):
        """Некорректное завершение, заказ не назначен"""
        payload = TestAPIOrders.orders_1_2_test
        response = self.request_post_orders(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # завершаем заказы
        correct_payload = TestAPIOrders.complete_data
        response = self.request_post_orders_complete(correct_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_complete_incorrect_courier_id(self):
        """Некорректный/несуществующий id курьера"""
        payload = TestAPIOrders.orders_1_2_test
        response = self.request_post_orders(payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # завершаем заказы
        payload = TestAPIOrders.complete_data
        test_case = [4, 1000, -1, 'foo', None, []]
        for case in test_case:
            payload['courier_id'] = case
            response = self.request_post_orders_complete(payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_complete_incorrect_courier_id_other_order(self):
        """Некорректный id курьера, заказ назначен другому исполнителю"""
        # Создаем группу заказов
        payload = TestAPIOrders.orders_1_2_test
        response = self.request_post_orders(payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)
        # Создаем курьера
        payload = {'data': [
            {
                'courier_id': 3,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:00-14:00', '09:00-10:00']
            },
            {
                'courier_id': 4,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:00-14:00', '09:00-10:00']
            }
        ]}
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}, {'id': 4}]},
                         response.data)

        # Назначаем заказы
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])
        # завершаем заказы
        payload = TestAPIOrders.complete_data
        test_case = [4, 1000, -1, 'foo', None, []]
        for case in test_case:
            payload['courier_id'] = case
            response = self.request_post_orders_complete(payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_orders_complete_correct(self):
        """Успешное завершение заказов"""
        # Создаем группу заказов
        payload = TestAPIOrders.orders_1_2_test
        response = self.request_post_orders(payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

        # Создаем курьера
        payload = {'data': [
            {
                'courier_id': 3,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:00-14:00', '09:00-10:00']
            }
        ]}
        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}]},
                         response.data)

        # Назначаем заказы
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # завершаем заказы
        correct_payload = TestAPIOrders.complete_data
        response = self.request_post_orders_complete(correct_payload)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['order_id'], 1)

    def test_post_orders_complete_incorrect_complete_time(self):
        """Некорректное время завершение заказа, невозможно завершить"""
        # Создаем группу заказов
        payload = TestAPIOrders.orders_1_2_test

        response = self.request_post_orders(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'orders': [{'id': 1}, {'id': 2}]}, response.data)

        # Создаем курьера
        payload = {'data': [
            {
                'courier_id': 3,
                'courier_type': 'foot',
                'regions': [2, 22, 24],
                'working_hours': ['11:00-14:00', '09:00-10:00']
            }
        ]}

        response = self.request_post_couriers(payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual({'couriers': [{'id': 3}]},
                         response.data)

        # Назначаем заказы
        response = self.request_post_orders_assign({'courier_id': 3})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['orders'], [{'id': 1}])

        # завершаем заказы в прошлом веке,
        # на секунду раньше чем назначили и т.д
        payload = TestAPIOrders.complete_data
        test_case = ['1900-01-10T10:33:01.42Z',
                     None, 0, 1000, 'abacaba', [], [None], [0], [1000],
                     datetime.datetime.now() - datetime.timedelta(seconds=1)]
        for case in test_case:
            if isinstance(case, datetime.datetime):
                format = '%Y-%m-%dT%H:%M:%S.%f%z'
                case = datetime.datetime.strftime(case, format)[:-4] + 'Z'
            payload['complete_time'] = case
            response = self.request_post_orders_complete(payload)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            payload_without_time = {'courier_id': 3,
                                    'order_id': payload['order_id']}
            response = self.request_post_orders_complete(payload_without_time)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            response = self.request_post_orders_complete({})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
