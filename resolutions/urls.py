from django.urls import path
from .views import ResolutionsListView, TechTipFixListView, TechTipDetail,\
    ErrorDetailView, ManualFixDetail, ManualFixListView, CustomFixesListView, \
    CustomFixesDetail, CustomFixesCreateView, CustomFixesUpdateView, CustomFixDeleteView, \
    NewErrorFormView, ErrorListView

urlpatterns = [
    path('', ResolutionsListView.as_view(), name='resolutions-home'),
    path('new/', NewErrorFormView.as_view(), name='resolution-new-error'),
    path('tech-tips/', TechTipFixListView.as_view(), name='resolutions-tech-tip'),
    path('tech-tips/<slug:slug>/', TechTipDetail.as_view(), name='resolutions-tech-tip-detail'),
    path('error/', ErrorListView.as_view(), name='resolutions-error'),
    path('error/<slug:slug>/', ErrorDetailView.as_view(), name='resolutions-error-detail'),
    path('manual/', ManualFixListView.as_view(), name='resolution-manual'),
    path('manual/<slug:slug>/', ManualFixDetail.as_view(), name='resolution-manual-detail'),
    path('fix/', CustomFixesListView.as_view(), name='user-fix'),
    path('fix/new/', CustomFixesCreateView.as_view(), name='user-fix-create'),
    path('fix/<slug:slug>/', CustomFixesDetail.as_view(), name='user-fix-detail'),
    path('fix/update/<slug:slug>/', CustomFixesUpdateView.as_view(), name='user-fix-update'),
    path('fix/delete/<slug:slug>/', CustomFixDeleteView.as_view(), name='user-fix-delete')
]
