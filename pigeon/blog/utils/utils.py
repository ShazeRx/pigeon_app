from collections import OrderedDict

from django.contrib.auth.models import User
from django.db.models import QuerySet


class BlogSerializerUtils:
    @staticmethod
    def add_values_to_dict(dict: dict, **kwargs):
        data = OrderedDict()
        data.update(dict)
        for key, value in kwargs.items():
            data[key] = value
        return data

    @staticmethod
    def randomize_password(queryset: QuerySet):
        while True:
            password = User.objects.make_random_password()
            if not queryset.filter(password=password):
                break
        return password
