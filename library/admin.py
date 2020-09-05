from django.contrib import admin
from .models import ProductFamily, ProductType, ProductModel, OptionType, Option, Supply, SupplyType, \
    Manual, OptionBelongsToModel, Firmware, FirmwareType
from django_summernote.admin import SummernoteModelAdmin



class OptionBelongsToModel(admin.TabularInline):
    model = OptionBelongsToModel


class FirmwareModelAdmin(SummernoteModelAdmin):
    prepopulated_fields = {'slug': ('id_number',)}
    ordering = ['version']
    summernote_fields = 'changes'


class ProductModelAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('model_number',)}
    ordering = ['family_id__family_name']


class OptionAdmin(admin.ModelAdmin):
    inlines = [OptionBelongsToModel]
    prepopulated_fields = {'slug': ('option_model_number',)}
    ordering = ['option_model_number']


class OptionTypeAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('type',)}
    ordering = ['type']


class SupplyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('supply_number',)}


class ProductFamilyAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('family_name',)}
    ordering = ['family_name']


admin.site.register(ProductFamily, ProductFamilyAdmin)
admin.site.register(ProductType)
admin.site.register(ProductModel, ProductModelAdmin)
admin.site.register(OptionType, OptionTypeAdmin)
admin.site.register(Supply, SupplyAdmin)
admin.site.register(SupplyType)
admin.site.register(Manual)
admin.site.register(Firmware, FirmwareModelAdmin)
admin.site.register(Option, OptionAdmin)
admin.site.register(FirmwareType)
