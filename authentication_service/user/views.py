from rest_framework.response import Response
from rest_framework import status, viewsets, authentication, permissions
from .models import *
from .serializers import*
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
import subprocess

class VerifyView(APIView):
    @swagger_auto_schema(manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authorization token", type=openapi.TYPE_STRING)])
    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token is None:
            return Response({'error': 'No token provided'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            token_obj = Token.objects.get(key=token)
        except Token.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)

        if not token_obj.user.is_active:
            return Response({'error': 'User not active'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'message': 'Token is valid'})
    
def mx_call(function, args):
    # TODO: need to use "str:[arg]" for string arguments
    # TODO: strings are probably base64 encoded
    cmd = f"mxpy contract call {address} \
            --recall-nonce --pem=${pem} --gas-limit=50000000 \
            --function=\"{function}\" --arguments {' '.join(args)} --send"
    return subprocess.run(cmd, shell=True, capture_output=True).stdout.decode()


class BalanceView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authorization token", type=openapi.TYPE_STRING)],
        operation_description="API to get user balance",
        responses={200: openapi.Response(description='OK')},
    )
    def get(self, request, format=None):
        print(request.user)
        
        user = request.user.username
        password = request.user.password  # Replace with the actual way to get the user's password
        return Response({"balance": mx_call("balance", [user, password])})


class TransferView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="API for transferring funds",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'recipient': openapi.Schema(type=openapi.TYPE_STRING, description='Recipient'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount'),
            },
        ),
        responses={200: openapi.Response(description='OK')},
    )
    def post(self, request, format=None):
        user = request.user.username
        password = request.user.password  # Replace with the actual way to get the user's password
        recipient = request.data.get('recipient')
        amount = request.data.get('amount')
        return Response({"result": mx_call("transfer", [user, password, recipient, amount])})


class CreateView(APIView):
    @swagger_auto_schema(
        operation_description="API for creating a user",
        manual_parameters=[
            openapi.Parameter('user', openapi.IN_QUERY, description='user', type=openapi.TYPE_STRING),
            openapi.Parameter('password', openapi.IN_QUERY, description='password', type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response(description='OK')},
    )
    def post(self, request, format=None):
        user = request.data.get("user")
        password = request.data.get("password")
        return Response({"result": mx_call("create", [user, password])})


class MintView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="API for minting funds",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'recipient': openapi.Schema(type=openapi.TYPE_STRING, description='Recipient'),
                'amount': openapi.Schema(type=openapi.TYPE_NUMBER, description='Amount'),
            },
        ),
        responses={200: openapi.Response(description='OK')},
    )
    def post(self, request, format=None):
        recipient = request.data.get("recipient")
        amount = request.data.get("amount")
        return Response({"result": mx_call("mint", [recipient, amount])})


class HistoryView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="API for getting transaction history",
        manual_parameters=[
            openapi.Parameter('key', openapi.IN_QUERY, description='Key', type=openapi.TYPE_STRING),
        ],
        responses={200: openapi.Response(description='OK')},
    )
    def get(self, request, format=None):
        key = request.data.get("key")
        user = request.user.username
        password = request.user.password
        return Response({"result": mx_call("history", [key, user, password])})