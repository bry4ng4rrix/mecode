from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Budget, BudgetHistory, Depense, DepenseItem
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
        fields = ['id', 'email', 'first_name', 'last_name', 'password', 'total_budget']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_total_budget(self, obj):
        last_history = obj.budgethistory_set.last()
        return last_history.total_budget if last_history else 0
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
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

    class Meta:
        model = Depense
        fields = ['id', 'titre', 'montant_total', 'date', 'items']
        read_only_fields = ['montant_total', 'user']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        
        # Calcul automatique du total
        total = sum(item['prix'] for item in items_data)
        
        depense = Depense.objects.create(user=user, montant_total=total, **validated_data)
        
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

