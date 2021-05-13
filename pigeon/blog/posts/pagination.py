from rest_framework.pagination import PageNumberPagination


class PostPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'post_size'
    max_page_size = 24