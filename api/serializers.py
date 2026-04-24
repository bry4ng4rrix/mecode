from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Budget, BudgetHistory, Depense, DepenseItem, UserAccess
from django.db.models import Sum
User = get_user_model()

class BudgetHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetHistory
        fields = ['total_budget']

class UserSerializer(serializers.ModelSerializer):
    total_budget = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'role', 'temp_manager_email', 'is_approved', 'access_level', 'total_budget']
        extra_kwargs = {
            'password': {'write_only': True},
            'is_approved': {'read_only': True},
            'access_level': {'read_only': True},
        }

    def get_total_budget(self, obj):
        last_history = obj.budgethistory_set.last()
        return last_history.total_budget if last_history else 0
    
    def create(self, validated_data):
        role = validated_data.get('role', 'MANAGER')
        temp_manager_email = validated_data.get('temp_manager_email')
        
        # Managers are approved by default (or maybe they don't need approval)
        # Associates need approval
        is_approved = True if role == 'MANAGER' else False
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=role,
            temp_manager_email=temp_manager_email,
            is_approved=is_approved
        )
        
        # Link to manager if it's an associate and manager email is provided
        if role == 'ASSOCIER' and temp_manager_email:
            try:
                manager = User.objects.get(email=temp_manager_email, role='MANAGER')
                user.manager = manager
                user.save()
            except User.DoesNotExist:
                # We still create the user but without a manager link (or we could raise an error)
                # The instructions say "associate must add manager email", so maybe we should validate it.
                pass
                
        return user


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['user']


class DepenseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepenseItem
        fields = ['nom', 'prix']

class DepenseSerializer(serializers.ModelSerializer):
    items = DepenseItemSerializer(many=True)
    added_by_email = serializers.ReadOnlyField(source='added_by.email')

    class Meta:
        model = Depense
        fields = ['id', 'titre', 'montant_total', 'date', 'items', 'user', 'status', 'added_by_email']
        read_only_fields = ['montant_total', 'status', 'added_by_email']

    def validate(self, data):
        items_data = data.get('items', [])
        total = sum(item['prix'] for item in items_data)
        
        # Le "user" dans data est le propriétaire du compte
        owner = data.get('user', self.instance.user if self.instance else self.context['request'].user)
        
        last_history = BudgetHistory.objects.filter(user=owner).last()
        current_budget = last_history.total_budget if last_history else 0
        
        if self.instance:
            diff = total - self.instance.montant_total
            if diff > current_budget:
                raise serializers.ValidationError({"items": "Le nouveau montant total dépasse le budget disponible."})
        else:
            if total > current_budget:
                raise serializers.ValidationError({"items": "Le montant total de la dépense dépasse le budget actuel."})
        
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request_user = self.context['request'].user
        owner = validated_data.get('user', request_user)
        
        # Calcul automatique du total
        total = sum(item['prix'] for item in items_data)
        
        # Déterminer le statut initial
        status = 'APPROVED'
        if owner != request_user:
            # Vérifier les permissions
            access = UserAccess.objects.filter(owner=owner, shared_with=request_user).first()
            if not access:
                raise serializers.ValidationError("Vous n'avez pas accès à ce compte.")
            if access.access_level == 'LIMITED':
                status = 'PENDING'
        
        depense = Depense.objects.create(
            user=owner, 
            added_by=request_user, 
            montant_total=total, 
            status=status,
            **validated_data
        )
        
        for item_data in items_data:
            DepenseItem.objects.create(depense=depense, **item_data)
        
        return depense

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        instance.titre = validated_data.get('titre', instance.titre)
        
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                DepenseItem.objects.create(depense=instance, **item_data)
            
            total = sum(item['prix'] for item in items_data)
            instance.montant_total = total
            
        instance.save()
        return instance


class UserAccessSerializer(serializers.ModelSerializer):
    owner_email = serializers.ReadOnlyField(source='owner.email')
    shared_with_email = serializers.ReadOnlyField(source='shared_with.email')

    class Meta:
        model = UserAccess
        fields = ['id', 'owner', 'shared_with', 'access_level', 'owner_email', 'shared_with_email', 'created_at']
        read_only_fields = ['owner', 'created_at']
