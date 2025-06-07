from django.contrib import admin
from django.utils.html import format_html
from .models import ChatSession, ChatMessage


class ChatMessageInline(admin.TabularInline):
    """채팅 메시지 인라인"""
    model = ChatMessage
    extra = 0
    readonly_fields = ['created_at', 'tokens']
    fields = ['role', 'content', 'tokens', 'created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('created_at')


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """채팅 세션 관리자"""
    
    list_display = ['title', 'user', 'category', 'status', 'message_count', 'total_tokens', 'duration_display', 'created_at']
    list_filter = ['category', 'status', 'created_at']
    search_fields = ['title', 'user__name', 'user__email']
    ordering = ['-last_message_at', '-created_at']
    readonly_fields = ['id', 'message_count', 'duration_minutes', 'created_at', 'updated_at']
    inlines = [ChatMessageInline]
    
    fieldsets = (
        (None, {'fields': ('user', 'title', 'category')}),
        ('세션 정보', {'fields': ('status', 'session_token')}),
        ('통계', {'fields': ('total_tokens', 'message_count', 'duration_minutes')}),
        ('시간 정보', {'fields': ('last_message_at', 'created_at', 'updated_at')}),
        ('시스템정보', {'fields': ('id', 'deleted_at')}),
    )

    def duration_display(self, obj):
        minutes = obj.duration_minutes
        if minutes > 60:
            hours = minutes // 60
            mins = minutes % 60
            return f"{hours}시간 {mins:.0f}분"
        return f"{minutes:.0f}분"
    duration_display.short_description = '지속 시간'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """채팅 메시지 관리자"""
    
    list_display = ['session_title', 'role', 'content_preview', 'tokens', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'session__title', 'session__user__name']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        (None, {'fields': ('session', 'role', 'content')}),
        ('메타데이터', {'fields': ('tokens', 'metadata')}),
        ('시스템정보', {'fields': ('id', 'created_at')}),
    )

    def session_title(self, obj):
        return obj.session.title
    session_title.short_description = '세션 제목'

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = '내용 미리보기'
