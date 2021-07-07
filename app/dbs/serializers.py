from rest_framework import serializers
from .models import DBObjectCompare, DBObjectFKCompare, DBTableCompare, DBTableColumnCompare, DBInstance, DBCompare
from utils.enums import DbType
from django.contrib.auth.models import User
from app.authentication.serializers import UserSerializer
from enumchoicefield import EnumChoiceField


class RelatedFieldAlternative(serializers.PrimaryKeyRelatedField):
    def __init__(self, **kwargs):
        self.serializer = kwargs.pop('serializer', None)
        if self.serializer is not None and not issubclass(self.serializer, serializers.Serializer):
            raise TypeError('"serializer" is not a valid serializer class')

        super().__init__(**kwargs)

    def use_pk_only_optimization(self):
        return False if self.serializer else True

    def to_representation(self, instance):
        if self.serializer:
            return self.serializer(instance, context=self.context).data
        return super().to_representation(instance)


class DBInstanceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:dbinstance-detail")

    class Meta:
        model = DBInstance
        fields = ['url', 'id', 'name', 'host', 'port', 'username', 'password', 'sid', 'service', 'type', 'added_on', ]


class DBCompareSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:dbcompare-detail")
    src_db = RelatedFieldAlternative(queryset=DBInstance.objects.all(), serializer=DBInstanceSerializer)
    dst_db = RelatedFieldAlternative(queryset=DBInstance.objects.all(), serializer=DBInstanceSerializer)

    class Meta:
        model = DBCompare
        fields = ['url', 'id', 'src_db', 'dst_db', 'last_compared', 'added_on']


class DBTableCompareSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:dbtablecompare-detail")
    compare_dbs = RelatedFieldAlternative(queryset=DBCompare.objects.all(), serializer=DBCompareSerializer)
    # compare_dbs = serializers.HyperlinkedRelatedField(
    #     view_name='api:dbcompare-detail',
    #     queryset=DBCompare.objects.filter(id=DBTableCompare.compare_dbs)
    # )

    class Meta:
        model = DBTableCompare
        fields = '__all__'

    # def to_representation(self, instance):
    #     self.fields['compare_dbs'] = serializers.HyperlinkedRelatedField(view_name='api:dbcompare-detail', read_only=True)
    #     return super(DBTableCompareSerializer, self).to_representation(instance)


class DBTableColumnSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:dbtablecolumncompare-detail")
    type = EnumChoiceField(enum_class=DbType)

    class Meta:
        model = DBTableColumnCompare
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['compare_dbs'] = serializers.HyperlinkedRelatedField(view_name='api:dbcompare-detail', read_only=True)
        return super(DBTableColumnSerializer, self).to_representation(instance)


class DbObjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = DBObjectCompare
        fields = ['table_name', 'src_exists', 'dst_exists', ]

    def to_representation(self, instance):
        self.fields['compare_dbs'] = serializers.HyperlinkedRelatedField(view_name='api:dbcompare-detail', read_only=True)
        return super(DbObjectSerializer, self).to_representation(instance)


class DBFKSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:dbobjectfkcompare-detail")

    class Meta:
        model = DBObjectFKCompare
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['compare_dbs'] = serializers.HyperlinkedRelatedField(view_name='api:dbcompare-detail', read_only=True)
        return super(DBFKSerializer, self).to_representation(instance)
