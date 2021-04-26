from rest_framework.generics import CreateAPIView, RetrieveAPIView
from pigeon.auth.serializers import UserSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView


class LoginView(APIView):
    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        serializer = UserSerializer(user)
        if user is not None and user.is_active:
            return Response(status=200, data=serializer.data)
        return Response(status=status.HTTP_401_UNAUTHORIZED)
 

class RegisterView(CreateAPIView):
    model = User
    serializer_class = UserSerializer



