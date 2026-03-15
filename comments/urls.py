from django.urls import path
from comments.views import CommentListCreateView, CommentDetailView, UserCommentListView

urlpatterns = [
    path("comments/", CommentListCreateView.as_view()),
    path("comments/<int:comment_id>/", CommentDetailView.as_view()),
    path("user/<int:user_id>/comments", UserCommentListView.as_view()),
]
