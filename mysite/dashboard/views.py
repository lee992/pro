# dashboard/views.py

import json
from datetime import timedelta
import random
from datetime import date
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from .models import Bookmark, Comment, Like, Post, Category
from .forms import UserProfileForm, PostForm, CommentForm

def staff_member_required(view_func):
    """
    관리자(is_staff=True)만 접근할 수 있도록 하는 데코레이터.
    권한이 없는 경우 대시보드 로그인 페이지로 리디렉션합니다.
    """
    return user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=reverse_lazy('dashboard:login'),
        redirect_field_name='next'
    )(view_func)


@staff_member_required
def dashboard_view(request):
    """
    대시보드 페이지에 필요한 모든 데이터를 계산하고 템플릿에 전달하는 뷰.
    """
    # 1. 전체 사용자 목록 (사용자 관리 페이지용)
    user_list = User.objects.all().order_by('-date_joined')
    page = request.GET.get('page', 1)
    paginator = Paginator(user_list, 10)  # 한 페이지에 10명씩 표시
    try:
        users = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        users = paginator.page(1)

    # 2. 요약 카드 데이터
    user_count = user_list.count()
    post_count = Post.objects.count()
    comment_count = Comment.objects.count()
    like_count = Like.objects.count()
    bookmark_count = Bookmark.objects.count()

    # 월간 활성 사용자 (MAU) - 최근 30일 이내에 로그인한 사용자
    thirty_days_ago = timezone.now() - timedelta(days=30)
    mau_count = User.objects.filter(last_login__gte=thirty_days_ago).count()

    # 3. 차트 데이터 - 월간 활성 사용자 (MAU) 그래프 (최근 12개월)
    # DB 조회를 12번에서 1번으로 줄여 성능을 개선합니다.
    current_date = timezone.now().date()

    # 1. 12개월 전 첫날을 계산하여 쿼리 범위를 지정합니다.
    start_date_year = current_date.year
    start_date_month = current_date.month - 11
    while start_date_month <= 0:
        start_date_month += 12
        start_date_year -= 1
    start_date_for_query = date(start_date_year, start_date_month, 1)

    # 2. DB에서 한 번의 쿼리로 월별 활성 사용자 수를 집계합니다.
    mau_query_results = User.objects.filter(
        last_login__gte=start_date_for_query
    ).annotate(month=TruncMonth('last_login')) \
     .values('month') \
     .annotate(mau=Count('id', distinct=True)) \
     .values('month', 'mau')

    # 3. 쿼리 결과를 { 'YYYY-MM': count } 형태의 딕셔너리로 변환하여 조회 속도를 높입니다.
    mau_data_map = {item['month'].strftime('%Y-%m'): item['mau'] for item in mau_query_results}

    # 4. 지난 12개월을 순회하며 차트 데이터를 생성합니다. (데이터가 없는 달은 0으로 채웁니다)
    mau_chart_labels = []
    mau_chart_values = []
    for i in range(11, -1, -1):  # 11개월 전부터 이번달까지
        year = current_date.year
        month = current_date.month - i
        while month <= 0:
            month += 12
            year -= 1
        label = date(year, month, 1).strftime("%Y-%m")
        mau_chart_labels.append(label)
        # --- 데모용 더미 데이터 추가 ---
        # NOTE: 이 부분은 차트가 어떻게 보이는지 확인하기 위한 더미 데이터입니다.
        #       실제 운영 환경에서는 `+ random.randint(50, 300)` 부분을 삭제해야 합니다.
        mau_chart_values.append(mau_data_map.get(label, 0) + random.randint(50, 300))
 
    # 전체 콘텐츠 분포
    content_distribution_labels = ['게시글', '댓글', '좋아요', '북마크']
    content_distribution_values = [post_count, comment_count, like_count, bookmark_count]

    # 4. 최근 가입자 및 게시글 목록
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_posts = Post.objects.order_by('-created_at')[:5]

    context = {
        'users': users,
        'user_count': user_count,
        'post_count': post_count,
        'comment_count': comment_count,
        'like_count': like_count,
        'bookmark_count': bookmark_count,
        'mau_count': mau_count,
        'mau_chart_labels': json.dumps(mau_chart_labels),
        'mau_chart_values': json.dumps(mau_chart_values),
        'content_distribution_labels': json.dumps(content_distribution_labels),
        'content_distribution_values': json.dumps(content_distribution_values),
        'recent_users': recent_users,
        'recent_posts': recent_posts,
    }
    return render(request, 'dashboard/dashboard.html', context)

@staff_member_required
@require_POST
def toggle_user_status(request, user_id):
    if request.user.id == user_id:
        return JsonResponse({'status': 'error', 'message': '자신의 상태는 변경할 수 없습니다.'}, status=403)
    
    try:
        user_to_toggle = User.objects.get(id=user_id)
        user_to_toggle.is_active = not user_to_toggle.is_active
        user_to_toggle.save(update_fields=['is_active'])
        return JsonResponse({'status': 'success', 'is_active': user_to_toggle.is_active})
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': '사용자를 찾을 수 없습니다.'}, status=404)


@staff_member_required
def user_list_partial(request):
    """
    AJAX 페이지네이션 및 검색 요청을 처리하여 사용자 목록 HTML 조각을 반환하는 뷰.
    """
    search_query = request.GET.get('search', '')
    user_list = User.objects.all().order_by('-date_joined')

    if search_query:
        user_list = user_list.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    page = request.GET.get('page', 1)
    paginator = Paginator(user_list, 10)  # 한 페이지에 10명씩 표시
    users = paginator.get_page(page)
    return render(request, 'dashboard/_user_list.html', {'users': users})


@login_required
def profile_edit_view(request):
    """
    Handles displaying and processing the user profile edit form.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필 정보가 성공적으로 업데이트되었습니다.')
            return HttpResponseRedirect(reverse_lazy('dashboard:user_home'))
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'dashboard/profile_edit.html', {'form': form})



@login_required
def login_redirect_view(request):
    """
    로그인 후 사용자의 역할(is_staff)에 따라 적절한 페이지로 리디렉션합니다.
    """
    if request.user.is_staff:
        # 관리자는 대시보드로 이동
        return HttpResponseRedirect(reverse_lazy('dashboard:dashboard'))
    else:
        # 일반 사용자는 사용자 홈으로 이동
        return HttpResponseRedirect(reverse_lazy('dashboard:user_home'))


@login_required
def user_home_view(request):
    """
    일반 사용자를 위한 홈 페이지 뷰.
    """
    return render(request, 'dashboard/user_home.html')


# --- 게시판 기능 View 추가 ---

@login_required
def post_list_view(request):
    """
    게시글 목록을 보여주는 뷰.
    """
    post_list = Post.objects.select_related('author', 'category').annotate(
        like_count=Count('likes', distinct=True)
    ).all().order_by('-created_at')
    paginator = Paginator(post_list, 10)  # 한 페이지에 10개씩
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'dashboard/post_list.html', {'page_obj': page_obj})


@login_required
def post_detail_view(request, pk):
    """
    게시글 상세 내용과 댓글을 보여주는 뷰.
    """
    post = get_object_or_404(Post.objects.select_related('author', 'category'), pk=pk)
    comments = post.comments.select_related('author').order_by('created_at')
    
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.author = request.user
            new_comment.save()
            messages.success(request, '댓글이 성공적으로 작성되었습니다.')
            return redirect('dashboard:post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()

    # 좋아요 상태와 카운트는 GET/POST에 상관없이 항상 필요합니다.
    like_count = post.likes.count()
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = post.likes.filter(user=request.user).exists()

    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'like_count': like_count,
        'user_has_liked': user_has_liked,
    }
    return render(request, 'dashboard/post_detail.html', context)


@login_required
def post_create_view(request):
    """
    새로운 게시글을 작성하는 뷰.
    """
    # 글을 작성하기 전에 카테고리가 존재하는지 확인합니다.
    if not Category.objects.exists():
        messages.error(request, '게시글을 작성하려면 먼저 관리자 페이지에서 카테고리를 하나 이상 생성해야 합니다.')
        return redirect('dashboard:post_list')

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '게시글이 성공적으로 작성되었습니다.')
            return redirect('dashboard:post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    return render(request, 'dashboard/post_form.html', {'form': form, 'form_title': '새 글 작성'})


@login_required
def post_edit_view(request, pk):
    """
    기존 게시글을 수정하는 뷰.
    """
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        raise PermissionDenied

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '게시글이 성공적으로 수정되었습니다.')
            return redirect('dashboard:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'dashboard/post_form.html', {'form': form, 'form_title': '글 수정'})


@login_required
@require_POST
def toggle_like_view(request, pk):
    try:
        user = request.user
        post = get_object_or_404(Post, pk=pk)

        like, created = Like.objects.get_or_create(user=user, post=post)

        if not created:
            like.delete()
            is_liked = False
        else:
            like.save()  # 👈 명시적으로 저장
            is_liked = True

        like_count = post.likes.count()

        print(f'[DEBUG] Like 객체 생성됨: {created}, 현재 좋아요 수: {like_count}')
        return JsonResponse({'is_liked': is_liked, 'like_count': like_count})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)
