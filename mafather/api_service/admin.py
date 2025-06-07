from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserChild, Session, SearchLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """사용자 관리자"""
    
    list_display = ['email', 'name', 'auth_provider', 'is_active', 'last_login', 'created_at']
    list_filter = ['auth_provider', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('개인정보', {'fields': ('name', 'profile_image')}),
        ('인증정보', {'fields': ('auth_provider', 'auth_provider_id')}),
        ('권한', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('중요한 날짜', {'fields': ('last_login', 'created_at', 'updated_at', 'deleted_at')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


@admin.register(UserChild)
class UserChildAdmin(admin.ModelAdmin):
    """자녀 정보 관리자"""
    
    list_display = ['name', 'user', 'birth_date', 'gender', 'age_months', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['name', 'user__name', 'user__email']
    ordering = ['-created_at']
    readonly_fields = ['id', 'age_months', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'name', 'birth_date', 'gender')}),
        ('시스템정보', {'fields': ('id', 'age_months', 'created_at', 'updated_at', 'deleted_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    """세션 관리자"""
    
    list_display = ['user', 'token_preview', 'ip_address', 'is_expired', 'created_at', 'expires_at']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['user__email', 'user__name', 'ip_address']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'is_expired']
    
    fieldsets = (
        (None, {'fields': ('user', 'token', 'expires_at')}),
        ('기기정보', {'fields': ('device_info', 'ip_address')}),
        ('시스템정보', {'fields': ('id', 'is_expired', 'created_at', 'updated_at')}),
    )

    def token_preview(self, obj):
        return f"{obj.token[:20]}..." if obj.token else "-"
    token_preview.short_description = '토큰 미리보기'

    def is_expired(self, obj):
        expired = obj.is_expired()
        color = 'red' if expired else 'green'
        text = '만료됨' if expired else '유효함'
        return format_html(f'<span style="color: {color};">{text}</span>')
    is_expired.short_description = '만료 여부'


@admin.register(SearchLog)
class SearchLogAdmin(admin.ModelAdmin):
    """검색 로그 관리자"""
    
    list_display = ['query', 'search_type', 'user', 'results_count', 'ip_address', 'created_at']
    list_filter = ['search_type', 'created_at']
    search_fields = ['query', 'user__email', 'user__name']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        (None, {'fields': ('user', 'query', 'search_type', 'results_count')}),
        ('기술정보', {'fields': ('ip_address', 'user_agent')}),
        ('시스템정보', {'fields': ('id', 'created_at')}),
    )
