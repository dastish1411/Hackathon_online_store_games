from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CommentCreateDeleteView, LikedProductsViews


router = DefaultRouter()
router.register('product', ProductViewSet, 'product')
router.register('comment', CommentCreateDeleteView, 'comment')
urlpatterns = [
    path('liked/', LikedProductsViews.as_view(), name='liked')
]
urlpatterns += router.urls