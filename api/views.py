from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import UserSerializer, BudgetSerializer, DepenseSerializer, UserAccessSerializer
from django.contrib.auth import get_user_model
from .models import Budget, BudgetHistory, Depense, UserAccess
from django.db.models import Sum, Q

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class UserAccessListCreateView(generics.ListCreateAPIView):
    serializer_class = UserAccessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAccess.objects.filter(Q(owner=self.request.user) | Q(shared_with=self.request.user))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UserAccessDeleteView(generics.DestroyAPIView):
    queryset = UserAccess.objects.all()
    serializer_class = UserAccessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserAccess.objects.filter(owner=self.request.user)

class BudgetListCreateView(generics.ListCreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        total = Budget.objects.filter(user=self.request.user).aggregate(Sum('montant'))['montant__sum'] or 0
        BudgetHistory.objects.create(user=self.request.user, total_budget=total, titre="+")

class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        self._update_history("MOD")

    def perform_destroy(self, instance):
        instance.delete()
        self._update_history("-")

    def _update_history(self, titre):
        total = Budget.objects.filter(user=self.request.user).aggregate(Sum('montant'))['montant__sum'] or 0
        BudgetHistory.objects.create(user=self.request.user, total_budget=total, titre=titre)

class DepenseListCreateView(generics.ListCreateAPIView):
    serializer_class = DepenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        shared_accounts = UserAccess.objects.filter(shared_with=self.request.user).values_list('owner', flat=True)
        # Add associates' accounts if the user is a manager
        associate_accounts = User.objects.filter(manager=self.request.user).values_list('id', flat=True)
        return Depense.objects.filter(Q(user=self.request.user) | Q(user__in=shared_accounts) | Q(user__in=associate_accounts))

    def perform_create(self, serializer):
        depense = serializer.save()
        if depense.status == 'APPROVED':
            self._update_budget_history(depense.user, -depense.montant_total, "-")

    def _update_budget_history(self, user, montant_diff, titre):
        last_history = BudgetHistory.objects.filter(user=user).last()
        current_total = last_history.total_budget if last_history else 0
        new_total = current_total + montant_diff
        BudgetHistory.objects.create(user=user, total_budget=new_total, titre=titre)

class DepenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DepenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        shared_accounts = UserAccess.objects.filter(shared_with=self.request.user).values_list('owner', flat=True)
        # Add associates' accounts if the user is a manager
        associate_accounts = User.objects.filter(manager=self.request.user).values_list('id', flat=True)
        # On permet la lecture/modif si on est proprio ou si on a un accès FULL ou si on est le manager
        return Depense.objects.filter(Q(user=self.request.user) | Q(user__in=shared_accounts) | Q(user__in=associate_accounts))

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_montant = old_instance.montant_total
        old_status = old_instance.status
        
        depense = serializer.save()
        
        if depense.status == 'APPROVED':
            diff = depense.montant_total - (old_montant if old_status == 'APPROVED' else 0)
            if diff != 0:
                self._update_budget_history(depense.user, -diff, "MOD")

    def perform_destroy(self, instance):
        montant_a_restaurer = instance.montant_total if instance.status == 'APPROVED' else 0
        owner = instance.user
        instance.delete()
        if montant_a_restaurer != 0:
            self._update_budget_history(owner, montant_a_restaurer, "RESTORE")

    def _update_budget_history(self, user, montant_diff, titre):
        last_history = BudgetHistory.objects.filter(user=user).last()
        current_total = last_history.total_budget if last_history else 0
        new_total = current_total + montant_diff
        BudgetHistory.objects.create(user=user, total_budget=new_total, titre=titre)

class ApproveDepenseView(generics.UpdateAPIView):
    queryset = Depense.objects.all()
    serializer_class = DepenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Depense.objects.filter(user=self.request.user, status='PENDING')

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        action = request.data.get('action')
        
        if action == 'APPROVE':
            instance.status = 'APPROVED'
            instance.save()
            last_history = BudgetHistory.objects.filter(user=instance.user).last()
            current_total = last_history.total_budget if last_history else 0
            new_total = current_total - instance.montant_total
            BudgetHistory.objects.create(user=instance.user, total_budget=new_total, titre="DEPENSE APPROVED")
            return Response({"status": "approved"})
        elif action == 'REJECT':
            instance.status = 'REJECTED'
            instance.save()
            return Response({"status": "rejected"})
        
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

class AssociateViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role != 'MANAGER':
            return User.objects.none()
        return User.objects.filter(manager=self.request.user)

    def perform_create(self, serializer):
        # A manager can create an associate directly
        serializer.save(manager=self.request.user, role='ASSOCIER', is_approved=True)

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        associate = self.get_object()
        action_type = request.data.get('action') # 'APPROVE' or 'REJECT'
        access_level = request.data.get('access_level', 'LIMITED')
        
        if action_type == 'APPROVE':
            associate.is_approved = True
            associate.access_level = access_level
            associate.save()
            
            UserAccess.objects.update_or_create(
                owner=associate,
                shared_with=self.request.user,
                defaults={'access_level': access_level}
            )
            return Response({"status": "approved", "access_level": access_level})
        elif action_type == 'REJECT':
            associate.is_approved = False
            associate.manager = None
            associate.save()
            return Response({"status": "rejected"})
            
        return Response({"error": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
