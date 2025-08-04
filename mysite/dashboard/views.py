# dashboard/views.py

import json
from datetime import timedelta
from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import Bookmark, Comment, Like, Post


@login_required
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

    # 3. 차트 데이터
    # 월간 활성 사용자 (MAU) 그래프 - 최근 12개월
    mau_chart_labels = []
    mau_chart_values = []
    current_date = timezone.now().date()
    for i in range(11, -1, -1):  # 11개월 전부터 이번달까지
        # Calculate year and month for 'i' months ago
        year = current_date.year
        month = current_date.month - i
        while month <= 0:
            month += 12
            year -= 1
 
        # Get the number of distinct users who logged in that month
        mau_for_month = User.objects.filter(
            last_login__year=year, last_login__month=month
        ).values("id").distinct().count()
        mau_chart_labels.append(date(year, month, 1).strftime("%Y-%m"))
        mau_chart_values.append(mau_for_month)
 
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

@login_required
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


@login_required
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
