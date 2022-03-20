from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only


# render(request, template_name, context=None, content_type=None, status=None, using=None)
@login_required(login_url="login")
@admin_only
def home(request):
    customers = Customer.objects.all()
    orders = Order.objects.all()
    total_orders = orders.count()
    delivered = orders.filter(status='delivered').count()
    pending = orders.filter(status='pending').count()
    context = {
        'customers': customers,
        'orders': orders,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def products(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'accounts/products.html', context)

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def customer(request, customer_pk):
    customer = Customer.objects.get(pk=customer_pk)  #also true for get(id=customer_pk)
    orders = customer.order_set.all()
    order_count = orders.count()

    order_filter = OrderFilter(request.GET, queryset=orders)
    orders = order_filter.qs

    context = {
        'customer': customer,
        'orders': orders,
        'order_count': order_count,
        'order_filter': order_filter
    }
    return render(request, 'accounts/customer.html', context)

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def create_order(request, customer_id):
    OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
    customer = Customer.objects.get(pk=customer_id)
    # form = OrderForm(initial={'customer': customer})
    formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
    if request.method == "POST":
        formset = OrderFormSet(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')   # only / means nothing that redirect to home
    context = {
        'formset': formset,
        'customer_name': customer.name
    }
    return render(request, 'accounts/create_order.html', context)

@login_required(login_url="login")
@allowed_users(allowed_roles=['admin'])
def update_order(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == "POST":
        form = OrderForm(request.POST, instance=order)
        form.save()
        return redirect('/')
    form = OrderForm(instance=order)
    context = {'form': form}
    return render(request, 'accounts/update_order.html', context)

@allowed_users(allowed_roles=['admin'])
def delete_order(request, order_id):
    order = Order.objects.get(id=order_id)
    if request.method == "POST":
        order.delete()
        return redirect('/')
    context = {'item': order}
    return render(request, 'accounts/delete.html', context)

@login_required(login_url="login")
@allowed_users(allowed_roles=['customer'])
def user_page(request):
    orders = request.user.customer.order_set.all()
    total_orders = orders.count()
    delivered = orders.filter(status='delivered').count()
    pending = orders.filter(status='pending').count()
    context = {
        'orders': orders,
        'total_orders': total_orders,
        'delivered': delivered,
        'pending': pending         
        }
    return render(request, 'accounts/user.html', context)


@unauthenticated_user
def login_page(request):

    if request.method == "POST":
        username = request.POST['username']  #access like dictionary
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Username or Password invalid")

    return render(request, 'accounts/login.html')

def logout_page(request):
    logout(request)
    return redirect('login')

@unauthenticated_user
def register_user(request):
    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(request, "Registration successful")
            return redirect('user_page')

    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@login_required(login_url="login")
@allowed_users(allowed_roles=['customer'])
def account_settings(request):
    customer = request.user.customer
    form = CustomerForm(instance=customer)

    if request.method == "POST":
        form = CustomerForm(request.POST, request.FILES, instance=customer)
        if form.is_valid():
            form.save()

    context = {
        'form': form,
    }
    return render(request, 'accounts/account_settings.html', context)