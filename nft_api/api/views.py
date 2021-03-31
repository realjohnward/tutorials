from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from .serializers import ContractSerializer
from .models import Contract 
from rest_framework.response import Response
import requests
from django.shortcuts import get_object_or_404

class ContractViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing the accounts
    associated with the user.
    """
    serializer_class = ContractSerializer
    queryset = Contract.objects.all()

    @action(detail=True)
    def nft(self, request, pk=None):
        contract = get_object_or_404(Contract, pk=pk)
        nft_id = request.GET.get("id")
        url = f"https://api.opensea.io/api/v1/asset/{contract.address}/{nft_id}/"
        response = requests.get(url).json()
        return Response(response)

    @action(detail=True)
    def nfts(self, request, pk=None):
        contract = get_object_or_404(Contract, pk=pk)
        nft_ids_str = request.GET.get("ids")
        nft_ids = [int(id) for id in nft_ids_str.split(",")]
        qry = {"asset_contract_address": contract.address, "token_ids": nft_ids, "order_direction":"desc","offset":"0","limit":"20"}
        url = f"https://api.opensea.io/api/v1/assets"
        response = requests.get(url, params=qry).json()
        return Response(response)

    @action(detail=True)
    def nft_events(self, request, pk=None):
        contract = get_object_or_404(Contract, pk=pk)
        nft_id = request.GET.get("id")     
        url = "https://api.opensea.io/api/v1/events"
        querystring = {"only_opensea":"false","offset":"0","limit":"20", "asset_contract_address": contract.address, "token_id": int(nft_id)}
        response = requests.get(url, params=querystring).json()
        return Response(response)

    @action(detail=True)
    def opensea_data(self, request, pk=None):
        contract = get_object_or_404(Contract, pk=pk)
        url = f"https://api.opensea.io/api/v1/asset_contract/{contract.address}"
        response = requests.get(url).json()
        return Response(response)