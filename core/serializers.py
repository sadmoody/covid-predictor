from core.tasks import Country, Entry, Formula
from rest_framework import serializers

class EntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Entry
        fields = ['date', 'value']
        exclude = ['id']

class FormulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formula
        #fields = ['']
        fields = ['a', 'b', 'c', 'd']
        extra_kwargs = {
            'a': {'max_digits': 20, 'decimal_places': 5, 'coerce_to_string': False},
            'b': {'max_digits': 20, 'decimal_places': 5, 'coerce_to_string': False},
            'c': {'max_digits': 20, 'decimal_places': 5, 'coerce_to_string': False},
            'd': {'max_digits': 20, 'decimal_places': 5, 'coerce_to_string': False}
        }

class CountryListSerializer(serializers.ModelSerializer):
    confirmed_formula = FormulaSerializer(many=False)
    death_formula = FormulaSerializer(many=False)
    class Meta:
        model = Country
        fields = ['name', 'confirmed_formula', 'death_formula', 't_zero', 'latest_confirmed_count', 'latest_death_count']

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['name', 'confirmed', 'death', 'confirmed_formula', 'death_formula', 't_zero', 'latest_confirmed_count', 'latest_death_count']
        depth = 1