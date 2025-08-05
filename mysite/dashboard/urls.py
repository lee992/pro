from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
 
app_name = 'dashboard'

urlpatterns = [
    # 기존 URL 패턴
    path('', views.dashboard_view, name='dashboard'),
    path('toggle_user_status/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),
    path('user_list_partial/', views.user_list_partial, name='user_list_partial'),

    # 로그인 후 리디렉션을 처리할 URL
    path('redirect/', views.login_redirect_view, name='login_redirect'),
    path('home/', views.user_home_view, name='user_home'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),

    # 게시판 URL 추가
    path('board/', views.post_list_view, name='post_list'),
    path('board/post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('board/post/new/', views.post_create_view, name='post_create'),
    path('board/post/<int:pk>/edit/', views.post_edit_view, name='post_edit'),
    path('board/post/<int:pk>/like/', views.toggle_like_view, name='toggle_like'),

    # 로그인 및 로그아웃 URL 추가
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='dashboard/login.html',
            redirect_authenticated_user=True  # 이미 로그인된 사용자는 대시보드로 리디렉션
        ),
        name='login'
    ),
    path(
        'logout/',
        # 로그아웃 후 로그인 페이지로 이동
        auth_views.LogoutView.as_view(next_page=reverse_lazy('dashboard:login')),
        name='logout'
    ),

    # Password Reset URLs
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='dashboard/password_reset_form.html',
             email_template_name='dashboard/password_reset_email.html',
             subject_template_name='dashboard/password_reset_subject.txt',
             success_url=reverse_lazy('dashboard:password_reset_done')
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='dashboard/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='dashboard/password_reset_confirm.html',
             success_url=reverse_lazy('dashboard:password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='dashboard/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]