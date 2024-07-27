import json
import logging
import requests
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.http import HttpRequest
from rest_framework import status
from account.models import Account, Destination
logger = logging.getLogger(__name__)


# approach 2: websocket data pusher
class DataHandlerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("WebSocket connection established")
        await self.accept()

    async def disconnect(self, close_code):
        logger.info("WebSocket connection closed")

    async def receive(self, text_data):
        data = json.loads(text_data)
        response = await self.handle_data(data)
        await self.send(text_data=json.dumps(response))

    @database_sync_to_async
    def handle_data(self, data):
        request = HttpRequest()
        secret_token = data.get('secret_token')
        try:
            data_payload = data.get('data')
        except json.JSONDecodeError:
            return {"message": "Invalid Data", "status_code": status.HTTP_400_BAD_REQUEST}

        if not secret_token:
            return {"message": "Unauthenticated", "status_code": status.HTTP_401_UNAUTHORIZED}

        try:
            account = Account.objects.get(secret_key=secret_token)
        except Account.DoesNotExist:
            return {"message": "Invalid secret token", "status_code": status.HTTP_401_UNAUTHORIZED}

        destinations = Destination.objects.filter(account=account)
        for destination in destinations:
            url = destination.url
            http_method = destination.http_method
            headers = destination.headers
            if http_method == 'GET':
                params = {**data_payload}
                response = requests.get(url, params=params, headers=headers)
            elif http_method in ['POST', 'PUT']:
                response = requests.request(http_method, url, json=data_payload, headers=headers)
            else:
                return {"message": "Unsupported HTTP method", "status_code": status.HTTP_400_BAD_REQUEST}

            logger.info("Data sent to destination: %s, method: %s, url: %s", destination.id, destination.http_method, destination.url)

        return {"message": "Data sent to destinations successfully", "status_code": status.HTTP_200_OK}
