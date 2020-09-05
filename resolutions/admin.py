from django.contrib import admin
from .models import Error, TechTipFix, ManualFix, CustomFixes
from photos.models import TechTipPics
from django_summernote.admin import SummernoteModelAdmin

class TechTipPics(admin.TabularInline):
    model = TechTipPics

class CustomFixAdmin(SummernoteModelAdmin):
    prepopulated_fields = {'slug': ('id_number',)}
    ordering = ['author', 'id_number']


class ErrorAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('error_name',)}
    ordering = ['error_name']


class TechTipAdmin(SummernoteModelAdmin):
    inlines = [TechTipPics]
    prepopulated_fields = {'slug': ('tech_tip_number',)}
    ordering = ['tech_tip_number']
    summernote_fields = 'tech_tip_content'


class ManualFixAdmin(SummernoteModelAdmin):
    summernote_fields = 'steps_to_fix_error'
    prepopulated_fields = {'slug': ('id',)}
    ordering = ['repairs_error']


admin.site.register(Error, ErrorAdmin)
admin.site.register(TechTipFix, TechTipAdmin)
admin.site.register(ManualFix, ManualFixAdmin)
admin.site.register(CustomFixes, CustomFixAdmin)
