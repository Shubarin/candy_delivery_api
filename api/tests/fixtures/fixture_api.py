import json

from django.test import Client


class MixinAPI:
    client = Client()
    data_courier_3_foot_4_bike = {"data": [
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

    @staticmethod
    def request_post_couriers(payload):
        response = MixinAPI.client.post('/api/v1/couriers/',
                                        data=json.dumps(payload),
                                        content_type='application/json')
        return response

    @staticmethod
    def request_get_couriers_detail(courier_id):
        response = MixinAPI.client.get(f'/api/v1/couriers/{courier_id}/')
        return response

    @staticmethod
    def request_patch_courier(payload, courier_id):
        response = MixinAPI.client.patch(f'/api/v1/couriers/{courier_id}/',
                                         data=json.dumps(payload),
                                         content_type='application/json')
        return response

    @staticmethod
    def request_post_orders(payload):
        response = MixinAPI.client.post('/api/v1/orders/',
                                        data=json.dumps(payload),
                                        content_type='application/json')
        return response

    @staticmethod
    def request_post_orders_assign(payload):
        response = MixinAPI.client.post('/api/v1/orders/assign/',
                                        data=json.dumps(payload),
                                        content_type='application/json')
        return response

    @staticmethod
    def request_post_orders_complete(payload):
        response = MixinAPI.client.post('/api/v1/orders/complete/',
                                        data=json.dumps(payload),
                                        content_type='application/json')
        return response
