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
from .utils import mx_contract, mx_query
import re


def process_balance(data):
    pattern = re.compile(r'\"number\": (\d+)')
    if pattern.search(data) is None:
        return 0
    return int(pattern.search(data).group(1))

class BalanceView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authorization token", type=openapi.TYPE_STRING)],
        operation_description="API to get user balance",
        responses={200: openapi.Response(description='OK')},
    )
    def get(self, request, format=None):
        return Response({"balance": process_balance(mx_query("get_account_balance", [request.user.username]))})


class TransferView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="API for transferring funds",
        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authorization token", type=openapi.TYPE_STRING)],
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
        user = request.user
        recipient = request.data.get('recipient')
        amount = request.data.get('amount')
        return Response({"result": mx_contract(user.pem_key, "transfer", [user.username, recipient, amount])})


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
        user = request.user
        amount = request.data.get("amount")
        user = request.user.username
        return Response({"result": mx_contract(user.pem_key, "mint", [user.username, amount])})


def process_history(data):
    pattern = re.compile(r'"hex": "([0-9a-fA-F]+)"')
    hex_data = pattern.search(data).group(1)
    lines = bytes.fromhex(hex_data).split(b'\n')
    transactions = []
    for l in lines[:-1]:
        ammount, sender, receiver = l.split(b' ')
        transactions.append({
            'ammount': int.from_bytes(ammount, byteorder='big'),
            'sender': sender.decode(),
            'receiver': receiver.decode()
        })
    return transactions

class HistoryView(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        manual_parameters=[openapi.Parameter('Authorization', openapi.IN_HEADER, description="Authorization token", type=openapi.TYPE_STRING)],
        operation_description="API to getting user transaction history",
        responses={200: openapi.Response(description='OK')},
    )
    def get(self, request, format=None):
        key = request.data.get("key")
        user = request.user.username
        password = request.user.password
        return Response({"result": process_history(mx_query("get_account_history", [request.user.username]))})