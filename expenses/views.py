from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Expense
from .forms import ExpenseForm, RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('index')
    return render(request, 'expenses/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('index')
    return render(request, 'expenses/login.html', {'form': form})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
    return redirect('login')


@login_required
def index(request):
    expenses = Expense.objects.filter(user=request.user)

    category = request.GET.get('category', '')
    if category:
        expenses = expenses.filter(category=category)

    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    breakdown = Expense.objects.filter(user=request.user).values('category').annotate(total=Sum('amount')).order_by('-total')

    form = ExpenseForm()
    return render(request, 'expenses/index.html', {
        'expenses': expenses,
        'total': total,
        'form': form,
        'breakdown': breakdown,
        'selected_category': category,
    })


@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
    return redirect('index')


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.POST or None, instance=expense)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('index')
    return render(request, 'expenses/edit.html', {'form': form, 'expense': expense})


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        expense.delete()
    return redirect('index')
