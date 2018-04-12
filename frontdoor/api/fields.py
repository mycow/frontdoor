from django import forms

class HouseModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj.house.house_name

class UserModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
         return obj