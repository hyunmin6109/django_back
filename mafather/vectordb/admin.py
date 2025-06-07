from django.contrib import admin
from django.utils.html import format_html
from .models import DevelopmentRecord, DevelopmentRecordImage, DevelopmentMilestone, ChildMilestone


class DevelopmentRecordImageInline(admin.TabularInline):
    """발달 기록 이미지 인라인"""
    model = DevelopmentRecordImage
    extra = 1
    readonly_fields = ['created_at']


@admin.register(DevelopmentRecord)
class DevelopmentRecordAdmin(admin.ModelAdmin):
    """발달 기록 관리자"""
    
    list_display = ['title', 'child', 'user', 'age_group', 'development_area', 'record_type', 'date', 'created_at']
    list_filter = ['age_group', 'development_area', 'record_type', 'date', 'created_at']
    search_fields = ['title', 'description', 'child__name', 'user__name']
    ordering = ['-date', '-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [DevelopmentRecordImageInline]
    
    fieldsets = (
        (None, {'fields': ('user', 'child', 'title', 'description')}),
        ('분류정보', {'fields': ('age_group', 'development_area', 'record_type', 'date')}),
        ('시스템정보', {'fields': ('id', 'created_at', 'updated_at', 'deleted_at')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


@admin.register(DevelopmentRecordImage)
class DevelopmentRecordImageAdmin(admin.ModelAdmin):
    """발달 기록 이미지 관리자"""
    
    list_display = ['record', 'image_preview', 'order', 'created_at']
    list_filter = ['created_at']
    search_fields = ['record__title']
    ordering = ['record', 'order']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        (None, {'fields': ('record', 'image_url', 'order')}),
        ('시스템정보', {'fields': ('id', 'created_at', 'deleted_at')}),
    )

    def image_preview(self, obj):
        if obj.image_url:
            return format_html('<img src="{}" style="max-height: 50px;" />', obj.image_url)
        return "-"
    image_preview.short_description = '이미지 미리보기'

    def get_queryset(self, request):
        return super().get_queryset(request).filter(deleted_at__isnull=True)


@admin.register(DevelopmentMilestone)
class DevelopmentMilestoneAdmin(admin.ModelAdmin):
    """발달 이정표 관리자"""
    
    list_display = ['title', 'age_group', 'development_area', 'order', 'is_active', 'created_at']
    list_filter = ['age_group', 'development_area', 'is_active', 'created_at']
    search_fields = ['title', 'description']
    ordering = ['age_group', 'development_area', 'order']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('title', 'description')}),
        ('분류정보', {'fields': ('age_group', 'development_area', 'order')}),
        ('상태정보', {'fields': ('is_active',)}),
        ('시스템정보', {'fields': ('id', 'created_at', 'updated_at')}),
    )


@admin.register(ChildMilestone)
class ChildMilestoneAdmin(admin.ModelAdmin):
    """자녀 이정표 달성 관리자"""
    
    list_display = ['child', 'milestone_title', 'milestone_area', 'achieved_date', 'created_at']
    list_filter = ['milestone__age_group', 'milestone__development_area', 'achieved_date', 'created_at']
    search_fields = ['child__name', 'milestone__title', 'notes']
    ordering = ['-achieved_date']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('child', 'milestone', 'achieved_date')}),
        ('메모', {'fields': ('notes',)}),
        ('시스템정보', {'fields': ('id', 'created_at', 'updated_at')}),
    )

    def milestone_title(self, obj):
        return obj.milestone.title
    milestone_title.short_description = '이정표 제목'

    def milestone_area(self, obj):
        return obj.milestone.get_development_area_display()
    milestone_area.short_description = '발달 영역'
