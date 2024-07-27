import re
import logging
import json
import requests
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Account, Destination
from .utils import CommonUtils
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

CommonUtils.setup_logging()
logger = logging.getLogger(__name__)


# swagger doc info
schema_view = get_schema_view(
    openapi.Info(
        title="DATA PUSHER",
        default_version="V1",
        description="APIs for ",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="yogeshkrishnan.cse@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)


# HealthView to check server status
class HealthView(APIView):
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    @swagger_auto_schema(
        operation_description="Check if server is active or not",
        responses={200: "SUCCESS"},
    )
    def get(self, request):
        """
            @description: This API used to check if server is active or not
            @param request:
            @return: "SUCCESS"
        """
        response = {"status": "success"}
        return Response(response)


# AccountView for Accounts CRUD operations
class AccountView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve account details",
        manual_parameters=[
            openapi.Parameter('account_id', openapi.IN_QUERY, description="Account ID", type=openapi.TYPE_STRING),
        ],
        responses={
            200: "Account details",
            400: "Bad request",
            404: "Account not found",
        },
    )
    def get(self, request):
        """
            @description: This API used to retrieve account details
            @param request: account_id
            @return: Account details
        """
        try:
            account_id = request.query_params.get('account_id')
            account = Account.objects.get(account_id=account_id)
            account_details = {
                "account_name": account.account_name,
                "email": account.email,
                "website": account.website,
                "secret_key": account.secret_key,
            }
            logger.info("Account retrieved for {}".format(account_id))
            return CommonUtils.generate_response(data=account_details)
        except Account.DoesNotExist:
            return CommonUtils.generate_response(status_code=status.HTTP_404_NOT_FOUND, message="Account not found")
        except Exception as e:
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=str(e))

    @swagger_auto_schema(
        operation_description="Create a new account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'account_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'website': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['account_name', 'email'],
        ),
        responses={
            201: "Account details",
            400: "Bad request",
            409: "Conflict",
        },
    )
    def post(self, request):
        """
            @description: This API used to create a new account
            @param request: account_name*, email*, website
            @return: Account details
        """
        try:
            data = request.data
            account_name = data.get('account_name')
            email = data.get('email')
            website = data.get('website')
            if account_name is None or account_name == "":
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide account_name")
            if email is None:
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide email")
            # Validate email format
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Invalid email format")

            # Validate website format
            if website is not None:
                if not re.match(r'^(http|https)://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,63}(/\S*)?$', website):
                    return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                         message="Invalid website format")

            secret_key = CommonUtils.generate_random_key(20)
            account = Account.objects.create(account_name=account_name.upper(), email=email, website=website,
                                             secret_key=secret_key)
            account_details = {
                "account_id": account.account_id,
                "account_name": account.account_name,
                "email": account.email,
                "website": account.website,
                "secret_key": account.secret_key,
            }
            logger.info("New account created: {}".format(account_name))
            return CommonUtils.generate_response(data=account_details)
        except IntegrityError as e:
            error_message = str(e)
            if 'UNIQUE constraint failed' in error_message:
                if 'email' in error_message:
                    field_name = 'Email'
                elif 'account_name' in error_message:
                    field_name = 'Account name'
                elif 'website' in error_message:
                    field_name = 'Website'
                return CommonUtils.generate_response(status_code=status.HTTP_409_CONFLICT,
                                                     message=f"{field_name} already taken")
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=error_message)
        except Exception as e:
            logger.error("Error creating account: {}".format(str(e)))
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=str(e))

    @swagger_auto_schema(
        operation_description="Update an existing account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'account_id': openapi.Schema(type=openapi.TYPE_STRING),
                'account_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'website': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['account_id'],
        ),
        responses={
            200: "Updated Account details",
            400: "Bad request",
            404: "Account not found",
            409: "Conflict",
        },
    )
    def put(self, request):
        """
            @description: This API used to update an existing account
            @param request: account_id*, account_name, email, website
            @return: Updated account details
        """
        try:
            data = request.data
            account_id = data.get('account_id')
            account = Account.objects.get(account_id=account_id)

            account_name = data.get('account_name', account.account_name).upper()
            email = data.get('email', account.email)
            website = data.get('website', account.website)
            if account_name is None or account_name == "":
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide account_name")
            if email is None:
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide email")
                # Validate email format
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Invalid email format")

                # Validate website format
            if website is not None:
                if not re.match(r'^(http|https)://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,63}(/\S*)?$', website):
                    return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                         message="Invalid website format")
            account.account_name = account_name
            account.email = email
            account.website = website
            account.save()

            account_details = {
                "account_id": account.account_id,
                "account_name": account.account_name,
                "email": account.email,
                "website": account.website,
                "secret_key": account.secret_key,
            }
            logger.info("Account updated: {}".format(account_id))
            return CommonUtils.generate_response(data=account_details)
        except Account.DoesNotExist:
            return CommonUtils.generate_response(status_code=status.HTTP_404_NOT_FOUND, message="Account not found")
        except IntegrityError as e:
            error_message = str(e)
            if 'UNIQUE constraint failed' in error_message:
                if 'email' in error_message:
                    field_name = 'Email'
                elif 'account_name' in error_message:
                    field_name = 'Account name'
                elif 'website' in error_message:
                    field_name = 'Website'
                return CommonUtils.generate_response(status_code=status.HTTP_409_CONFLICT,
                                                     message=f"{field_name} already taken")
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=error_message)
        except Exception as e:
            logger.error("Error updating account: {}".format(str(e)))
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=str(e))

    @swagger_auto_schema(
        operation_description="Delete an existing account",
        manual_parameters=[
            openapi.Parameter('account_id', openapi.IN_QUERY, description="Account ID", type=openapi.TYPE_STRING)
        ],
        responses={
            200: "Success message",
            400: "Bad Request",
            404: "Account not found"
        }
    )
    def delete(self, request):
        """
            @description: This API used to delete an existing account
            @param request: account_id
            @return: Success message
        """
        try:
            account_id = request.data.get('account_id')
            account = Account.objects.get(account_id=account_id)
            account.delete()
            logger.info("Account deleted: {}".format(account_id))
            return CommonUtils.generate_response(message="Account deleted successfully")
        except Account.DoesNotExist:
            return CommonUtils.generate_response(status_code=status.HTTP_404_NOT_FOUND, message="Account not found")
        except Exception as e:
            logger.error("Error deleting account: {}".format(str(e)))
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=str(e))


# DestinationView for Destinations CRUD operations
class DestinationView(APIView):
    @swagger_auto_schema(
        operation_description="Retrieve all destinations for an account",
        manual_parameters=[
            openapi.Parameter('account_id', openapi.IN_QUERY, description="Account ID", type=openapi.TYPE_STRING)
        ],
        responses={
            200: "List of destination details",
            400: "Bad Request",
            404: "Account not found"
        }
    )
    def get(self, request):
        """
        @description: This API is used to retrieve all destinations for an account
        @param request: account_id
        @return: List of destination details
        """
        try:
            account_id = request.query_params.get('account_id')
            account = Account.objects.get(account_id=account_id)
            destinations = Destination.objects.filter(account=account)

            destination_details_list = []
            for destination in destinations:
                destination_details = {
                    "destination_id": destination.id,
                    "account_id": destination.account_id,
                    "url": destination.url,
                    "http_method": destination.http_method,
                    "headers": destination.headers,
                }
                destination_details_list.append(destination_details)

            logger.info("Destinations retrieved for account: {}".format(account_id))
            return CommonUtils.generate_response(data=destination_details_list)
        except Account.DoesNotExist:
            return CommonUtils.generate_response(status_code=status.HTTP_404_NOT_FOUND, message="Account not found")
        except Exception as e:
            logger.error("Error retrieving destinations: {}".format(str(e)))
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=str(e))

    @swagger_auto_schema(
        operation_description="Create a new destination for an account",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'account_id': openapi.Schema(type=openapi.TYPE_STRING),
                'url': openapi.Schema(type=openapi.TYPE_STRING),
                'http_method': openapi.Schema(type=openapi.TYPE_STRING),
                'headers': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            201: "Destination details created successfully",
            400: "Bad Request",
            404: "Account not found"
        }
    )
    def post(self, request):
        """
        @description: This API is used to create a new destination for an account
        @param request: account_id*, url*, http_method*, headers*
        @return: Destination details
        """
        try:
            data = request.data
            account_id = data.get('account_id')
            url = data.get('url')
            http_method = data.get('http_method')
            headers = data.get('headers')
            if account_id is None or account_id == "":
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide account_id")

            if url is None or url == "":
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide url")
            if url is not None:
                if not re.match(r'^(http|https)://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,63}(/\S*)?$', url):
                    return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                         message="Invalid url format")
            if http_method is None or http_method == "":
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide  http_method")

            if headers is None or headers == "":
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide headers")

            # Validate account existence
            account = Account.objects.get(account_id=account_id)

            # Create destination
            destination = Destination.objects.create(account=account, url=url, http_method=http_method, headers=headers)
            destination_details = {
                "destination_id": destination.id,
                "account_id": destination.account_id,
                "url": destination.url,
                "http_method": destination.http_method,
                "headers": destination.headers,
            }
            logger.info("New destination created for account: {}".format(account_id))
            return CommonUtils.generate_response(data=destination_details, status_code=status.HTTP_201_CREATED)
        except Account.DoesNotExist:
            return CommonUtils.generate_response(status_code=status.HTTP_404_NOT_FOUND, message="Account not found")
        except Exception as e:
            logger.error("Error creating destination: {}".format(str(e)))
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=str(e))

    @swagger_auto_schema(
        operation_description="Update an existing destination",
        manual_parameters=[
            openapi.Parameter('destination_id', openapi.IN_QUERY, description="Destination ID",
                              type=openapi.TYPE_STRING)
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'url': openapi.Schema(type=openapi.TYPE_STRING),
                'http_method': openapi.Schema(type=openapi.TYPE_STRING),
                'headers': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: "Updated destination details",
            400: "Bad Request",
            404: "Destination not found"
        }
    )
    def put(self, request):
        """
        @description: This API is used to update an existing destination
        @param request: destination_id*, url, http_method, headers
        @return: Updated destination details
        """
        try:
            data = request.data
            destination_id = data.get('destination_id')
            destination = Destination.objects.get(id=destination_id)

            url = data.get('url', destination.url)
            http_method = data.get('http_method', destination.http_method)
            headers = data.get('headers', destination.headers)
            if url is None or url == "":
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide url")
            if url is not None:
                if not re.match(r'^(http|https)://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,63}(/\S*)?$', url):
                    return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                         message="Invalid url format")
            if http_method is None or http_method == "":
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide  http_method")

            if headers is None or headers == "":
                return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST,
                                                     message="Please provide headers")

            destination.url = url
            destination.http_method = http_method
            destination.headers = headers
            destination.save()

            destination_details = {
                "destination_id": destination.id,
                "account_id": destination.account_id,
                "url": destination.url,
                "http_method": destination.http_method,
                "headers": destination.headers,
            }
            logger.info("Destination updated: {}".format(destination_id))
            return CommonUtils.generate_response(data=destination_details)
        except Destination.DoesNotExist:
            return CommonUtils.generate_response(status_code=status.HTTP_404_NOT_FOUND, message="Destination not found")
        except Exception as e:
            logger.error("Error updating destination: {}".format(str(e)))
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=str(e))

    @swagger_auto_schema(
        operation_description="Delete an existing destination",
        manual_parameters=[
            openapi.Parameter('destination_id', openapi.IN_QUERY, description="Destination ID",
                              type=openapi.TYPE_STRING)
        ],
        responses={
            200: "Success message",
            400: "Bad Request",
            404: "Destination not found"
        }
    )
    def delete(self, request):
        """
        @description: This API is used to delete an existing destination
        @param request: destination_id
        @return: Success message
        """
        try:
            destination_id = request.data.get('destination_id')
            destination = Destination.objects.get(id=destination_id)
            destination.delete()
            logger.info("Destination deleted: {}".format(destination_id))
            return CommonUtils.generate_response(message="Destination deleted successfully")
        except Destination.DoesNotExist:
            return CommonUtils.generate_response(status_code=status.HTTP_404_NOT_FOUND, message="Destination not found")
        except Exception as e:
            logger.error("Error deleting destination: {}".format(str(e)))
            return CommonUtils.generate_response(status_code=status.HTTP_400_BAD_REQUEST, message=str(e))


# approach 1 :  rest api data pusher

class DataHandlerView(APIView):
    @swagger_auto_schema(
        operation_description="Handle data",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'data': openapi.Schema(type=openapi.TYPE_STRING)
            }
        ),
        responses={
            200: "Data sent to destinations successfully",
            400: "Bad Request",
            401: "Unauthenticated"
        }
    )
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return CommonUtils.generate_response(message="Invalid Data", status_code=status.HTTP_400_BAD_REQUEST)

        if 'CL-XTOKEN' not in request.headers:
            return CommonUtils.generate_response(message="Unauthenticated", status_code=status.HTTP_401_UNAUTHORIZED)

        secret_token = request.headers['CL-XTOKEN']
        try:
            account = Account.objects.get(secret_key=secret_token)
        except Account.DoesNotExist:
            return CommonUtils.generate_response(message="Invalid secret token",
                                                 status_code=status.HTTP_401_UNAUTHORIZED)
        destinations = Destination.objects.filter(account=account)
        for destination in destinations:
            url = destination.url
            http_method = destination.http_method
            headers = destination.headers
            if http_method == 'GET':
                params = {**data}
                response = requests.get(url, params=params, headers=headers)
            elif http_method in ['POST', 'PUT']:
                response = requests.request(http_method, url, json=data, headers=headers)
            else:
                return CommonUtils.generate_response(message="Unsupported HTTP method",
                                                     status_code=status.HTTP_400_BAD_REQUEST)

            logger.info("Data sent to destination: {} method:{}  url:{}".format(destination.id, destination.http_method,
                                                                                destination.url))

        return CommonUtils.generate_response(message="Data sent to destinations successfully",
                                             status_code=status.HTTP_200_OK)
