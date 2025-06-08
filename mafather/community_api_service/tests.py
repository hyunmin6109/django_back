from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Post, Category, Comment, Like
from api_service.models import User
import uuid

class CommunityAPITestCase(TestCase):
    def setUp(self):
        """테스트에 필요한 기본 데이터 설정"""
        # 테스트용 사용자 생성
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            password='testpass123',
            name='Other User'
        )
        
        # 테스트용 카테고리 생성
        self.category = Category.objects.create(
            name='테스트 카테고리',
            post_type='question',
            description='테스트용 카테고리입니다.'
        )
        
        # API 클라이언트 설정
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        """게시글 작성 테스트"""
        url = reverse('post-create')
        data = {
            'title': '테스트 게시글',
            'content': '테스트 내용입니다.',
            'category_id': str(self.category.id),
            'post_type': 'question',
            'is_anonymous': False
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, '테스트 게시글')

    def test_get_posts(self):
        """게시글 목록 조회 테스트"""
        # 테스트용 게시글 생성
        Post.objects.create(
            user=self.user,
            category=self.category,
            title='테스트 게시글',
            content='테스트 내용입니다.',
            post_type='question'
        )
        
        url = reverse('post-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_post_detail(self):
        """게시글 상세 조회 테스트"""
        post = Post.objects.create(
            user=self.user,
            category=self.category,
            title='테스트 게시글',
            content='테스트 내용입니다.',
            post_type='question'
        )
        
        url = reverse('post-detail', args=[post.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '테스트 게시글')

    def test_like_post(self):
        """게시글 좋아요 테스트"""
        post = Post.objects.create(
            user=self.user,
            category=self.category,
            title='테스트 게시글',
            content='테스트 내용입니다.',
            post_type='question'
        )
        
        url = reverse('post-like', args=[post.id])
        
        # 좋아요 추가
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(post.like_count, 1)
        
        # 좋아요 취소
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(post.like_count, 0)

    def test_create_comment(self):
        """댓글 작성 테스트"""
        post = Post.objects.create(
            user=self.user,
            category=self.category,
            title='테스트 게시글',
            content='테스트 내용입니다.',
            post_type='question'
        )
        
        url = reverse('post-comment', args=[post.id])
        data = {
            'content': '테스트 댓글입니다.',
            'is_anonymous': False
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(post.comment_count, 1)

    def test_reply_comment(self):
        """댓글 답글 테스트"""
        post = Post.objects.create(
            user=self.user,
            category=self.category,
            title='테스트 게시글',
            content='테스트 내용입니다.',
            post_type='question'
        )
        
        parent_comment = Comment.objects.create(
            user=self.user,
            post=post,
            content='부모 댓글입니다.'
        )
        
        url = reverse('comment-reply', args=[post.id, parent_comment.id])
        data = {
            'content': '답글입니다.',
            'is_anonymous': False
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(parent_comment.replies.count(), 1)

    def test_edit_comment(self):
        """댓글 수정 테스트"""
        post = Post.objects.create(
            user=self.user,
            category=self.category,
            title='테스트 게시글',
            content='테스트 내용입니다.',
            post_type='question'
        )
        
        comment = Comment.objects.create(
            user=self.user,
            post=post,
            content='수정 전 댓글입니다.'
        )
        
        url = reverse('comment-edit', args=[post.id, comment.id])
        data = {
            'content': '수정된 댓글입니다.'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.get(id=comment.id).content, '수정된 댓글입니다.')

    def test_delete_comment(self):
        """댓글 삭제 테스트"""
        post = Post.objects.create(
            user=self.user,
            category=self.category,
            title='테스트 게시글',
            content='테스트 내용입니다.',
            post_type='question'
        )
        
        comment = Comment.objects.create(
            user=self.user,
            post=post,
            content='삭제될 댓글입니다.'
        )
        
        url = reverse('comment-delete', args=[post.id, comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(Comment.objects.get(id=comment.id).deleted_at)

    def test_unauthorized_access(self):
        """인증되지 않은 접근 테스트"""
        self.client.force_authenticate(user=None)
        
        # 게시글 작성 시도
        url = reverse('post-create')
        data = {
            'title': '테스트 게시글',
            'content': '테스트 내용입니다.',
            'category_id': str(self.category.id),
            'post_type': 'question'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_comment_permission(self):
        """댓글 권한 테스트"""
        post = Post.objects.create(
            user=self.user,
            category=self.category,
            title='테스트 게시글',
            content='테스트 내용입니다.',
            post_type='question'
        )
        
        comment = Comment.objects.create(
            user=self.user,
            post=post,
            content='테스트 댓글입니다.'
        )
        
        # 다른 사용자로 로그인
        self.client.force_authenticate(user=self.other_user)
        
        # 댓글 수정 시도
        url = reverse('comment-edit', args=[post.id, comment.id])
        data = {'content': '수정 시도'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
