import uuid
from django.db import models
from django.utils import timezone
from api_service.models import User, UserChild


class DevelopmentRecord(models.Model):
    """발달 기록"""
    
    RECORD_TYPE_CHOICES = [
        ('development_record', '발달 기록'),
        ('milestone_achievement', '이정표 달성'),
        ('observation', '관찰 기록'),
        ('concern', '우려사항'),
    ]
    
    AGE_GROUP_CHOICES = [
        ('0-3months', '0-3개월'),
        ('3-6months', '3-6개월'),
        ('6-9months', '6-9개월'),
        ('9-12months', '9-12개월'),
        ('12-18months', '12-18개월'),
        ('18-24months', '18-24개월'),
        ('24-36months', '24-36개월'),
        ('36-48months', '36-48개월'),
        ('48-60months', '48-60개월'),
        ('60months+', '60개월 이상'),
    ]
    
    DEVELOPMENT_AREA_CHOICES = [
        ('physical', '신체 발달'),
        ('cognitive', '인지 발달'),
        ('language', '언어 발달'),
        ('social', '사회성 발달'),
        ('emotional', '정서 발달'),
        ('self_care', '자조 기능'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='development_records', verbose_name='사용자')
    child = models.ForeignKey(UserChild, on_delete=models.CASCADE, related_name='development_records', verbose_name='자녀')
    date = models.DateField(verbose_name='기록 날짜')
    age_group = models.CharField(max_length=50, choices=AGE_GROUP_CHOICES, verbose_name='연령 그룹')
    development_area = models.CharField(
        max_length=50, 
        choices=DEVELOPMENT_AREA_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name='발달 영역'
    )
    title = models.CharField(max_length=200, verbose_name='제목')
    description = models.TextField(verbose_name='상세 내용')
    record_type = models.CharField(
        max_length=50, 
        choices=RECORD_TYPE_CHOICES, 
        default='development_record',
        verbose_name='기록 유형'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제 시간')

    class Meta:
        db_table = 'development_records'
        verbose_name = '발달 기록'
        verbose_name_plural = '발달 기록들'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['child']),
            models.Index(fields=['date']),
        ]

    def __str__(self):
        return f"{self.child.name} - {self.title} ({self.date})"

    def soft_delete(self):
        """소프트 삭제"""
        self.deleted_at = timezone.now()
        self.save()


class DevelopmentRecordImage(models.Model):
    """발달 기록 이미지"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(
        DevelopmentRecord, 
        on_delete=models.CASCADE, 
        related_name='images', 
        verbose_name='발달 기록'
    )
    image_url = models.URLField(verbose_name='이미지 URL')
    order = models.IntegerField(default=0, verbose_name='이미지 순서')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제 시간')

    class Meta:
        db_table = 'development_record_images'
        verbose_name = '발달 기록 이미지'
        verbose_name_plural = '발달 기록 이미지들'
        ordering = ['order']

    def __str__(self):
        return f"{self.record.title} - 이미지 {self.order + 1}"

    def soft_delete(self):
        """소프트 삭제"""
        self.deleted_at = timezone.now()
        self.save()


class DevelopmentMilestone(models.Model):
    """발달 이정표"""
    
    AGE_GROUP_CHOICES = [
        ('0-3months', '0-3개월'),
        ('3-6months', '3-6개월'),
        ('6-9months', '6-9개월'),
        ('9-12months', '9-12개월'),
        ('12-18months', '12-18개월'),
        ('18-24months', '18-24개월'),
        ('24-36months', '24-36개월'),
        ('36-48months', '36-48개월'),
        ('48-60months', '48-60개월'),
        ('60months+', '60개월 이상'),
    ]
    
    DEVELOPMENT_AREA_CHOICES = [
        ('physical', '신체 발달'),
        ('cognitive', '인지 발달'),
        ('language', '언어 발달'),
        ('social', '사회성 발달'),
        ('emotional', '정서 발달'),
        ('self_care', '자조 기능'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    age_group = models.CharField(max_length=50, choices=AGE_GROUP_CHOICES, verbose_name='연령 그룹')
    development_area = models.CharField(max_length=50, choices=DEVELOPMENT_AREA_CHOICES, verbose_name='발달 영역')
    title = models.CharField(max_length=200, verbose_name='이정표 제목')
    description = models.TextField(verbose_name='이정표 설명')
    order = models.IntegerField(default=0, verbose_name='표시 순서')
    is_active = models.BooleanField(default=True, verbose_name='활성 상태')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')

    class Meta:
        db_table = 'development_milestones'
        verbose_name = '발달 이정표'
        verbose_name_plural = '발달 이정표들'
        ordering = ['age_group', 'development_area', 'order']

    def __str__(self):
        return f"[{self.get_age_group_display()}] {self.get_development_area_display()} - {self.title}"


class ChildMilestone(models.Model):
    """자녀별 이정표 달성"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    child = models.ForeignKey(UserChild, on_delete=models.CASCADE, related_name='achieved_milestones', verbose_name='자녀')
    milestone = models.ForeignKey(
        DevelopmentMilestone, 
        on_delete=models.CASCADE, 
        related_name='child_achievements', 
        verbose_name='이정표'
    )
    achieved_date = models.DateField(verbose_name='달성 날짜')
    notes = models.TextField(blank=True, null=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')

    class Meta:
        db_table = 'child_milestones'
        verbose_name = '자녀 이정표 달성'
        verbose_name_plural = '자녀 이정표 달성들'
        unique_together = ['child', 'milestone']  # 같은 이정표는 한 번만 달성 가능

    def __str__(self):
        return f"{self.child.name} - {self.milestone.title} ({self.achieved_date})"
