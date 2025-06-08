from django.urls import path, include
from . import views

urlpatterns = [
    path('posts/', views.get_posts, name='post-list'),
    path('posts/create/', views.create_post, name='post-create'),
    path('posts/<uuid:post_id>/', views.get_post, name='post-detail'),
    path('posts/<uuid:post_id>/like/', views.like_post, name='post-like'),
    path('posts/<uuid:post_id>/comment/', views.comment_post, name='post-comment'),
    path('posts/<uuid:post_id>/comment/<uuid:comment_id>/', views.get_comment, name='comment-detail'),
    path('posts/<uuid:post_id>/comment/<uuid:comment_id>/like/', views.like_comment, name='comment-like'),
    path('posts/<uuid:post_id>/comment/<uuid:comment_id>/delete/', views.delete_comment, name='comment-delete'),
    path('posts/<uuid:post_id>/comment/<uuid:comment_id>/edit/', views.edit_comment, name='comment-edit'),
    path('posts/<uuid:post_id>/comment/<uuid:comment_id>/reply/', views.reply_comment, name='comment-reply'),
]
