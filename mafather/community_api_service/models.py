import uuid
from django.db import models, transaction
from django.utils import timezone
from api_service.models import User



class Category(models.Model):
    """카테고리"""
    
    POST_TYPE_CHOICES = [
        ('question', '질문'),
        ('story', '이야기'),
        ('tip', '팁'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name='카테고리 이름')
    description = models.TextField(blank=True, null=True, verbose_name='카테고리 설명')
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, verbose_name='적용 게시물 타입')
    color = models.CharField(max_length=7, blank=True, null=True, verbose_name='카테고리 색상 (HEX)')
    icon = models.CharField(max_length=50, blank=True, null=True, verbose_name='아이콘 클래스명')
    order = models.IntegerField(default=0, verbose_name='표시 순서')
    is_active = models.BooleanField(default=True, verbose_name='활성 상태')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')

    class Meta:
        db_table = 'categories'
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리들'
        ordering = ['post_type', 'order']
        indexes = [
            models.Index(fields=['post_type']),
        ]

    def __str__(self):
        return f"[{self.get_post_type_display()}] {self.name}"


class Post(models.Model):
    """통합 게시물"""
    
    POST_TYPE_CHOICES = [
        ('question', '질문'),
        ('story', '이야기'),
        ('tip', '팁'),
    ]
    
    STATUS_CHOICES = [
        ('draft', '초안'),
        ('published', '게시됨'),
        ('hidden', '숨김'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='작성자')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', verbose_name='카테고리')
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, verbose_name='게시물 타입')
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='published', verbose_name='상태')
    view_count = models.IntegerField(default=0, verbose_name='조회수')
    like_count = models.IntegerField(default=0, verbose_name='좋아요 수')
    comment_count = models.IntegerField(default=0, verbose_name='댓글 수')
    is_anonymous = models.BooleanField(default=False, verbose_name='익명 여부')
    is_solved = models.BooleanField(blank=True, null=True, verbose_name='해결 여부 (질문 타입에만 적용)')
    is_pinned = models.BooleanField(default=False, verbose_name='상단 고정 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제 시간')

    class Meta:
        db_table = 'posts'
        verbose_name = '게시물'
        verbose_name_plural = '게시물들'
        ordering = ['-is_pinned', '-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['user']),
            models.Index(fields=['post_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_pinned']),
        ]

    def __str__(self):
        return f"[{self.get_post_type_display()}] {self.title}"

    def soft_delete(self):
        """소프트 삭제"""
        self.deleted_at = timezone.now()
        self.save()

    def increment_view_count(self):
        """조회수 증가"""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def update_comment_count(self):
        """댓글 수 업데이트"""
        self.comment_count = self.comments.filter(deleted_at__isnull=True).count()
        self.save(update_fields=['comment_count'])

    def update_like_count(self):
        """좋아요 수 업데이트"""
        from .models import Like  # 순환 import 방지
        self.like_count = Like.objects.filter(
            target_id=self.id,
            target_type='post'
        ).count()
        self.save(update_fields=['like_count'])


class Comment(models.Model):
    """댓글"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='작성자')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='게시물')
    content = models.TextField(verbose_name='내용')
    like_count = models.IntegerField(default=0, verbose_name='좋아요 수')
    is_anonymous = models.BooleanField(default=False, verbose_name='익명 여부')
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='replies',
        verbose_name='부모 댓글'
    )
    depth = models.IntegerField(default=0, verbose_name='댓글 깊이')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제 시간')

    class Meta:
        db_table = 'comments'
        verbose_name = '댓글'
        verbose_name_plural = '댓글들'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"{self.post.title} - 댓글 by {self.user.name}"

    def soft_delete(self):
        """소프트 삭제"""
        self.deleted_at = timezone.now()
        self.save()
        # 부모 게시물의 댓글 수 업데이트
        self.post.update_comment_count()

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # 대댓글의 깊이 설정
            if self.parent:
                self.depth = 1
            super().save(*args, **kwargs)
            # 댓글 저장 시 게시물의 댓글 수 업데이트
            if not self.deleted_at:
                self.post.comment_count = Comment.objects.filter(
                    post=self.post,
                    deleted_at__isnull=True
                ).count()
                self.post.save(update_fields=['comment_count', 'updated_at'])

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            post = self.post
            super().delete(*args, **kwargs)
            # 댓글 삭제 시 게시물의 댓글 수 업데이트
            post.comment_count = Comment.objects.filter(
                post=post,
                deleted_at__isnull=True
            ).count()
            post.save(update_fields=['comment_count', 'updated_at'])

    def update_like_count(self):
        """좋아요 수 업데이트"""
        from .models import Like
        self.like_count = Like.objects.filter(
            target_id=self.id,
            target_type='post'
        ).count()
        self.save(update_fields=['like_count'])


class PostImage(models.Model):
    """게시물 이미지"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images', verbose_name='게시물')
    image_url = models.URLField(verbose_name='이미지 URL')
    alt_text = models.CharField(max_length=255, blank=True, null=True, verbose_name='대체 텍스트')
    order = models.IntegerField(default=0, verbose_name='이미지 순서')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')
    deleted_at = models.DateTimeField(blank=True, null=True, verbose_name='삭제 시간')

    class Meta:
        db_table = 'post_images'
        verbose_name = '게시물 이미지'
        verbose_name_plural = '게시물 이미지들'
        ordering = ['order']

    def __str__(self):
        return f"{self.post.title} - 이미지 {self.order + 1}"

    def soft_delete(self):
        """소프트 삭제"""
        self.deleted_at = timezone.now()
        self.save()



class Like(models.Model):
    """좋아요"""
    
    TARGET_TYPE_CHOICES = [
        ('post', '게시물'),
        ('comment', '댓글'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes', verbose_name='사용자')
    target_id = models.UUIDField(verbose_name='대상 ID')
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES, verbose_name='대상 유형')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성 시간')

    class Meta:
        db_table = 'likes'
        verbose_name = '좋아요'
        verbose_name_plural = '좋아요들'
        unique_together = ['user', 'target_id', 'target_type']  # 중복 좋아요 방지
        indexes = [
            models.Index(fields=['target_id', 'target_type']),
            models.Index(fields=['user', 'target_id', 'target_type']),
        ]

    def __str__(self):
        return f"{self.user.name} - {self.get_target_type_display()} 좋아요"

    @property
    def target_object(self):
        """대상 객체 반환"""
        if self.target_type == 'post':
            try:
                return Post.objects.get(id=self.target_id)
            except Post.DoesNotExist:
                return None
        elif self.target_type == 'comment':
            try:
                return Comment.objects.get(id=self.target_id)
            except Comment.DoesNotExist:
                return None
        return None

    def save(self, *args, **kwargs):
        # 먼저 저장
        super().save(*args, **kwargs)
        
        # 그다음 카운트 업데이트 (트랜잭션 내에서)
        try:
            target_obj = self.target_object
            if target_obj:
                like_count = Like.objects.filter(
                    target_id=self.target_id,
                    target_type=self.target_type
                ).count()
                
                if self.target_type == 'post':
                    # Post 모델에 직접 업데이트
                    Post.objects.filter(id=self.target_id).update(like_count=like_count)
                elif self.target_type == 'comment':
                    # Comment 모델에 직접 업데이트
                    Comment.objects.filter(id=self.target_id).update(like_count=like_count)
        except Exception as e:
            # 로그 기록하고 무시 (테스트 환경에서는 print)
            print(f"Error updating like count in save: {str(e)}")

    def delete(self, *args, **kwargs):
        target_obj = self.target_object
        target_id = self.target_id
        target_type = self.target_type
        
        # 먼저 삭제
        super().delete(*args, **kwargs)
        
        # 그다음 카운트 업데이트
        try:
            like_count = Like.objects.filter(
                target_id=target_id,
                target_type=target_type
            ).count()
            
            if target_type == 'post':
                Post.objects.filter(id=target_id).update(like_count=like_count)
            elif target_type == 'comment':
                Comment.objects.filter(id=target_id).update(like_count=like_count)
        except Exception as e:
            print(f"Error updating like count in delete: {str(e)}")
