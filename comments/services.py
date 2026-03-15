from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404

from .models import Comment, CommentVote, CommentBookmark


def get_all_comments():
    return Comment.objects.all()


def get_user_comments(*, user):
    return (
        Comment.objects
        .filter(user=user, parent=None)
        .select_related("user", "parent")
        .prefetch_related("replies", "replies__replies")
    )


def get_comment_by_id(comment_id):
    return get_object_or_404(
        Comment.objects.prefetch_related("replies"),
        id=comment_id
    )


def add_comment(*, user, text, parent=None):
    return Comment.objects.create(
        user=user,
        text=text,
        parent=parent
    )


def reply_to_comment(*, comment_id):
    comment = Comment.objects.select_for_update().get(pk=comment_id)

    if not comment:
        return False

    else:
        comment.parent = Comment.objects.create(user=comment.parent, text=comment.text)
        comment.save(update_fields=["parent"])

    return True


def update_comment(*, user, comment, text):
    if comment.user != user:
        return None

    comment.text = text
    comment.save(update_fields=["text", "updated_at"])
    return comment


def delete_comment(*, user, comment):
    if comment.user != user:
        return False

    comment.delete()
    return True


@transaction.atomic
def set_comment_vote(*, user, comment, value):
    if value not in (CommentVote.UPVOTE, CommentVote.DOWNVOTE):
        raise ValueError("Invalid vote value")

    comment = Comment.objects.select_for_update().get(pk=comment.pk)
    existing_vote = CommentVote.objects.select_for_update().filter(
        user=user,
        comment=comment
    ).first()

    if existing_vote is None:
        CommentVote.objects.create(user=user, comment=comment, value=value)
        if value == CommentVote.UPVOTE:
            Comment.objects.filter(pk=comment.pk).update(
                upvotes_count=F("upvotes_count") + 1
            )
        else:
            Comment.objects.filter(pk=comment.pk).update(
                downvotes_count=F("downvotes_count") + 1
            )
        return

    if existing_vote.value == value:
        existing_vote.delete()
        if value == CommentVote.UPVOTE:
            Comment.objects.filter(pk=comment.pk).update(
                upvotes_count=F("upvotes_count") - 1
            )
        else:
            Comment.objects.filter(pk=comment.pk).update(
                downvotes_count=F("downvotes_count") - 1
            )
        return

    if existing_vote.value == CommentVote.UPVOTE:
        Comment.objects.filter(pk=comment.pk).update(
            upvotes_count=F("upvotes_count") - 1,
            downvotes_count=F("downvotes_count") + 1
        )
    else:
        Comment.objects.filter(pk=comment.pk).update(
            downvotes_count=F("downvotes_count") - 1,
            upvotes_count=F("upvotes_count") + 1
        )

    existing_vote.value = value
    existing_vote.save(update_fields=["value"])


@transaction.atomic
def toggle_comment_bookmark(*, user, comment):
    existing_bookmark = CommentBookmark.objects.filter(
        user=user,
        comment=comment
    ).first()

    if existing_bookmark:
        existing_bookmark.delete()
        comment.bookmarks_count = max(0, comment.bookmarks_count - 1)
        comment.save(update_fields=["bookmarks_count"])
        return False

    CommentBookmark.objects.create(user=user, comment=comment)
    comment.bookmarks_count += 1
    comment.save(update_fields=["bookmarks_count"])
    return True
