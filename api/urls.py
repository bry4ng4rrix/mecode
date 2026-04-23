from django.urls import path
from .views import (
    RegisterView, 
    CurrentUserView, 
    BudgetListCreateView, 
    BudgetDetailView,
    DepenseListCreateView,
    DepenseDetailView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('budget/', BudgetListCreateView.as_view(), name='budget-list-create'),
    path('budget/<int:pk>/', BudgetDetailView.as_view(), name='budget-detail'),
    path('depense/', DepenseListCreateView.as_view(), name='depense-list-create'),
    path('depense/<int:pk>/', DepenseDetailView.as_view(), name='depense-detail'),
]
