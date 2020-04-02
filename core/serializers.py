from core.tasks import Country, Entry, Formula
from rest_framework import serializers

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'confirmed', 'confirmed_formula', 'lat', 'long', 't_zero']
        depth = 1

class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'confirmed_formula', 'lat', 'long', 't_zero']
        depth = 1

class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ['date', 'value']
        exclude = ['id']

class FormulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formula
        fields = ['a', 'b', 'c', 'd']