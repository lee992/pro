from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # /dashboard/ URL로 접속했을 때 dashboard_view를 호출합니다.
    path('', views.dashboard_view, name='dashboard'),
    # 사용자 상태를 토글하기 위한 URL
    path('users/<int:user_id>/toggle_status/', views.toggle_user_status, name='toggle_user_status'),
]
