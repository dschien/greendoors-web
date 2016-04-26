from rest_framework import serializers
# @TODO check project substitution
from <%= name %>.models import House, InstalledMeasure, Measure, MeasureCategory, Favourite, Note, Scan, \
    BackboneRouteEvent


__author__ = 'schien'


class MeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Measure


class MeasureCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasureCategory


class FavouriteSerializer(serializers.ModelSerializer):
    def get_validation_exclusions(self):
        # Need to exclude `author` since we'll add that later based off the request
        exclusions = super(FavouriteSerializer, self).get_validation_exclusions()
        return exclusions + ['user']

    class Meta:
        model = Favourite
        exclude = ('user', 'created')


class ScanSerializer(serializers.ModelSerializer):
    def get_validation_exclusions(self):
        # Need to exclude `author` since we'll add that later based off the request
        exclusions = super(ScanSerializer, self).get_validation_exclusions()
        return exclusions + ['user']

    class Meta:
        model = Scan
        exclude = ('user', 'created')


class NoteSerializer(serializers.ModelSerializer):
    def get_validation_exclusions(self):
        # Need to exclude `author` since we'll add that later based off the request
        exclusions = super(NoteSerializer, self).get_validation_exclusions()
        return exclusions + ['user']

    class Meta:
        model = Note
        exclude = ('user', 'created')


class InstalledMeasureSerializer(serializers.ModelSerializer):
    #measure = MeasureSerializer()

    class Meta:
        model = InstalledMeasure
        exclude = ('supplier', 'report_text', 'product')


class HouseSerializer(serializers.ModelSerializer):
    measures = InstalledMeasureSerializer()

    class Meta:
        model = House
        exclude = ('report_text', 'image')

class BackboneRouteEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackboneRouteEvent