from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Service
from .forms import ServiceForm


def service_list(request):
    services = Service.objects.filter(is_available=True).order_by("-created_at")
    return render(request, "services/service_list.html", {
        "services": services
    })


def service_detail(request, pk):
    service = get_object_or_404(Service, pk=pk)
    return render(request, "services/service_detail.html", {
        "service": service
    })


@login_required
def service_create(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("service_list")

    else:
        form = ServiceForm()

    return render(request, "services/service_form.html", {
        "form": form,
        "action": "Create"
    })


@login_required
def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == "POST":
        form = ServiceForm(request.POST, instance=service)

        if form.is_valid():
            form.save()
            return redirect("service_detail", pk=service.pk)

    else:
        form = ServiceForm(instance=service)

    return render(request, "services/service_form.html", {
        "form": form,
        "action": "Update"
    })


@login_required
def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)

    if request.method == "POST":
        service.delete()
        return redirect("service_list")

    return render(request, "services/service_confirm_delete.html", {
        "service": service
    })