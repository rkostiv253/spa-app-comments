from django.contrib import admin

from comments.models import Comment, CommentVote, CommentBookmark

admin.register(Comment)
admin.register(CommentVote)
admin.register(CommentBookmark)
