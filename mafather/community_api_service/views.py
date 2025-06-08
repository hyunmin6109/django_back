# community_api_service/views.py
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Post, Category, Like, Comment
from .serializers import PostSerializer, CategorySerializer, CommentSerializer

# 게시글 작성 API   
@api_view(['POST'])
@permission_classes([IsAuthenticated])  # 로그인한 사용자만 접근 가능
def create_post(request):
    serializer = PostSerializer(data=request.data)
    if serializer.is_valid():
        post = serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# 게시글 목록 조회 API
@api_view(['GET'])
def get_posts(request):
    posts = Post.objects.filter(deleted_at__isnull=True)  # 삭제되지 않은 게시글만
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

# 게시글 상세 조회 API
@api_view(['GET'])
def get_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        post.increment_view_count()  # 조회수 증가
        serializer = PostSerializer(post)
        return Response(serializer.data)
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# 게시글 좋아요 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        
        # 이미 좋아요를 누른 경우
        existing_like = Like.objects.filter(
            user=request.user,
            target_id=post_id,
            target_type='post'
        ).first()
        
        if existing_like:
            existing_like.delete()
            return Response({"message": "좋아요가 취소되었습니다."}, status=200)
        
        # 새로운 좋아요 생성
        like = Like.objects.create(
            user=request.user,
            target_id=post_id,
            target_type='post'
        )
        
        return Response({"message": "좋아요가 등록되었습니다."}, status=201)
        
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        # 디버깅을 위해 구체적인 오류 메시지 반환
        return Response({"error": f"서버 오류: {str(e)}"}, status=500)

# 게시글 댓글 작성 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        
        # 요청 데이터에 post_id 추가
        data = request.data.copy()
        data['post'] = post_id
        
        # 부모 댓글이 있는 경우 (답글)
        parent_id = data.get('parent_id')
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id, post=post, deleted_at__isnull=True)
                data['parent'] = parent_id
            except Comment.DoesNotExist:
                return Response({"error": "부모 댓글을 찾을 수 없습니다."}, status=404)
        
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            comment = serializer.save(user=request.user)
            post.update_comment_count()  # update_comment_count 메서드 사용
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
        
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# 게시글 댓글 조회 API
@api_view(['GET'])
def get_comment(request, post_id, comment_id):
    try:
        post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        comment = Comment.objects.get(id=comment_id, post=post, deleted_at__isnull=True)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=404)
    except Comment.DoesNotExist:
        return Response({"error": "댓글을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# 게시글 댓글 좋아요 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_comment(request, post_id, comment_id):
    try:
        post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        comment = Comment.objects.get(id=comment_id, post=post, deleted_at__isnull=True)
        
        # 이미 좋아요를 누른 경우
        existing_like = Like.objects.filter(
            user=request.user,
            target_id=comment_id,
            target_type='comment'
        ).first()
        
        if existing_like:
            existing_like.delete()
            return Response({"message": "좋아요가 취소되었습니다."}, status=200)
        
        # 새로운 좋아요 생성
        Like.objects.create(
            user=request.user,
            target_id=comment_id,
            target_type='comment'
        )
        
        return Response({"message": "좋아요가 등록되었습니다."}, status=201)
        
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=404)
    except Comment.DoesNotExist:
        return Response({"error": "댓글을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# 게시글 댓글 삭제 API
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, post_id, comment_id):
    try:
        post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        comment = Comment.objects.get(id=comment_id, post=post, deleted_at__isnull=True)
        
        # 댓글 작성자 또는 관리자만 삭제 가능
        if comment.user != request.user and not request.user.is_staff:
            return Response({"error": "댓글을 삭제할 권한이 없습니다."}, status=403)
        
        comment.soft_delete()
        return Response({"message": "댓글이 삭제되었습니다."}, status=200)
        
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=404)
    except Comment.DoesNotExist:
        return Response({"error": "댓글을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# 게시글 댓글 수정 API
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_comment(request, post_id, comment_id):
    try:
        post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        comment = Comment.objects.get(id=comment_id, post=post, deleted_at__isnull=True)
        
        # 댓글 작성자만 수정 가능
        if comment.user != request.user:
            return Response({"error": "댓글을 수정할 권한이 없습니다."}, status=403)
        
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
        
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=404)
    except Comment.DoesNotExist:
        return Response({"error": "댓글을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

# 게시글 댓글 답글 API
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reply_comment(request, post_id, comment_id):
    try:
        post = Post.objects.get(id=post_id, deleted_at__isnull=True)
        parent_comment = Comment.objects.get(id=comment_id, post=post, deleted_at__isnull=True)
        
        # 요청 데이터에 post_id와 parent_id 추가
        data = request.data.copy()
        data['post'] = post_id
        data['parent'] = comment_id
        
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            comment = serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
        
    except Post.DoesNotExist:
        return Response({"error": "게시글을 찾을 수 없습니다."}, status=404)
    except Comment.DoesNotExist:
        return Response({"error": "부모 댓글을 찾을 수 없습니다."}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)