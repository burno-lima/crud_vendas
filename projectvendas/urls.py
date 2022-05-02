from django.urls import path
from .views import list_orders, create_order, update_order, delete_order, home, importer, graficos, export

urlpatterns = [
    path('', list_orders, name='home'),
    path('importer', importer, name='importer'),
    path('export', export, name='export'),
    path('graficos', graficos, name='graficos'),
    path('orders', list_orders, name='list_orders'),
    path('new', create_order, name='create_order'),
    path('update/<int:id>', update_order, name='update_order'),
    path('delete/<int:id>', delete_order, name='delete_order'),
]
