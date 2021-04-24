from django.http import HttpResponse
from .models import *

def index(request):
    return HttpResponse('Pigeon!!!')