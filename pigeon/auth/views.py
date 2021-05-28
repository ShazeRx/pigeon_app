from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView
from pigeon.auth.serializers import UserSerializer
from .utils import MailSenderUtil
import os
import jwt

class LoginView(APIView):
    """
    View for login
    """

    def post(self, request: Request) -> Response:
        """
        Enpoint for authenticate and login user
        :param request: Pure http request
        :return: If user is authenticated and is active then returns pair of tokens (refresh,access),
         if not then 401 code will be returned
        """
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        serializer = UserSerializer(user)
        if user is not None and user.is_active:
            return Response(status=200, data=serializer.get_token(user))
        return Response(status=status.HTTP_403_FORBIDDEN)


class RegisterView(APIView):
    """
    View for registering user
    """



class VerifyEmailView(GenericAPIView):
    """
    View for verifying an email
    """
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(jwt=token, key=os.environ.get('SECRET_KEY'), algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True;
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'email': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)