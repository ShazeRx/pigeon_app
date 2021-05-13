from rest_framework.pagination import PageNumberPagination


class CommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'comment_size'
    max_page_size = 20