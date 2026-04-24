from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, 
    CurrentUserView, 
    BudgetListCreateView, 
    BudgetDetailView,
    DepenseListCreateView,
    DepenseDetailView,
    UserAccessListCreateView,
    UserAccessDeleteView,
    ApproveDepenseView,
    AssociateViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'associates', AssociateViewSet, basename='associate')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('budget/', BudgetListCreateView.as_view(), name='budget-list-create'),
    path('budget/<int:pk>/', BudgetDetailView.as_view(), name='budget-detail'),
    path('depense/', DepenseListCreateView.as_view(), name='depense-list-create'),
    path('depense/<int:pk>/', DepenseDetailView.as_view(), name='depense-detail'),
    path('depense/<int:pk>/approve/', ApproveDepenseView.as_view(), name='depense-approve'),
    path('access/', UserAccessListCreateView.as_view(), name='access-list-create'),
    path('access/<int:pk>/', UserAccessDeleteView.as_view(), name='access-delete'),
    path('', include(router.urls)),
]
