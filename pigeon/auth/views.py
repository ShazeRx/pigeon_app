from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
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
        if user is not None:
            return Response(status=200, data=serializer.get_token(user))
        return Response(data={"message": "User not activated or does not exist"}, status=status.HTTP_403_FORBIDDEN)


class RegisterView(APIView):
    """
    View for registering user
    """
    model = User
    serializer_class = UserSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user_data['tokens'] = serializer.get_token(User.objects.get(id=user_data['id']))
        MailSenderUtil.send_email(request=request, user_data=user_data)
        return Response(data=user_data, status=status.HTTP_201_CREATED)


class VerifyEmailView(GenericAPIView):
    """
    View for verifying an email
    """

    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(jwt=token, key=os.environ.get('SECRET_KEY'), algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'message': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
