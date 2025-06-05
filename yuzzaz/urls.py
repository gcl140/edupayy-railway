from django.contrib.auth import views as auth_views
from django.urls import path
from . import views


urlpatterns = [
    # path('register/', views.register, name='register'),
    path('register/<str:user_type>/', views.register, name='register'),
    # path('register/', views.register, name='register'),
    path('homepage/', views.homepage, name='homepage'),
    path('', views.homepage, name='homepage'),
    path('login/', views.login, name='login'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('logout/', views.logout, name='logout'),
    path('send_custom_email/', views.send_custom_email, name='send_custom_email'),
    path('parents_dashboard/', views.parents_dashboard, name='parents_dashboard'),
    path('profile/', views.profile, name='profile'),
    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='yuzzaz/password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='yuzzaz/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='yuzzaz/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name='yuzzaz/password_reset_complete.html'), name='password_reset_complete'),
    path('activate-user/', views.activate_user_by_email, name='activate_user_by_email'),
    path('notifications/mark-all-read/', views.mark_all_notifications_as_read, name='mark_all_notifications_read'),
    path('notifications/mark-all-read-page/', views.mark_all_notifications_as_read_page, name='mark_all_notifications_as_read_page'),

]
