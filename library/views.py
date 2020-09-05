import datetime
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin
from django.db.models import Min
from django.contrib.auth.models import User
from resolutions.views import ResolutionsResultsView
from users.models import Profile
from .models import (ProductType, ProductFamily, ProductModel,
                     Firmware, Manual, Supply,
                     SupplyType, OptionType, Option,
                     OptionBelongsToModel, FirmwareType
                     )
from resolutions.models import TechTipFix, ManualFix, Error
from resolutions.forms import MainSearch
from library.datum import get_error
from library.help.sorting import sort_firmware
from library.help.query import create_firmware_query


class ProductTypeListView(FormMixin, ListView):
    model = ProductType
    context_object_name = 'types'
    form_class = MainSearch
    qs = QuerySet()

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        # query = request.GET.get("q")
        # if query:
        #     self.qs = ProductFamily.objects.filter(productmodel__model_number__icontains=query).distinct()
        #     if not self.qs:
        #         self.qs = ProductModel.objects.filter(family_id__family_name__icontains=query)
        # else:
        #     self.qs = {}
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_results'] = self.qs
        context['model_count'] = ProductModel.objects.all().count()
        context['user_count'] = User.objects.all().count()
        return context


class ResultsListView(ListView):
    template_name = 'library/results_list.html'
    qs = QuerySet()

    def get_queryset(self):
        return self.qs

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q")
        if query:
            self.qs = ProductFamily.objects.filter(productmodel__model_number__icontains=query).distinct()
            if not self.qs:
                self.qs = ProductModel.objects.filter(family_id__family_name__icontains=query)
        else:
            self.qs = {}
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_results'] = self.qs
        context['user'] = Profile.objects.filter(user=self.request.user).first()
        return context


class ProductFamilyListView(FormMixin, ListView):
    model = ProductFamily
    context_object_name = 'families'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        type_id = get_object_or_404(ProductType, product_type=self.kwargs['type_id'])
        return ProductFamily.objects.filter(type_id=type_id).order_by('family_name')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        return context


class ProductModelListView(ListView):
    model = ProductModel
    context_object_name = 'models'

    def get_queryset(self):
        product_model = get_object_or_404(ProductFamily, family_name=self.kwargs['family_id'])
        return ProductModel.objects.filter(family_id=product_model)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['title'] = ProductFamily.objects.filter(family_name=self.object_list.first().family_id).first()
        return context


class ProductModelDetailView(FormMixin, DetailView):
    model = ProductModel
    context_object_name = 'model_detail'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['supply_types'] = SupplyType.objects.filter(supply__model_id=self.object.model_id)\
            .distinct().order_by('supply_type')
        context['supplies'] = Supply.objects.filter(model_id=self.object.model_id).select_related()
        context['manuals'] = Manual.objects.filter(model_id=self.object.model_id)
        context['firmwares'] = Firmware.objects.filter(model_id=self.object.model_id)
        context['options'] = OptionBelongsToModel.objects.filter(product_model=self.object.model_id)\
            .order_by('product_option__option_type__type', 'product_option__option_model_number')
        tech_tip_qs = Error.objects.filter(techtipfix__model_id=self.object.model_id,)\
            .order_by('error_name')
        manual_fix_qs = Error.objects.filter(manualfix__model_id=self.object.model_id)\
            .order_by('error_name')
        context['tech_tips'] = get_error(tech_tip_qs, manual_fix_qs)
        return context


class FirmwareDetailView(DetailView):
    model = Firmware
    context_object_name = 'firmware'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['user'] = Profile.objects.filter(user=self.request.user).first()
        return context


class FirmwareListView(ListView):
    model = Firmware
    context_object_name = 'firmwares'
    paginator = None
    qs = {}
    queried_families = []
    queried_types = []
    start_date = list(Firmware.objects.aggregate(Min('release_date')).values())[0].strftime('%Y-%m-%d')
    end_date = datetime.date.today().strftime('%Y-%m-%d')

    def get(self, request, *args, **kwargs):
        self.queried_types = request.GET.getlist("type")
        self.queried_families = request.GET.getlist('family')
        filtered_dates = request.GET.getlist('date')
        if len(self.queried_types) | len(self.queried_families) | len(filtered_dates):
            dates, family_query, type_query = create_firmware_query(filtered_dates,
                                                                    self.queried_families, self.queried_types)      #TODO add models to end of firmware cards and fix javascript
            self.qs = sort_firmware(Firmware.objects.filter(family_query).filter(type_query)
                                    .filter(release_date__range=[dates[0], dates[1]])
                                    .order_by('-release_date'))
            self.start_date = dates[0]
            self.end_date = dates[1]
            return super().get(request, *args, **kwargs)
        else:
            self.qs = sort_firmware(Firmware.objects.all())
            self.paginator = Paginator(Firmware.objects.all(), 5) #TODO: need to get pagination working.  Paginiation will not work with the way I am organizing the Firmware data throough the sortfirmware method
            print(self.paginator.page(1))
            return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['firmware_dict'] = self.qs
        context['queried_types'] = self.queried_types
        context['firmware_types'] = FirmwareType.objects.all()
        context['families'] = ProductFamily.objects.all()
        context['queried_families'] = self.queried_families
        context['start_date'] = self.start_date
        context['end_date'] = self.end_date
        context['page_list'] = self.paginator
        return context


class ManualListView(ListView):
    model = Manual
    context_object_name = 'manuals'


class SupplyListView(FormMixin, ListView):
    model = SupplyType
    form_class = MainSearch
    context_object_name = 'supplies'
    template_name = 'library/supply_list.html'

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user.id) if self.request.user.id else {}
        return context


class SupplyDetailView(FormMixin, DetailView):
    model = Supply
    context_object_name = 'supply'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allSupplies'] = Supply.objects.filter(model_id__supply=self.object.supply_id)\
            .filter(supply_type=self.object.supply_type).distinct().order_by('supply_number')
        context['relatedModels'] = ProductModel.objects.filter(supply__supply_id=self.object.supply_id)\
            .order_by('model_number')
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        return context


class OptionListView(FormMixin, ListView):
    model = OptionType
    context_object_name = 'types'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        return context


class OptionDetailView(FormMixin, DetailView):
    model = Option
    context_object_name = 'option'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mfp_models = ProductModel.objects.filter(option__option_id=self.object.option_id)\
            .order_by('family_id__family_name')
        families = {}
        for model in mfp_models:
            if model.family_id.family_name not in families:
                families[model.family_id.family_name] = []
            option_model_relation = OptionBelongsToModel.objects.filter(product_model_id=model.model_id,
                                                                        product_option_id=self.object.option_id)
            families[model.family_id.family_name].append((model.model_number, option_model_relation.first().is_standard))
            families[model.family_id.family_name].sort()
        context['models'] = mfp_models
        context['families'] = families
        context['user'] = Profile.objects.get(user=self.request.user)
        return context
