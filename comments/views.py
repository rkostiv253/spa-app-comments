from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from comments.models import Comment, User
from comments.services import (
    add_comment,
    update_comment,
    delete_comment,
    get_all_comments,
    get_user_comments,
    get_comment_by_id
)
from comments.serializers import CommentSerializer


class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        comments = get_all_comments()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        text = request.data.get("text")
        parent_id = request.data.get("parent")

        if not text or not text.strip():
            return Response(
                {"detail": "Text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        parent = None
        if parent_id:
            parent = get_object_or_404(Comment, id=parent_id)

        comment = add_comment(
            user=request.user,
            text=text.strip(),
            parent=parent
        )

        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserCommentListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        comments = get_user_comments(user=user)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommentDetailView(APIView):

    def get(self, request, comment_id):
        comment = get_comment_by_id(comment_id=comment_id)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        text = request.data.get("text")

        if not text or not text.strip():
            return Response(
                {"detail": "Text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated = update_comment(
            user=request.user,
            comment=comment,
            text=text.strip()
        )

        if updated is None:
            return Response(
                {"detail": "You cannot edit this comment."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommentSerializer(updated)
        return Response(serializer.data)

    def patch(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        text = request.data.get("text")

        if not text or not text.strip():
            return Response(
                {"detail": "Text is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        updated = update_comment(
            user=request.user,
            comment=comment,
            text=text.strip()
        )

        if updated is None:
            return Response(
                {"detail": "You cannot edit this comment."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CommentSerializer(updated)
        return Response(serializer.data)

    def delete(self, request, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)

        deleted = delete_comment(
            user=request.user,
            comment=comment
        )

        if not deleted:
            return Response(
                {"detail": "You cannot delete this comment."},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
