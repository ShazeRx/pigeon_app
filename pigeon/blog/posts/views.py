from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import *
from pigeon.blog.posts.serializers import PostSerializer
from pigeon.models import Post


class PostViewSet(viewsets.ModelViewSet):
    """
    View for posts
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Get all posts
        """
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True,
                                    context={
                                        'request': request})  # request context need to be passed to return reversed URL of image
        return Response(serializer.data)

    def retrieve(self, request: Request, *args, **kwargs):
        """
        Get post by id. Check check_password_equals() method in PostSerializer class to see example body json structure
        :param request: body can be empty
        :param kwargs: pk is fetched from url after post/ endpoint
        example url /post/1/
        :return: JSON all Post fields except password field
        """
        id = kwargs.get('pk')
        try:
            post = Post.objects.get(id=id)
        except Post.DoesNotExist:
            return Response(data={'message': f'Post not found with id {id}'}, status=HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = PostSerializer(post, context={'request': request})
        if serializer.check_password_equals(request.data, post):
            return Response(serializer.data, status=HTTP_200_OK)
