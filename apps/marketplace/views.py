import itertools

from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldDoesNotExist
from django.shortcuts import render

from apps.goods.models import Good
from apps.services.models import Service
from apps.catalog.models import Category


def _service_has_seller():
    """
    Service currently has no `seller` FK (confirmed gap, see docs/flags.md).
    Dashboard/ownership code checks this instead of assuming the field exists,
    so it degrades gracefully instead of crashing once catalog.Service is
    missing an owner.
    """
    try:
        Service._meta.get_field('seller')
        return True
    except FieldDoesNotExist:
        return False


def _apply_common_filters(queryset, q, category_id, price_min, price_max):
    if q:
        queryset = queryset.filter(title__icontains=q) | queryset.filter(description__icontains=q)
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if price_min:
        queryset = queryset.filter(price__gte=price_min)
    if price_max:
        queryset = queryset.filter(price__lte=price_max)
    return queryset


def browse(request):
    """
    Public, anonymous-friendly listing of all available goods + services.
    Filters (all optional GET params): q, category, price_min, price_max,
    condition (goods only, ignored for services).
    """
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()
    price_min = request.GET.get('price_min', '').strip()
    price_max = request.GET.get('price_max', '').strip()
    condition = request.GET.get('condition', '').strip()

    goods = Good.objects.filter(status='available').select_related('category', 'seller')
    goods = _apply_common_filters(goods, q, category_id, price_min, price_max)
    if condition:
        goods = goods.filter(condition=condition)

    services = Service.objects.filter(is_available=True).select_related('category', 'campus_location')
    services = _apply_common_filters(services, q, category_id, price_min, price_max)
    # `condition` intentionally ignored for services: the model has no such field.

    listings = list(itertools.chain(goods, services))

    context = {
        'listings': listings,
        'categories': Category.objects.all(),
        'query': q,
        'selected_category': category_id,
        'price_min': price_min,
        'price_max': price_max,
        'condition': condition,
    }
    return render(request, 'marketplace/browse.html', context)


@login_required
def dashboard(request):
    """
    Seller's own listings (all statuses, not just available), with edit/delete
    links. Services can't be filtered by owner yet -- Service has no `seller`
    field (see docs/flags.md) -- so that section stays empty with a visible
    notice until catalog.Service gets one, rather than silently showing
    listings that may not belong to this seller.
    """
    goods = Good.objects.filter(seller=request.user).select_related('category')

    services = Service.objects.none()
    services_blocked = not _service_has_seller()
    if not services_blocked:
        services = Service.objects.filter(seller=request.user).select_related('category')

    context = {
        'goods': goods,
        'services': services,
        'services_blocked': services_blocked,
    }
    return render(request, 'marketplace/dashboard.html', context)
