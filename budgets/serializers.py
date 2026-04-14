from rest_framework import serializers
from .models import Budget, Debt
from transactions.models import Category

class BudgetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    spent         = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True, default=0)
    remaining     = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True, default=0)

    class Meta:
        model  = Budget
        fields = ['id', 'category', 'category_name', 'amount', 'period', 'month', 'year', 'spent', 'remaining']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Debt
        fields = ['id', 'type', 'contact', 'amount', 'due_date', 'is_paid', 'description', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)