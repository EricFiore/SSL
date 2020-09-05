from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from . models import Manual, OptionType, Option, OptionBelongsToModel


# class FirmwareForm(ModelForm):
#
#     class Meta:
#         model = Firmware
#         fields = ['type', 'version', 'description', 'changes', 'release_date', 'model_id']


class ManualForm(ModelForm):

    class Meta:
        model = Manual
        fields = ['manual_name', 'manual_type', 'manual_part_num', 'manual_download_link', 'model_id']


# class SupplyForm(ModelForm):
#
#     class Meta:
#         model = Supply
#         fields = ['supply_number', 'supply_life', 'supply_content', 'supply_quantity', 'supply_comments', 'model_id']

class OptionBelongsToModelForm(ModelForm):

    class Meta:
        model = OptionBelongsToModel
        fields = ['is_standard', 'product_model']


# class OptionForm(ModelForm):
#     belongsToModelInline = inlineformset_factory(Option, OptionBelongsToModel, form=OptionBelongsToModelForm,
#                                                  fields=['is_standard', 'product_model'])
#
#     class Meta:
#         model = Option
#         fields = ['option_model_number', 'option_description', 'option_type', 'parent_option']


class OptionTypeForm(ModelForm):

    class Meta:
        model = OptionType
        fields = ['type', 'type_description', 'model_id']
