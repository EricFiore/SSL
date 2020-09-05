import datetime
import pytz
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import DetailView, ListView, FormView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import FormMixin, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .forms import StatisticalChoiceForm, TechTipSearch, TechTipDailySearch, CustomFixForm, ErrorForm, MainSearch
from .models import Error, TechTipFix, ManualFix, CustomFixes
from users.models import Profile
from photos.models import TechTipPics
from comments.forms import CustomFixCommentForm, TechTipCommentForm, ManualFixCommentForm
from comments.models import CustomFixComments, TechTipComment, ManualFixComment
from tracking.pages import capture_hit
from tracking.time_modification import convert_to_end_datetime, convert_to_start_datetime
from tracking.page_tracking import (DataTracking, get_daily_views, record_active_pages, record_active_page_ranking,
                                    get_all_pages_movement)
from library import datum
from search.query import Query, count_dict_results
from search.documents import ProductModelDocument, ErrorDocument


def get_view_type(url):
    """a url is passed in a a type of view is output
    if an invalid view type is passed in an empty string
    will be returned"""
    view_types = {
        'fix': 'User Fix',
        'tech-tips': 'Tech Tip',
        'manual': "Manual Fix",
        'error': 'Error'
    }
    if url.split('/')[-2] in view_types:
        return view_types[url.split('/')[-2]]
    else:
        return ' '


def get_recent_items(view_type):
    """accepts a view type as defined in the get_view_type method and outputs
    a database call for the most 5 most recent items.  If an invalid view
    type is passed in a null value is returned"""
    recent_items = {
        'Tech Tip': TechTipFix.objects.all().order_by('-tech_tip_date')[:5],
        'User Fix': CustomFixes.objects.all().order_by('-created_on_date')[:5],
        'Manual Fix': ManualFix.objects.all().order_by('-date_added')[:5],
        'Error': Error.objects.all().order_by('created_on_date')[:5]
    }
    if view_type in recent_items:
        return recent_items[view_type]
    else:
        return None


def generilize_recent_database_call(url):
    """accepts a url, retrieves the 5 most recent entries
    belonging to the model of the inputted url, then
    outputs the title 'title' and 'id' of objects
    belonging to the models of that url"""
    most_recent_items = get_recent_items(get_view_type(url))
    generilized_items = {}
    if get_view_type(url) == 'User Fix':
        for item in most_recent_items:
            generilized_items[item.id_number] = {
                'id': item.id_number,
                'title': item.symptoms
            }
    if get_view_type(url) == 'Tech Tip':
        for item in most_recent_items:
            generilized_items[item.tech_tip_number] = {
                'id': item.tech_tip_number,
                'title': item.tech_tip_title
            }
    if get_view_type(url) == 'Manual Fix':
        for item in most_recent_items:
            generilized_items[item.id] = {
                'id': item.id,
                'title': item.steps_to_fix_error
            }
    if get_view_type(url) == 'Error':
        for item in most_recent_items:
            generilized_items[item.error_name] = {
                'id': item.error_name,
                'title': item.error_title
            }
    return generilized_items


def return_largest_dict_items(dictionary, num_to_return):
    if type(dictionary) != dict:
        raise TypeError(f'dict expected, received {type(dictionary)}')
    copied_dict = {}
    for key, value in dictionary.items():
        try:
            copied_dict[key] = abs(value)
        except TypeError:
            print('numeric value must be entered')

    sorted_list = [key for key in sorted(copied_dict, key=lambda x: copied_dict[x], reverse=True)]
    sorted_list = sorted_list[:num_to_return]

    return {key: value for (key, value) in dictionary.items() if key in sorted_list}


class TopPercentileView(View):
    form_class = MainSearch
    DEFAULT_PERCENTILE = 70
    template_name = 'resolutions/highest_percentile.html'

    def get(self, request, *args, **kwargs):
        context = {
            'table_choice_form': StatisticalChoiceForm({'table': StatisticalChoiceForm.HPI}),
            'user': Profile.objects.get(user=self.request.user.id) if self.request.user.id else {}
        }
        percentile = self.DEFAULT_PERCENTILE
        if request.GET.get('start_date') and request.GET.get('end_date'):
            form_data = TechTipSearch(request.GET)
            if form_data.is_valid():
                context['end_date'] = form_data.cleaned_data['end_date']
                context['start_date'] = form_data.cleaned_data['start_date']
                percentile = int(form_data.cleaned_data['percentile'])
            else:
                context['end_date'] = {}
                context['start_date'] = {}
                context['previous_end_date'] = {}
                context['previous_start_date'] = {}
                context['comparison_views'] = {}
                context['date_form'] = form_data
                return render(request, self.template_name, context)
        else:
            form_data = TechTipSearch()
            context['end_date'] = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
            context['start_date'] = context['end_date'] - datetime.timedelta(days=30)
        tech_tip_statistics = DataTracking(self.request.path, context['start_date'], context['end_date'])
        context['previous_end_date'] = tech_tip_statistics.previous_end_date
        context['previous_start_date'] = tech_tip_statistics.previous_start_date
        context['comparison_views'] = tech_tip_statistics.get_percentile_views(percentile)
        context['date_form'] = form_data
        context['form'] = self.form_class
        context['data_type'] = get_view_type(self.request.path)
        context['recent'] = generilize_recent_database_call(self.request.path)
        context['movement'] = return_largest_dict_items(get_all_pages_movement(self.request.path), 5)
        return render(request, self.template_name, context)


class DailyViews(View):
    form_class = MainSearch
    template_name = 'resolutions/daily_views.html'

    def get(self, request, *args, **kwargs):
        context = {
            'table_choice_form': StatisticalChoiceForm({'table': StatisticalChoiceForm.TVOT}),
            'user': Profile.objects.get(user=self.request.user.id) if self.request.user.id else {}
        }
        form_data = TechTipDailySearch
        if request.GET.get('period_start') and request.GET.get('period_end'):
            form_data = TechTipDailySearch(request.GET)
            if form_data.is_valid():
                context['daily_views'] = get_daily_views(self.request.path,
                                                         convert_to_start_datetime(form_data.cleaned_data['period_start']),
                                                         form_data.cleaned_data['period_end'])
            else:
                context['daily_views'] = {}
        else:
            context['daily_views'] = get_daily_views(self.request.path,
                                                     convert_to_end_datetime(datetime.date.today())
                                                     -
                                                     datetime.timedelta(days=5),
                                                     convert_to_end_datetime(datetime.date.today()))
        context['date_form'] = form_data
        context['form'] = self.form_class
        context['data_type'] = get_view_type(self.request.path)
        context['recent'] = generilize_recent_database_call(self.request.path)
        context['movement'] = return_largest_dict_items(get_all_pages_movement(self.request.path), 5)
        return render(request, self.template_name, context)


class NewErrorFormView(LoginRequiredMixin, FormView):
    model = Error
    form_class = ErrorForm
    template_name = 'resolutions/error_form.html'

    def get_success_url(self):
        return reverse('resolutions-home')

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        return context


class ManualFixListView(FormMixin, ListView):
    model = ManualFix
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET.get('search'):
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        if request.GET.get('table') == 'TVOT' or request.GET.get('period_start'):
            view = DailyViews.as_view()
            return view(request, *args, **kwargs)
        if request.GET.get('table') == 'HPI' or request.GET.get('start_date'):
            view = TopPercentileView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['table_choice_form'] = StatisticalChoiceForm()
        context['recent'] = generilize_recent_database_call(self.request.path)
        context['data_type'] = get_view_type(self.request.path)
        context['movement'] = return_largest_dict_items(get_all_pages_movement(self.request.path), 5)
        return context


class ManualFixDisplay(FormMixin, DetailView):
    model = ManualFix
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        capture_hit(request)
        record_active_pages()
        record_active_page_ranking()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['comment_form'] = ManualFixCommentForm()
        context['comments'] = ManualFixComment.objects.filter(manual_fix=self.get_object().manual_fix_id)\
            .order_by('-date_comment_made')
        return context


class ManualFixCommentsView(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = ManualFix
    template_name = 'resolutions/manualfix_detail.html'
    form_class = ManualFixCommentForm

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = Profile.objects.get(user=self.request.user)
        form.instance.manual_fix = self.get_object()
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('resolution-manual-detail', kwargs={'slug': self.get_object().slug})


class ManualFixDetail(View):

    def get(self, request, *args, **kwargs):
        view = ManualFixDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ManualFixCommentsView.as_view()
        return view(request, *args, **kwargs)


class ResolutionsResultsView(FormView):
    template_name = 'resolutions/resolutions_search_results.html'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        form_data = MainSearch(request.GET or None)
        if form_data.is_valid():
            query = Query(form_data.cleaned_data['search'], [ProductModelDocument, ErrorDocument])
            self.kwargs['tip_results'], self.kwargs['man_results'], self.kwargs['custom_fixes'] = \
                query.db_resolution_query()
            self.kwargs['es_tt'], self.kwargs['es_man'], self.kwargs['es_uf'] = \
                query.es_resolutions_query(self.kwargs['custom_fixes'],
                                           self.kwargs['tip_results'],
                                           self.kwargs['man_results'])
            self.kwargs['errors'] = query.error_query()
            self.kwargs['models'] = query.model_query()
            self.kwargs['uf_count'] = count_dict_results(self.kwargs['custom_fixes'], self.kwargs['es_uf'])
            self.kwargs['tip_count'] = count_dict_results(self.kwargs['tip_results'], self.kwargs['es_tt'])
            self.kwargs['man_count'] = count_dict_results(self.kwargs['man_results'], self.kwargs['es_man'])
            self.kwargs['error_count'] = count_dict_results(self.kwargs['errors'])
            self.kwargs['model_count'] = count_dict_results(self.kwargs['models'])
            self.kwargs['form'] = form_data
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.kwargs['form']
        context['custom_fixes'] = self.kwargs['custom_fixes']
        context['tip_results'] = self.kwargs['tip_results']
        context['man_results'] = self.kwargs['man_results']
        context['es_tt'] = self.kwargs['es_tt']
        context['es_uf'] = self.kwargs['es_uf']
        context['es_man'] = self.kwargs['es_man']
        context['errors'] = self.kwargs['errors']
        context['models'] = self.kwargs['models']
        context['uf_count'] = self.kwargs['uf_count']
        context['tip_count'] = self.kwargs['tip_count']
        context['man_count'] = self.kwargs['man_count']
        context['errors_count'] = self.kwargs['error_count']
        context['model_count'] = self.kwargs['model_count']
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        return context


class ResolutionsListView(View):

    def get(self, request, *args, **kwargs):
        return redirect('library-home')


class TechTipFixListView(FormMixin, ListView):
    model = TechTipFix
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET.get('search'):
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        if request.GET.get('table') == 'HPI' or request.GET.get('start_date'):
            view = TopPercentileView.as_view()
            return view(request, *args, **kwargs)
        if request.GET.get('table') == 'TVOT' or request.GET.get('period_start'):
            view = DailyViews.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['recent'] = generilize_recent_database_call(self.request.path)
        context['data_type'] = get_view_type(self.request.path)
        context['table_choice_form'] = StatisticalChoiceForm()
        context['movement'] = return_largest_dict_items(get_all_pages_movement(self.request.path), 5)
        return context


class TechTipFixDisplay(FormMixin, DetailView):
    model = TechTipFix
    context_object_name = 'tech_tip'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        capture_hit(request)
        record_active_pages()
        record_active_page_ranking()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pics'] = TechTipPics.objects.filter(tech_tip_number=self.object.tech_tip_id)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['comments'] = TechTipComment.objects.filter(tech_tip=self.get_object().tech_tip_id)\
            .order_by('-date_comment_made')
        context['comment_form'] = TechTipCommentForm()
        return context


class TechTipComments(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = TechTipFix
    template_name = 'resolutions/techtipfix_detail.html'
    form_class = TechTipCommentForm

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = Profile.objects.get(user=self.request.user)
        form.instance.tech_tip = self.get_object()
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('resolutions-tech-tip-detail', kwargs={'slug': self.get_object().slug})


class TechTipDetail(View):

    def get(self, request, *args, **kwargs):
        view = TechTipFixDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = TechTipComments.as_view()
        return view(request, *args, **kwargs)


class ErrorListView(FormMixin, ListView):
    model = Error
    context_object_name = 'errors'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET.get('search'):
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        if request.GET.get('table') == 'TVOT' or request.GET.get('period_start'):
            view = DailyViews.as_view()
            return view(request, *args, **kwargs)
        if request.GET.get('table') == 'HPI' or request.GET.get('start_date'):
            view = TopPercentileView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user.id) if self.request.user.id else {}
        context['recent'] = generilize_recent_database_call(self.request.path)
        context['data_type'] = get_view_type(self.request.path)
        context['table_choice_form'] = StatisticalChoiceForm()
        context['movement'] = return_largest_dict_items(get_all_pages_movement(self.request.path), 5)
        return context


class ErrorDetailView(FormMixin, DetailView):
    model = Error
    context_object_name = 'error'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        capture_hit(request)
        record_active_pages()
        record_active_page_ranking()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tech_tips = TechTipFix.objects.filter(repairs_error=self.object.error_id)
        manual_fixes = ManualFix.objects.filter(repairs_error=self.object.error_id)
        custom_fixes = CustomFixes.objects.filter(repairs_error=self.object.error_id)
        context['user'] = Profile.objects.get(user=self.request.user.id) if self.request.user.id else {}
        context['techTip_count'], context['techTip_modelCount'], \
            context['tech_tips'] = datum.get_products(tech_tips)
        context['manualFix_count'], context['manualFix_modelCount'], \
            context['manual_fixes'] = datum.get_products(manual_fixes)
        context['customFix_count'], context['customFix_modelCount'], \
            context['custom_fixes'] = datum.get_products(custom_fixes)
        return context


class CustomFixesListView(FormMixin, ListView):
    model = CustomFixes
    context_object_name = 'user_fixes'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET.get('search'):
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        if request.GET.get('table') == 'TVOT' or request.GET.get('period_start'):
            view = DailyViews.as_view()
            return view(request, *args, **kwargs)
        if request.GET.get('table') == 'HPI' or request.GET.get('start_date'):
            view = TopPercentileView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user.id) if self.request.user.id else {}
        context['recent'] = generilize_recent_database_call(self.request.path)
        context['data_type'] = get_view_type(self.request.path)
        context['table_choice_form'] = StatisticalChoiceForm()
        context['movement'] = return_largest_dict_items(get_all_pages_movement(self.request.path), 5)
        return context


class CustomFixesDisplay(FormMixin, DetailView):
    model = CustomFixes
    context_object_name = 'user_fix'
    form_class = MainSearch

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        capture_hit(request)
        record_active_pages()
        record_active_page_ranking()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['comments'] = CustomFixComments.objects.filter(fix=self.object.custom_fix_id)\
            .order_by('-date_comment_made')
        context['comment_form'] = CustomFixCommentForm()
        return context


class CustomFixesComment(LoginRequiredMixin, SingleObjectMixin, FormView):
    model = CustomFixes
    template_name = 'resolutions/customfixes_detail.html'
    form_class = CustomFixCommentForm

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = Profile.objects.get(user=self.request.user)
        form.instance.fix = self.get_object()
        form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('user-fix-detail', kwargs={'slug': self.get_object().id_number})


class CustomFixesDetail(View):

    def get(self, request, *args, **kwargs):
        view = CustomFixesDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = CustomFixesComment.as_view()
        return view(request, *args, **kwargs)


class CustomFixesUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomFixes
    context_object_name = 'fix'
    form_class = CustomFixForm
    template_name_suffix = '_update_form'

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('user-fix-detail', kwargs={'slug': self.object.id_number})

    def form_valid(self, form):
        messages.success(self.request, 'fix {fix_id} has been processed and updated'
                         .format(fix_id=form.instance.id_number))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['update_form'] = self.get_form()
        context['form'] = MainSearch()
        return context


class CustomFixesCreateView(LoginRequiredMixin, CreateView):
    model = CustomFixes
    context_object_name = 'fix'
    form_class = CustomFixForm
    template_name_suffix = '_create_form'

    def get(self, request, *args, **kwargs):
        if request.GET:
            view = ResolutionsResultsView.as_view()
            return view(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = Profile.objects.get(user=self.request.user)
        messages.success(self.request, 'Your fix has been processed and created. The ID number is {id_number}'
                         .format(id_number=form.instance.id_number))
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        context['create_form'] = self.get_form()
        context['form'] = MainSearch()
        return context


class CustomFixDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CustomFixes
    context_object_name = 'fix'
    template_name_suffix = '_delete_form'

    def test_func(self):
        if self.get_object().author != self.request.user.profile:
            return False
        return True

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        elif not self.request.user.id:
            return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())
        messages.error(self.request, 'Fix {fix} not deleted.  You are not the original content creator'
                       .format(fix=self.get_object().id_number))
        return redirect(reverse('user-fix'))

    def get_success_url(self):
        return reverse('user-fix')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = Profile.objects.get(user=self.request.user) if self.request.user.id else {}
        return context
