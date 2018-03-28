import logging
from urllib.parse import urlparse

from django.urls import resolve
from django.utils import six

from rest_framework import serializers

logger = logging.getLogger(__name__)


class PrivateSerialiserField(serializers.Field):
    def __init__(self, serializer_field, privacy_parent, *args, **kwargs):
        super(PrivateSerialiserField, self).__init__(*args, **kwargs)
        self.serializer_field_parent = privacy_parent
        self.serializer_field = serializer_field
        self.serializer_field.bind('', self)
        
    def to_representation(self, instance):
        return self.serializer_field.to_representation(instance)

    def to_internal_value(self, data):
        return self.serializer_field.to_internal_value(data)
        

class ExtendedModelSerialiserField(serializers.Field):
    """
    A custom field which allows URLs to be provided when deserialising hyper-linked fields.
    
    The to internal value override always returns a dictionary. It's up to the serialiser to create the models.
    this is due to the fact that the field may not have a parent object to attribute it's foreign key to yet.
    
    """

    def __init__(self, serializer, many=False, *args, **kwargs):
        self.many = many
        self.partial = kwargs.pop('partial', False)
        super(ExtendedModelSerialiserField, self).__init__(*args, **kwargs)

        self.serializer = serializer
        self.serializer.bind('', self)

    def to_representation(self, instance):
        # Serialise using supplied serializer
        if instance.__class__.__name__ in ("RelatedManager", "ManyRelatedManager"):
            ret = []
            for item in instance.all():
                #print(instance, item, self.serializer)
                ret.append(self.serializer.to_representation(item))
            return ret
        return self.serializer.to_representation(instance)

    def to_internal_value(self, data):
        # Allow string, list or dictionary to be provided

        # If string then it must contain the URL
        if type(data) == str:
            return {'url':data}

        # If list then loop through results 
        elif type(data) == list:
            ret = []
            for object_dict in data:
                if type(object_dict) == str:
                    object_dict = {'url':object_dict}
                elif "type" in object_dict.keys():
                    del object_dict["type"]
                ret.append( object_dict )
            return ret
        
        # Otherwise use provided data
        else:
            obj_dict = data
            if "type" in obj_dict.keys():
                del obj_dict["type"]
            return obj_dict
        
    
class GenericRelatedField(serializers.Field):
    """
    A custom field to use for serializing generic relationships.
    """

    def __init__(self, serializer_dict, *args, **kwargs):
        self.many = kwargs.pop('many')
        self.url_only = kwargs.pop('url_only', False)
        super(GenericRelatedField, self).__init__(*args, **kwargs)

        self.serializer_dict = serializer_dict
        for s in self.serializer_dict.values():
            s.bind('', self)


    def to_representation(self, instance):
        if self.many:
            objects = []
            for object in instance.all():
                self.to_representation(object)
            return objects

        # find a serializer correspoding to the instance class
        for key in self.serializer_dict.keys():
            if isinstance(instance, key):
                # Generate the result of the classes serializer
                if self.url_only == False:
                    representation = self.serializer_dict[key].to_representation(instance=instance)
                    return representation
                else:
                    return '{}'.format(self.serializer_dict[key].fields['url'].to_representation(value=instance))
                    
                
        return '{}'.format(instance)


    def to_internal_value(self, data):
        # If provided as string, must be url to resource. Create dict containing just url
        if type(data) == str:
            data = {'url': data}

        # If provided as list then loop through all objects
        elif type(data) == list:
            if self.parent.instance == None:
                return []
            else:
                attr = getattr( self.parent.instance, self.source )
                attr.clear()
                for object in data:
                    attr.add( self.to_internal_value( object ) )
                self.parent.instance.save()
                return attr.all()

        # Existing resource can be specified as url
        if 'url' in data:
            # Extract details from the url and grab real object
            resolved_func, unused_args, resolved_kwargs = resolve(
                urlparse(data['url']).path)
            db_table = resolved_func.cls.serializer_class.Meta.model._meta.db_table
            lookup_field = resolved_func.cls.lookup_field
            if lookup_field == 'pk':
                lookup_field = 'id'
            lookup_value = resolved_kwargs[resolved_func.cls.lookup_field]
            object = resolved_func.cls.serializer_class.Meta.model.objects.raw('SELECT * from {} where {}={}'.format(db_table,lookup_field,lookup_value ))[0]
            #object = resolved_func.cls.queryset.get(pk=resolved_kwargs[resolved_func.cls.lookup_field])
        else:
            # If url is not specified then object is new and must have a 'type'
            # field to allow us to create correct object from list of
            # serializers
            for key in self.serializer_dict.keys():
                if data['type'] == key.__name__:
                    object = key()

        # Deserialize data into attributes of object and apply
        if object.__class__ in self.serializer_dict.keys():
            serializer = self.serializer_dict[object.__class__]
            serializer.partial = True
            obj_internal_value = serializer.to_internal_value(data)
            for k, v in obj_internal_value.items():
                setattr(object, k, v)
        else:
            raise NameError(
                "No serializer specified for {} entities".format(object.__class__.__name__))

        # Save object to store new or any updated attributes
        object.save()
        return object


class TypeField(serializers.Field):
    """
        Read only Field which displays the object type from the class name
    """

    def __init__(self, *args, **kwargs):

        kwargs['source'] = '__class__.__name__'
        kwargs['read_only'] = True
        super(TypeField, self).__init__(*args, **kwargs)

    def to_representation(self, value):
        return value
