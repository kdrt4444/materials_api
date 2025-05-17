from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import MaterialViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'materials', MaterialViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]