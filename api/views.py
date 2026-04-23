from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import UserSerializer, BudgetSerializer, DepenseSerializer
from django.contrib.auth import get_user_model
from .models import Budget, BudgetHistory, Depense
from django.db.models import Sum

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

class BudgetListCreateView(generics.ListCreateAPIView):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    

    def perform_create(self, serializer):
        # Enregistre le nouveau budget
        serializer.save(user=self.request.user)
        
        # Calcule le nouveau total et l'enregistre dans l'historique avec "+"
        total = Budget.objects.filter(user=self.request.user).aggregate(Sum('montant'))['montant__sum'] or 0
        BudgetHistory.objects.create(
            user=self.request.user,
            total_budget=total,
            titre="+"
        )

class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
        # Recalcule le total après modification
        self._update_history(titre="MOD")

    def perform_destroy(self, instance):
        instance.delete()
        # Recalcule le total après suppression avec "-"
        self._update_history(titre="-")

    def _update_history(self, titre="+"):
        total = Budget.objects.filter(user=self.request.user).aggregate(Sum('montant'))['montant__sum'] or 0
        BudgetHistory.objects.create(
            user=self.request.user,
            total_budget=total,
            titre=titre
        )

class DepenseListCreateView(generics.ListCreateAPIView):
    serializer_class = DepenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Depense.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        depense = serializer.save()
        
        # Récupère le dernier budget total
        last_history = BudgetHistory.objects.filter(user=self.request.user).last()
        current_total = last_history.total_budget if last_history else 0
        
        # Soustrait le montant de la dépense
        new_total = current_total - depense.montant_total
        
        # Enregistre dans l'historique avec "-"
        BudgetHistory.objects.create(
            user=self.request.user,
            total_budget=new_total,
            titre="-"
        )

class DepenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DepenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Depense.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_montant = old_instance.montant_total
        
        depense = serializer.save()
        new_montant = depense.montant_total
        
        diff = new_montant - old_montant
        
        if diff != 0:
            last_history = BudgetHistory.objects.filter(user=self.request.user).last()
            current_total = last_history.total_budget if last_history else 0
            new_total = current_total - diff
            
            BudgetHistory.objects.create(
                user=self.request.user,
                total_budget=new_total,
                titre="MOD"
            )

    def perform_destroy(self, instance):
        montant_restaure = instance.montant_total
        instance.delete()
        
        last_history = BudgetHistory.objects.filter(user=self.request.user).last()
        current_total = last_history.total_budget if last_history else 0
        new_total = current_total + montant_restaure
        
        BudgetHistory.objects.create(
            user=self.request.user,
            total_budget=new_total,
            titre="RESTORE"
        )
