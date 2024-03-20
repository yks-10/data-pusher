import secrets
import string
import logging
from rest_framework import status
from rest_framework.response import Response
class CommonUtils(object):

    # generate_random_key for secret_key generation
    @staticmethod
    def generate_random_key(length):
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for i in range(length))

    # setup_logging to provide log format
    @staticmethod
    def setup_logging():
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # generate_response to provide response format
    @staticmethod
    def generate_response(data=None, status_code=status.HTTP_200_OK, message=None):
        response_data = {
            "status": "success" if status_code == status.HTTP_200_OK else "failed",
            "data": data,
            "message": message
        }
        return Response(response_data, status=status_code)