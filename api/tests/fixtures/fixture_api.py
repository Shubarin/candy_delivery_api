import json

from django.test import Client


class MixinAPI:
    client = Client()

    @staticmethod
    def request_post_couriers(payload):
        response = MixinAPI.client.post('/api/v1/couriers/',
                                        data=json.dumps(payload),
                                        content_type='application/json')
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
