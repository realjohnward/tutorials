from rest_framework import serializers
from .models import Contract, Collection 

class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['id', 'name', 'address']

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection 
        fields = ['id', 'name', 'address']