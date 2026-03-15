from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):

    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "user", "text", "created_at", "updated_at", "parent", "replies")
        read_only_fields = ("id", "user", "created_at", "updated_at")

    def get_replies(self, obj):
        return CommentSerializer(obj.replies.all(), many=True).data
