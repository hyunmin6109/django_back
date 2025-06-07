from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Post, Comment, PostImage, Like


class PostImageInline(admin.TabularInline):
    """게시물 이미지 인라인"""
    model = PostImage
    extra = 1
    readonly_fields = ['created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """카테고리 관리자"""
    
    list_display = ['name', 'post_type', 'color_preview', 'order', 'is_active', 'created_at']
    list_filter = ['post_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['post_type', 'order']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('name', 'description', 'post_type')}),
        ('디자인', {'fields': ('color', 'icon')}),
        ('정렬 및 상태', {'fields': ('order', 'is_active')}),
        ('시스템정보', {'fields': ('id', 'created_at', 'updated_at')}),
    )

    def color_preview(self, obj):
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
                obj.color
            )
        return "-"
    color_preview.short_description = '색상'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """게시물 관리자"""
    
    list_display = ['title', 'user', 'post_type', 'category', 'status', 'view_count', 'like_count', 'comment_count', 'is_pinned', 'created_at']
    list_filter = ['post_type', 'status', 'category', 'is_anonymous', 'is_pinned', 'is_solved', 'created_at']
    search_fields = ['title', 'content', 'user__name', 'user__email']
    ordering = ['-is_pinned', '-created_at']
    readonly_fields = ['id', 'view_count', 'like_count', 'comment_count', 'created_at', 'updated_at']
    inlines = [PostImageInline]
    
    fieldsets = (
        (None, {'fields': ('user', 'category', 'post_type', 'title', 'content')}),
        ('상태 및 옵션', {'fields': ('status', 'is_anonymous', 'is_solved', 'is_pinned')}),
        ('통계', {'fields': ('view_count', 'like_count', 'comment_count')}),
        ('시스템정보', {'fields': ('id', 'created_at', 'updated_at', 'deleted_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """댓글 관리자"""
    
    list_display = ['content_preview', 'user', 'post_title', 'like_count', 'depth', 'is_anonymous', 'created_at']
    list_filter = ['depth', 'is_anonymous', 'created_at']
    search_fields = ['content', 'user__name', 'post__title']
    ordering = ['-created_at']
    readonly_fields = ['id', 'like_count', 'depth', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'post', 'parent', 'content')}),
        ('옵션', {'fields': ('is_anonymous',)}),
        ('통계 및 구조', {'fields': ('like_count', 'depth')}),
        ('시스템정보', {'fields': ('id', 'created_at', 'updated_at', 'deleted_at')}),
    )

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '내용 미리보기'

    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = '게시물 제목'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    """게시물 이미지 관리자"""
    
    list_display = ['post', 'image_preview', 'alt_text', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['post__title', 'alt_text']
    ordering = ['post', 'order']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        (None, {'fields': ('post', 'image_url', 'alt_text', 'order')}),
        ('시스템정보', {'fields': ('id', 'created_at', 'deleted_at')}),
    )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image_url)
        return "-"
    image_preview.short_description = '이미지 미리보기'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """좋아요 관리자"""
    
    list_display = ['user', 'target_type', 'target_preview', 'created_at']
    list_filter = ['target_type', 'created_at']
    search_fields = ['user__name', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'target_preview']
    
    fieldsets = (
        (None, {'fields': ('user', 'target_type', 'target_id')}),
        ('대상 정보', {'fields': ('target_preview',)}),
        ('시스템정보', {'fields': ('id', 'created_at')}),
    )

    def target_preview(self, obj):
        target_obj = obj.target_object
        if target_obj:
            if obj.target_type == 'post':
                return f"게시물: {target_obj.title}"
            elif obj.target_type == 'comment':
                content = target_obj.content[:30] + '...' if len(target_obj.content) > 30 else target_obj.content
                return f"댓글: {content}"
        return "대상을 찾을 수 없음"
    target_preview.short_description = '대상 미리보기'
