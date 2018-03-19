from django.db import models
import ast

class ListField(models.TextField):
    #__metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        print(self.name, "to_python",value, "|", type(value))
        if not value or value=='':
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        #value = super(ListField, self).get_prep_value(value)
        #print(self.name, "get_prep_value",value, "|", type(value))
        if value is None:
            return value

        return "{}".format(value)
        
    def from_db_value(self, value, expression, connection):
        #print(self.name, "from_db_value",value, "|", type(value))
        if value is None:
            #print(" from_db_value NONE",value, "|", type(value))
            return value
        if value=='':
            #print(" from_db_value EMPTY",value, "|", type(value))
            value = list()
        if isinstance(value, list):
            #print(" from_db_value LIST",value, "|", type(value))
            return value

        #print(" from_db_value AST",ast.literal_eval(value), "|", type(ast.literal_eval(value)))
        return ast.literal_eval(value)
    

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        print("value_to_string",value, "|", type(value),"|",self.get_db_prep_value(value))
        return self.get_db_prep_value(value)
