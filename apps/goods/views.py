from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Good
from .forms import GoodForm

def good_list(request):
    # Only show items that are currently available
    goods = Good.objects.filter(status='available').order_by('-created_at')
    return render(request, 'goods/good_list.html', {'goods': goods})

def good_detail(request, pk):
    good = get_object_or_404(Good, pk=pk)
    return render(request, 'goods/good_detail.html', {'good': good})

@login_required
def good_create(request):
    if request.method == 'POST':
        form = GoodForm(request.POST)
        if form.is_valid():
            # Save the form but don't commit to the database yet
            good = form.save(commit=False)
            # Assign the currently logged-in user as the seller
            good.seller = request.user
            good.save()
            return redirect('good_detail', pk=good.pk)
    else:
        form = GoodForm()
    
    return render(request, 'goods/good_form.html', {'form': form, 'action': 'Create'})

@login_required
def good_update(request, pk):
    # Ensure the user can only update their own listings
    good = get_object_or_404(Good, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = GoodForm(request.POST, instance=good)
        if form.is_valid():
            form.save()
            return redirect('good_detail', pk=good.pk)
    else:
        form = GoodForm(instance=good)
        
    return render(request, 'goods/good_form.html', {'form': form, 'action': 'Update'})

@login_required
def good_delete(request, pk):
    # Ensure the user can only delete their own listings
    good = get_object_or_404(Good, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        good.delete()
        return redirect('good_list')
        
    return render(request, 'goods/good_confirm_delete.html', {'good': good})