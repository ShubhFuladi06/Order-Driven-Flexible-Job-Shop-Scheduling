from django.urls import path
from django.shortcuts import redirect
from . import views


def home_redirect(request):
    return redirect('front_page')  # instead of 'login'


urlpatterns = [
    path('home/', views.front_page, name='front_page'),
    path('', home_redirect, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('reset/', views.password_reset_placeholder, name='password_reset'),
    path('save-product-demand/', views.save_product_demand, name='save_product_demand'),
    path('history/', views.view_history, name='view_history'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin_summary/', views.admin_summary, name='admin_summary'),
    path('admin_all_orders_overview/', views.admin_all_orders_overview, name='admin_all_orders_overview'),
    path('admin_machine_env/', views.admin_machine_env, name='admin_machine_env'),
    path('admin_fjsp1/', views.admin_fjsp1_view, name='admin_fjsp1'),



]
