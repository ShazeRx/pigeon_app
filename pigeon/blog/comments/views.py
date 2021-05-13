from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from pigeon.blog.comments.pagination import CommentPagination
from pigeon.blog.comments.serializers import CommentSerializer, GlobalCommentSerializer
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

    def get_serializer_context(self):
        context = super(CommentViewSet, self).get_serializer_context()
        context.update({'post_id': self.kwargs['post_pk']})
        return context


class GlobalCommentViewSet(viewsets.ModelViewSet):
    """
        Viewset for global comments
        """
    serializer_class = GlobalCommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination

    def get_queryset(self):
        """
        Get queryset of comments
        :return:
        """
        return Comment.objects.filter(post=self.kwargs['post_pk'])

    def get_serializer_context(self):
        context = super(GlobalCommentViewSet, self).get_serializer_context()
        context.update({'post_id': self.kwargs['post_pk']})
        return context
