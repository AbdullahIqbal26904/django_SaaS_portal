from django.urls import path
from . import views

urlpatterns = [
    path('', views.department_list, name='department_list'),
    path('create/', views.create_department, name='create_department'),
    path('<int:department_id>/', views.department_detail, name='department_detail'),
    path('<int:department_id>/edit/', views.edit_department, name='edit_department'),
    path('<int:department_id>/add-admin/', views.add_department_admin, name='add_department_admin'),
    path('<int:department_id>/add-user/', views.add_department_user, name='add_department_user'),
    path('<int:department_id>/remove-user/<int:user_id>/', views.remove_department_user, name='remove_department_user'),
]
