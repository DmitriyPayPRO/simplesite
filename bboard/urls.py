from django.urls import path

from .views import index, by_rubric
from .views import add_and_save
from .views import BbIndexView
from .views import BbDetailView
from .views import BbByRubricView
from .views import BbAddView
from .views import BbEditView
from .views import BbDeleteView

urlpatterns = [
    path('delete/<int:pk>/', BbDeleteView.as_view(), name='delete'),
    path('edit/<int:pk>/', BbEditView.as_view(), name='edit'),
    path('detail/<int:pk>/', BbDetailView.as_view(), name='detail'),
    path('add/', BbAddView.as_view(), name='add'),
    path('<int:rubric_id>/', BbByRubricView.as_view(), name='by_rubric'),
    path('', BbIndexView.as_view(), name='index'),
]