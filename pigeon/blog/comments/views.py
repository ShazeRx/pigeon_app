from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from pigeon.blog.comments.pagination import CommentPagination
from pigeon.blog.comments.serializers import CommentSerializer
from pigeon.models import Comment


class CommentViewSet(viewsets.ModelViewSet):
    """
    Viewset for comments
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination

    def get_queryset(self):
        """
        Get queryset of comments
        :return:
        """
        return Comment.objects.filter(post=self.kwargs['post_pk']).order_by('created_at')

    def get_serializer_context(self) -> CommentSerializer:
        context = super(CommentViewSet, self).get_serializer_context()
        context.update({'post_id': self.kwargs['post_pk']})
        return context

    def destroy(self, request, *args, **kwargs) -> Response:
        comment = Comment.objects.get(id=kwargs.get('pk'))
        serializer = self.get_serializer(comment)
        serializer.remove()
        return Response(status=HTTP_200_OK)
