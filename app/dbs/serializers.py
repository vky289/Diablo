from rest_framework import serializers
from .models import DBObjectCompare, DBObjectFKCompare, DBTableCompare, DBTableColumnCompare, DBInstance, DBCompare
from utils.enums import DbType
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
    url = serializers.HyperlinkedIdentityField(view_name="dbs:dbb:dbinstance-detail")

    class Meta:
        model = DBInstance
        fields = ['url', 'name', 'host', 'port', 'username', 'password', 'sid', 'service', 'type', 'added_on', 'added_by', ]


class DBCompareSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dbs:dbb:dbcompare-detail")
    src_db = RelatedFieldAlternative(queryset=DBInstance.objects.all(), serializer=DBInstanceSerializer)
    dst_db = RelatedFieldAlternative(queryset=DBInstance.objects.all(), serializer=DBInstanceSerializer)

    class Meta:
        model = DBCompare
        fields = '__all__'


class DBTableCompareSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dbs:dbb:dbtablecompare-detail")

    class Meta:
        model = DBTableCompare
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['compare_dbs'] = serializers.HyperlinkedRelatedField(view_name='dbs:dbb:dbcompare-detail', read_only=True)
        return super(DBTableCompareSerializer, self).to_representation(instance)


class DBTableColumnSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dbs:dbb:dbcompare-detail")
    type = EnumChoiceField(enum_class=DbType)

    class Meta:
        model = DBTableColumnCompare
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['compare_dbs'] = serializers.HyperlinkedRelatedField(view_name='dbs:dbb:dbcompare-detail', read_only=True)
        return super(DBTableColumnSerializer, self).to_representation(instance)


class DbViewSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dbs:dbb:dbtablecompare-detail")

    class Meta:
        model = DBObjectCompare
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['compare_dbs'] = serializers.HyperlinkedRelatedField(view_name='dbs:dbb:dbcompare-detail', read_only=True)
        return super(DbViewSerializer, self).to_representation(instance)


class DBFKSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dbs:dbb:dbobjectfkcompare-detail")

    class Meta:
        model = DBObjectFKCompare
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['compare_dbs'] = serializers.HyperlinkedRelatedField(view_name='dbs:dbb:dbcompare-detail', read_only=True)
        return super(DBFKSerializer, self).to_representation(instance)
