from rest_framework import serializers
from .models import Post, Category, PostImage, Comment
from api_service.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'post_type', 'color', 'icon']

class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ['id', 'image_url', 'alt_text', 'order']

class PostSerializer(serializers.ModelSerializer):
    images = PostImageSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.UUIDField(write_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'category', 'category_id',
            'post_type', 'status', 'is_anonymous', 'is_solved',
            'is_pinned', 'images', 'user', 'created_at', 'updated_at',
            'view_count', 'like_count', 'comment_count'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'view_count',
            'like_count', 'comment_count', 'user'
        ]

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'user', 'post', 'parent',
            'created_at', 'updated_at', 'is_anonymous',
            'like_count', 'depth', 'replies'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at',
            'like_count', 'depth', 'user'
        ]
    
    def get_replies(self, obj):
        if obj.depth == 0:  # 최상위 댓글인 경우에만 답글 표시
            replies = Comment.objects.filter(
                parent=obj,
                deleted_at__isnull=True
            ).order_by('created_at')
            return CommentSerializer(replies, many=True).data
        return []