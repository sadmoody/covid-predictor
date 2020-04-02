from django.shortcuts import render

# Create your views here.
from core.models import Country, Entry, Formula
from rest_framework import viewsets, permissions
from core.serializers import CountrySerializer, CountryListSerializer, EntrySerializer, FormulaSerializer
from rest_framework.response import Response
from django.http import HttpResponse
from django.template import loader

class CountryViewSet(viewsets.ViewSet):
    queryset = Country.objects.all().order_by('name')
    def list(self, request):
        queryset = Country.objects.all().order_by('name')
        serializer = CountryListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = Country.objects.get(name__iexact=pk)
        serializer = CountrySerializer(queryset)
        return Response(serializer.data)

def index(request):
    template = loader.get_template('core/base.html')
    context = {}
    return HttpResponse(template.render(context, request))