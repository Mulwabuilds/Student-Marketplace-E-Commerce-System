from django import forms
from apps.goods.models import Good

class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['title', 'description', 'price', 'category', 'condition']
        
        # Adding Bootstrap classes so it looks presentable out of the box
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'What are you selling?'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the item...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price in KES'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
        }