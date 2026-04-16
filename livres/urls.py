from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)
from . import views

router = DefaultRouter()
router.register(r'auteurs', views.AuteurViewSet)
router.register(r'livres',  views.LivreViewSet)
router.register(r'emprunts',views.EmpruntViewSet, basename='emprunt')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/',      views.RegisterView.as_view()),
    path('auth/token/',          TokenObtainPairView.as_view()),
    path('auth/token/refresh/',  TokenRefreshView.as_view()),
]
