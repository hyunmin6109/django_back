import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일은 필수입니다.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """사용자 모델"""
    
    AUTH_PROVIDER_CHOICES = [
        ('local', 'Local'),
        ('google', 'Google'),
        ('kakao', 'Kakao'),
        ('naver', 'Naver'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name='이메일')
    password = models.CharField(max_length=255, verbose_name='비밀번호')
    name = models.CharField(max_length=100, verbose_name='사용자 이름')
    profile_image = models.URLField(blank=True, null=True, verbose_name='프로필 이미지 URL')
    auth_provider = models.CharField(
        max_length=20, 
        choices=AUTH_PROVIDER_CHOICES, 
        default='local',
        verbose_name='인증 제공자'
    )
    auth_provider_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='인증 제공자 ID')
    last_login = models.DateTimeField(blank=True, null=True, verbose_name='마지막 로그인')
    is_active = models.BooleanField(default=True, verbose_name='활성 상태')
    is_staff = models.BooleanField(default=False, verbose_name='스태프 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제 시간')

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['auth_provider', 'auth_provider_id']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f"{self.name} ({self.email})"

    def soft_delete(self):
        """소프트 삭제"""
        self.deleted_at = timezone.now()
        self.is_active = False
        self.save()


class UserChild(models.Model):
    """사용자 자녀 정보"""
    
    GENDER_CHOICES = [
        ('male', '남성'),
        ('female', '여성'),
        ('other', '기타'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='children', verbose_name='사용자')
    name = models.CharField(max_length=100, verbose_name='자녀 별명')
    birth_date = models.DateField(verbose_name='생년월일')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='성별')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제 시간')

    class Meta:
        db_table = 'user_children'
        verbose_name = '자녀 정보'
        verbose_name_plural = '자녀 정보들'
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.name}의 자녀 - {self.name}"

    def soft_delete(self):
        """소프트 삭제"""
        self.deleted_at = timezone.now()
        self.save()

    @property
    def age_months(self):
        """개월 수 계산"""
        today = timezone.now().date()
        age_days = (today - self.birth_date).days
        return age_days // 30  # 대략적인 개월 수


class Session(models.Model):
    """세션 관리"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions', verbose_name='사용자')
    token = models.CharField(max_length=255, unique=True, verbose_name='세션 토큰')
    device_info = models.JSONField(blank=True, null=True, verbose_name='기기 정보')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP 주소')
    expires_at = models.DateTimeField(verbose_name='만료 시간')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')

    class Meta:
        db_table = 'sessions'
        verbose_name = '세션'
        verbose_name_plural = '세션들'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}..."

    def is_expired(self):
        """세션 만료 여부 확인"""
        return timezone.now() > self.expires_at


class SearchLog(models.Model):
    """검색 로그"""
    
    SEARCH_TYPE_CHOICES = [
        ('all', '전체'),
        ('posts', '게시물'),
        ('milestones', '발달 이정표'),
        ('records', '발달 기록'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='사용자')
    query = models.CharField(max_length=255, verbose_name='검색어')
    search_type = models.CharField(max_length=50, choices=SEARCH_TYPE_CHOICES, default='all', verbose_name='검색 유형')
    results_count = models.IntegerField(default=0, verbose_name='결과 수')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='IP 주소')
    user_agent = models.TextField(blank=True, null=True, verbose_name='User Agent')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')

    class Meta:
        db_table = 'search_logs'
        verbose_name = '검색 로그'
        verbose_name_plural = '검색 로그들'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.query} ({self.search_type})"
