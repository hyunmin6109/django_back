import uuid
from django.db import models
from django.utils import timezone
from api_service.models import User


class ChatSession(models.Model):
    """채팅 세션"""
    
    STATUS_CHOICES = [
        ('active', '활성'),
        ('completed', '완료'),
        ('expired', '만료'),
    ]
    
    CATEGORY_CHOICES = [
        ('general', '일반 상담'),
        ('development', '발달 상담'),
        ('health', '건강 상담'),
        ('behavior', '행동 상담'),
        ('nutrition', '영양 상담'),
        ('education', '교육 상담'),
        ('sleep', '수면 상담'),
        ('emergency', '응급 상담'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions', verbose_name='사용자')
    title = models.CharField(max_length=200, verbose_name='세션 제목')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name='상담 카테고리')
    session_token = models.CharField(max_length=255, blank=True, null=True, verbose_name='OpenAI 세션 토큰')
    total_tokens = models.IntegerField(default=0, verbose_name='총 사용 토큰 수')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='상태')
    last_message_at = models.DateTimeField(blank=True, null=True, verbose_name='마지막 메시지 시간')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제 시간')

    class Meta:
        db_table = 'chat_sessions'
        verbose_name = '채팅 세션'
        verbose_name_plural = '채팅 세션들'
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user.name} - {self.title} ({self.get_status_display()})"

    def soft_delete(self):
        """소프트 삭제"""
        self.deleted_at = timezone.now()
        self.status = 'expired'
        self.save()

    def add_tokens(self, token_count):
        """토큰 사용량 추가"""
        self.total_tokens += token_count
        self.save(update_fields=['total_tokens'])

    def update_last_message_time(self):
        """마지막 메시지 시간 업데이트"""
        self.last_message_at = timezone.now()
        self.save(update_fields=['last_message_at'])

    def complete_session(self):
        """세션 완료"""
        self.status = 'completed'
        self.save(update_fields=['status'])

    @property
    def message_count(self):
        """메시지 수"""
        return self.messages.count()

    @property
    def duration_minutes(self):
        """세션 지속 시간 (분)"""
        if self.last_message_at:
            duration = self.last_message_at - self.created_at
            return duration.total_seconds() / 60
        return 0


class ChatMessage(models.Model):
    """채팅 메시지"""
    
    ROLE_CHOICES = [
        ('user', '사용자'),
        ('assistant', '어시스턴트'),
        ('system', '시스템'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages', verbose_name='세션')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='역할')
    content = models.TextField(verbose_name='메시지 내용')
    tokens = models.IntegerField(default=0, verbose_name='메시지 토큰 수')
    metadata = models.JSONField(blank=True, null=True, verbose_name='추가 메타데이터')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')

    class Meta:
        db_table = 'chat_messages'
        verbose_name = '채팅 메시지'
        verbose_name_plural = '채팅 메시지들'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"[{self.get_role_display()}] {content_preview}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 메시지 저장 시 세션의 토큰 수와 마지막 메시지 시간 업데이트
        if self.tokens > 0:
            self.session.add_tokens(self.tokens)
        self.session.update_last_message_time()

    @property
    def is_user_message(self):
        """사용자 메시지 여부"""
        return self.role == 'user'

    @property
    def is_assistant_message(self):
        """어시스턴트 메시지 여부"""
        return self.role == 'assistant'