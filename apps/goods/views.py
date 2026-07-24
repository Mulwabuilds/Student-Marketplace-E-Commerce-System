from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.template.loader import render_to_string

from apps.catalog.models import Category

# Make sure to import your new forms and the GoodImage model
from .models import Good, GoodImage
from .forms import GoodForm, GoodImageForm

class GoodListView(ListView):
    model = Good
    template_name = 'goods/good_list.html'
    context_object_name = 'goods'

    def get_queryset(self):
        # 1. Base query: Only show items that are 'available'
        queryset = Good.objects.filter(status='available')

        # 2. Capture GET parameters from the search bar/filters
        query = self.request.GET.get('q')
        category = self.request.GET.get('category')
        condition = self.request.GET.get('condition')
        price_min = self.request.GET.get('price_min')
        price_max = self.request.GET.get('price_max')

        # 3. Apply filters dynamically if the user provided them
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        if category:
            queryset = queryset.filter(category=category)
        if condition:
            queryset = queryset.filter(condition=condition)
        if price_min:
            queryset = queryset.filter(price__gte=price_min)
        if price_max:
            queryset = queryset.filter(price__lte=price_max)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all().order_by('name')
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('HX-Request'):
            self.object_list = self.get_queryset()
            context = self.get_context_data()
            return HttpResponse(render_to_string('goods/_listing_grid.html', context, request=request))
        return super().get(request, *args, **kwargs)

class GoodDetailView(DetailView):
    model = Good
    template_name = 'goods/good_detail.html'
    context_object_name = 'good'

# --- SECURED CRUD VIEWS BELOW ---

class GoodCreateView(LoginRequiredMixin, CreateView):
    model = Good
    form_class = GoodForm
    template_name = 'goods/good_form.html'
    success_url = reverse_lazy('good_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_form'] = GoodImageForm(self.request.POST, self.request.FILES)
        else:
            context['image_form'] = GoodImageForm()
        return context

    def form_valid(self, form):
        # Assign the logged-in user as the seller
        form.instance.seller = self.request.user 
        
        context = self.get_context_data()
        image_form = context['image_form']
        
        if image_form.is_valid():
            self.object = form.save()
            if image_form.cleaned_data.get('image'):
                GoodImage.objects.create(good=self.object, image=image_form.cleaned_data['image'])
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class GoodUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Good
    form_class = GoodForm
    template_name = 'goods/good_form.html'
    success_url = reverse_lazy('good_list')

    def test_func(self):
        """Ensure only the seller can edit their item."""
        obj = self.get_object()
        return obj.seller == self.request.user 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_form'] = GoodImageForm(self.request.POST, self.request.FILES)
        else:
            context['image_form'] = GoodImageForm()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        image_form = context['image_form']
        
        if image_form.is_valid():
            self.object = form.save()
            if image_form.cleaned_data.get('image'):
                GoodImage.objects.update_or_create(
                    good=self.object,
                    defaults={'image': image_form.cleaned_data['image']}
                )
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class GoodDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Good
    template_name = 'goods/good_confirm_delete.html'
    success_url = reverse_lazy('good_list')

    def test_func(self):
        """Ensure only the seller can delete their item."""
        obj = self.get_object()
        return obj.seller == self.request.user