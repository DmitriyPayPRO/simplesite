from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse

from .models import Bb
from .models import Rubric

from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView, DeleteView
from django.views.generic.detail import DetailView, SingleObjectMixin
from django.views.generic.list import ListView
from django.views.generic.dates import ArchiveIndexView, DateDetailView
from django.urls import reverse_lazy, reverse

from django.core.paginator import Paginator

from django.forms import modelformset_factory
from django.forms import inlineformset_factory
from django.forms.formsets import ORDERING_FIELD_NAME

from .forms import BbForm
# Create your views here.

def index(request):
    bbs= Bb.objects.all()
    rubrics = Rubric.objects.all()
    paginator = Paginator(bbs, 2)
    if 'page' in request.GET:
        page_num = request.GET['page']
    else:
        page_num = 1
    page = paginator.get_page(page_num)
    context={'rubrics':rubrics, 'page': page, 'bbs': page.object_list} 
    return TemplateResponse(request, 'bboard/index.html', context)
    #bbs= Bb.objects.all()
    #rubrics = Rubric.objects.all()
    #context={'bbs':bbs, 'rubrics':rubrics}
    #return render(request, 'bboard/index.html', context)

def by_rubric(request, rubric_id):
    bbs= Bb.objects.filter(rubric=rubric_id)
    rubrics = Rubric.objects.all()
    current_rubric = Rubric.objects.get(pk=rubric_id)
    context={'bbs':bbs, 'rubrics':rubrics, 'current_rubric': current_rubric}
    return render(request, 'bboard/by_rubric.html', context)

class BbIndexView(ArchiveIndexView):
    model = Bb
    date_field = 'published'
    template_name = 'bboard/index.html'
    context_object_name = 'bbs'
    allow_empty = True

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context

class BbCreateView(CreateView):
    template_name='bboard/create.html'
    form_class=BbForm
    success_url=reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['rubrics']=Rubric.objects.all()
        return context

class BbDetailView(DetailView):
   model = Bb

   def get_context_data(self, *args, **kwargs):
       context = super().get_context_data(*args, **kwargs)
       context['rubrics'] = Rubric.objects.all()
       return context

# class BbDetailView(DateDetailView):
#     model = Bb
#     date_field = 'published'
#     month_format = '%m'

#     def get_context_data(self, *args, **kwargs):
#         context = super().get_context_data(*args, **kwargs)
#         context['rubrics'] = Rubric.objects.all()
#         return context

class BbByRubricView(SingleObjectMixin, ListView):
    template_name = 'bboard/by_rubric.html'
    pk_url_kwarg = 'rubric_id'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object(queryset=Rubric.objects.all())
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.object.bb_set.all()
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['current_rubric'] = self.object
        context['rubrics'] = Rubric.objects.all()
        context['bbs'] = context['object_list']        
        return context

class BbAddView(FormView):
    template_name = 'bboard/create.html'
    form_class = BbForm
    initial = {'price': 0.0}

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
    
    def get_form(self, form_class=None):
        self.object = super().get_form(form_class)
        return self.object

    def get_success_url(self):
        return reverse('bboard:by_rubric',
            kwargs={'rubric_id':self.object.cleaned_data['rubric'].pk})

class BbEditView(UpdateView):
    model = Bb
    form_class = BbForm
    success_url = reverse_lazy('index')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context

class BbDeleteView(DeleteView):
    model = Bb
    success_url = reverse_lazy('index')

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['rubrics'] = Rubric.objects.all()
        return context


def add(request):
    bbf = BbForm()
    context = {'form':bbf}
    return render(request, 'bboard/create.html', context)

def add_save(request):
    bbf = BbForm(request.POST)
    if bbf.is_valid():
        bbf.save()
        return HttpResponseRedirect(reverse('by_rubric',
        kwargs={'rubric_id':bbf.cleaned_data['rubric'].pk}))
    else:
        context = {'form': bbf}
        return render(request, 'bboard/create.html', context)

def add_and_save(request):
    if request.method == 'POST':
        bbf = BbForm(request.POST)
        if bbf.is_valid():
            bbf.save()
            return HttpResponseRedirect(reverse('by_rubric',
            kwargs={'rubric_id': bbf.cleaned_data['rubric'].pk}))
        else:
            context = {'form': bbf}
            return render(request, 'bboard/create.html', context)
    else:
        bbf = BbForm()
        context = {'form': bbf}
        return render(request, 'bboard/create.html', context)

def rubrics(request):
    RubricFormSet = modelformset_factory(Rubric, fields=('name',),
                            can_order=True, can_delete=True)

    if request.method == 'POST':
        formset = RubricFormSet(request.POST)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    rubric = form.save(commit=False)
                    rubric.order = form.cleaned_data[ORDERING_FIELD_NAME]
                    rubric.save()
            return redirect('bboard:index')
    else:
        formset = RubricFormSet()
    context = {'formset': formset}
    return render(request, 'bboard/rubrics.html', context)

def bbs(request, rubric_id):
    BbsFormSet = inlineformset_factory(Rubric, Bb, form=BbForm, extra=1)
    rubric = Rubric.objects.get(pk=rubric_id)
    if request.method == 'POST':
        fromset = BbsFormSet(request.POST, instance=rubric)
        if fromset.is_valid():
            fromset.save()
            return redirect('bboard:index')
    else:
        fromset = BbsFormSet(instance=rubric)
    context = {'formset':fromset, 'current_rubric':rubric}
    return render(request,'bboard/bbs.html', context)