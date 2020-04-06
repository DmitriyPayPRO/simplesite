from django import forms
from django.forms.widgets import Select

from .models import Bb, Rubric

class BbForm(forms.ModelForm):
    title = forms.CharField(label='Название товара')
    content = forms.CharField(label='Описание',
            widget=forms.widgets.Textarea())
    price = forms.DecimalField(label= 'Цена', decimal_places=2)
    rubric = forms.ModelChoiceField(queryset=Rubric.objects.all(),
            label='Рубрика', help_text='Не забудьте задать рубрику!',
            widget=forms.widgets.Select(attrs={'size':8}))

    class Meta:
        model = Bb
        fields=('title','content', 'price', 'rubric')