from django.urls import path
from .views import login_view, dashboard, sign_out, refresh_token, test_jwt

urlpatterns = [
    path("login/", login_view, name="login"),
    path("dashboard/", dashboard, name="dashboard"),
    path("sign_out/", sign_out, name="sign_out"),
    path("refresh_token/", refresh_token, name="refresh_token"),
    path("test_jwt/", test_jwt, name="test_jwt"),
]