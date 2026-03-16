import csv
import json
import datetime
from io import BytesIO
from collections import defaultdict
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Q

from .models import Expense, predict_category
from .forms import ExpenseForm, FilterForm


# ── Auth ──────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = AuthenticationForm(data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'expenses/login.html', {'form': form})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Account created successfully!')
        return redirect('dashboard')
    return render(request, 'expenses/signup.html', {'form': form})


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_filtered_expenses(user, filter_val='all', search=''):
    qs = Expense.objects.filter(user=user)
    today = datetime.date.today()

    if filter_val == 'today':
        qs = qs.filter(date=today)
    elif filter_val == 'week':
        week_ago = today - datetime.timedelta(days=7)
        qs = qs.filter(date__gte=week_ago)
    elif filter_val == 'month':
        qs = qs.filter(date__year=today.year, date__month=today.month)

    if search:
        qs = qs.filter(Q(description__icontains=search) | Q(category__icontains=search) | Q(notes__icontains=search))

    return qs


CATEGORY_COLORS = {
    'Food': '#f97316', 'Travel': '#3b82f6', 'Shopping': '#a855f7',
    'Health': '#22c55e', 'Utilities': '#eab308', 'Entertainment': '#ec4899',
    'Education': '#14b8a6', 'Other': '#94a3b8',
}

CATEGORY_ICONS = {
    'Food': '🍽️', 'Travel': '🚗', 'Shopping': '🛍️', 'Health': '💊',
    'Utilities': '⚡', 'Entertainment': '🎬', 'Education': '📚', 'Other': '📌',
}


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today = datetime.date.today()
    all_expenses = Expense.objects.filter(user=request.user)

    total = all_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    today_total = all_expenses.filter(date=today).aggregate(Sum('amount'))['amount__sum'] or 0
    week_total = all_expenses.filter(date__gte=today - datetime.timedelta(days=7)).aggregate(Sum('amount'))['amount__sum'] or 0
    month_total = all_expenses.filter(date__year=today.year, date__month=today.month).aggregate(Sum('amount'))['amount__sum'] or 0

    recent = all_expenses[:5]

    # Category totals for chart
    cat_data = []
    cat_totals = all_expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    for item in cat_totals:
        cat_data.append({
            'category': item['category'],
            'total': float(item['total']),
            'color': CATEGORY_COLORS.get(item['category'], '#94a3b8'),
            'icon': CATEGORY_ICONS.get(item['category'], '📌'),
        })

    context = {
        'total': total,
        'today_total': today_total,
        'week_total': week_total,
        'month_total': month_total,
        'recent': recent,
        'cat_data': cat_data,
        'cat_data_json': json.dumps(cat_data),
        'total_count': all_expenses.count(),
        'today_count': all_expenses.filter(date=today).count(),
        'week_count': all_expenses.filter(date__gte=today - datetime.timedelta(days=7)).count(),
        'month_count': all_expenses.filter(date__year=today.year, date__month=today.month).count(),
        'category_icons': CATEGORY_ICONS,
        'category_colors': CATEGORY_COLORS,
    }
    return render(request, 'expenses/dashboard.html', context)


# ── Expense CRUD ──────────────────────────────────────────────────────────────

@login_required
def add_expense(request):
    predicted = ''
    form = ExpenseForm(request.POST or None)

    if request.method == 'GET' and request.GET.get('desc'):
        predicted = predict_category(request.GET['desc'])
        return JsonResponse({'category': predicted})

    if request.method == 'POST' and form.is_valid():
        expense = form.save(commit=False)
        expense.user = request.user
        if not expense.category or expense.category == 'Other':
            expense.category = predict_category(expense.description)
        expense.save()
        messages.success(request, f'Expense "{expense.description}" added successfully!')
        return redirect('expense_list')

    return render(request, 'expenses/add_expense.html', {'form': form, 'predicted': predicted, 'title': 'Add Expense'})


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    form = ExpenseForm(request.POST or None, instance=expense)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Expense updated successfully!')
        return redirect('expense_list')
    return render(request, 'expenses/add_expense.html', {'form': form, 'title': 'Edit Expense', 'expense': expense})


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    if request.method == 'POST':
        name = expense.description
        expense.delete()
        messages.success(request, f'"{name}" deleted.')
        return redirect('expense_list')
    return render(request, 'expenses/confirm_delete.html', {'expense': expense})


@login_required
def expense_list(request):
    filter_val = request.GET.get('filter', 'all')
    search = request.GET.get('search', '')
    expenses = get_filtered_expenses(request.user, filter_val, search)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    context = {
        'expenses': expenses,
        'filter': filter_val,
        'search': search,
        'total': total,
        'count': expenses.count(),
        'category_icons': CATEGORY_ICONS,
        'category_colors': CATEGORY_COLORS,
    }
    return render(request, 'expenses/expense_list.html', context)


# ── Analytics ─────────────────────────────────────────────────────────────────

@login_required
def analytics(request):
    all_expenses = Expense.objects.filter(user=request.user)

    cat_totals = all_expenses.values('category').annotate(total=Sum('amount')).order_by('-total')
    grand_total = float(all_expenses.aggregate(Sum('amount'))['amount__sum'] or 0)

    cat_data = []
    for item in cat_totals:
        pct = round(float(item['total']) / grand_total * 100, 1) if grand_total else 0
        cat_data.append({
            'category': item['category'],
            'total': float(item['total']),
            'percent': pct,
            'color': CATEGORY_COLORS.get(item['category'], '#94a3b8'),
            'icon': CATEGORY_ICONS.get(item['category'], '📌'),
        })

    # Daily spending last 30 days
    today = datetime.date.today()
    thirty_ago = today - datetime.timedelta(days=30)
    daily_qs = all_expenses.filter(date__gte=thirty_ago).values('date').annotate(total=Sum('amount')).order_by('date')
    daily_data = [{'date': str(d['date']), 'total': float(d['total'])} for d in daily_qs]

    context = {
        'cat_data': cat_data,
        'cat_data_json': json.dumps(cat_data),
        'daily_data_json': json.dumps(daily_data),
        'grand_total': grand_total,
    }
    return render(request, 'expenses/analytics.html', context)


# ── Reports / Downloads ───────────────────────────────────────────────────────

@login_required
def download_csv(request):
    filter_val = request.GET.get('filter', 'all')
    expenses = get_filtered_expenses(request.user, filter_val)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['#', 'Date', 'Description', 'Category', 'Amount (INR)', 'Notes'])
    for i, e in enumerate(expenses, 1):
        writer.writerow([i, e.date, e.description, e.category, e.amount, e.notes or ''])

    return response


@login_required
def download_pdf(request):
    """Simple HTML-based PDF using browser print. Returns styled HTML page."""
    filter_val = request.GET.get('filter', 'all')
    expenses = get_filtered_expenses(request.user, filter_val)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'expenses/pdf_report.html', {
        'expenses': expenses,
        'total': total,
        'filter': filter_val,
        'username': request.user.username,
        'generated': datetime.date.today(),
    })
