from django.urls import path
from .views import (ProductTypeListView, ProductFamilyListView, ProductModelDetailView,
                    FirmwareListView, FirmwareDetailView, ManualListView,
                    OptionListView, OptionDetailView, SupplyListView,
                    SupplyDetailView, ResultsListView,
                    )


urlpatterns = [
    path('', ProductTypeListView.as_view(), name='library-home'),
    path('results/', ResultsListView.as_view(), name='library-results'),
    path('firmware/', FirmwareListView.as_view(), name='library-firmware'),
    path('firmware/<slug:slug>', FirmwareDetailView.as_view(), name='library-firmware-detail'),
    path('manual/', ManualListView.as_view(), name='library-manual'),
    path('option/', OptionListView.as_view(), name='library-option'),
    path('option/<slug:slug>', OptionDetailView.as_view(), name='library-option-detail'),
    path('supply/', SupplyListView.as_view(), name='library-supply'),
    path('supply/<slug:slug>', SupplyDetailView.as_view(), name='library-supply-detail'),
    path('<str:type_id>/', ProductFamilyListView.as_view(), name='library-type'),
    path('<str:type_id>/<slug:slug>', ProductModelDetailView.as_view(), name='library-model-detail')
]