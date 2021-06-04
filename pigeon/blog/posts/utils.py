from collections import OrderedDict


class PostSerializerUtils:
    @staticmethod
    def add_values_to_dict(dict: dict, **kwargs):
        data = OrderedDict()
        data.update(dict)
        for key,value in kwargs.items():
            data[key] = value
        return data
