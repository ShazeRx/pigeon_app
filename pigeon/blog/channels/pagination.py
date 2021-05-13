from rest_framework.pagination import PageNumberPagination


class ChannelPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'channel_size'
    max_page_size = 12
