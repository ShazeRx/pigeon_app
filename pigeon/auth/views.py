from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import *
from rest_framework.views import APIView

from pigeon.auth.serializers import UserSerializer


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


class RegisterView(CreateAPIView):
    """
    View for registering user
    """
    model = User
    serializer_class = UserSerializer()

    def post(self, request):
        try:
            user = self.serializer_class.create(request.data)
            if user:
                return Response(self.serializer_class.get_token(user), status=HTTP_200_OK)
            return Response(data={'message':'Unexpected error occurred'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            return Response(data={'message': str(e)}, status=HTTP_401_UNAUTHORIZED)
