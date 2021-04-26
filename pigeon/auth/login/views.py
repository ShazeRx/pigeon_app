from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView


class LoginView(APIView):

    def post(self, request, format=None):
        username = password = ''
        username = request.data['username']
        password = request.data['password']
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            token, create = Token.objects.get_or_create(user=user)
            return Response(status=status.HTTP_200_OK, data=str(token))
        return Response(status=status.HTTP_401_UNAUTHORIZED)
