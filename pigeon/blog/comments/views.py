from rest_framework import viewsets
from rest_framework.response import Response
from pigeon.blog.comments.serializers import CommentSerializer
from pigeon.models import Comment
from rest_framework.permissions import IsAuthenticated


class CommentViewSet(viewsets.ModelViewSet):
    """
    Viewset for comments
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get queryset of comments
        :return:
        """
        return Comment.objects.filter(post=self.kwargs['post_pk'])

    def list(self, request, *args, **kwargs):
        """
        Get all comments for given post as post_pk
        :param request: GET with following url structure /posts/<post_pk>/comments/
        :param args:
        :param kwargs:
        :return:
        """
        queryset = Comment.objects.filter(post=kwargs['post_pk'])
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Create comment for given post as post_pk
        :param request:  POST with following url structure /posts/<post_pk>/comments/ with following JSON structure
        {
            "user":<user_id>,
            "body":"some_body"
        }
        :param args:
        :param kwargs:
        :return:
        """
        serializer = CommentSerializer(data=request.data, context={
            'request': request, 'post_id': kwargs['post_pk']})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
