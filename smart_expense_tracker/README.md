# 💰 Smart Expense Tracker (Django)

A full-featured personal finance tracker built with Django.

---

## 🚀 Setup Instructions

### 1. Install Python
Make sure Python 3.9+ is installed: https://python.org

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install Django
```bash
pip install -r requirements.txt
```

### 4. Run database migrations
```bash
python manage.py makemigrations expenses
python manage.py migrate
```

### 5. Create a superuser (optional, for admin panel)
```bash
python manage.py createsuperuser
```

### 6. Start the development server
```bash
python manage.py runserver
```

### 7. Open in browser
```
http://127.0.0.1:8000/
```

---

## 📁 Project Structure

```
smart_expense_tracker/
├── manage.py               ← Run the project from here
├── settings.py             ← Django configuration
├── urls.py                 ← URL routing
├── requirements.txt        ← Python dependencies
├── db.sqlite3              ← Auto-created database
│
├── expenses/               ← Main app
│   ├── models.py           ← Expense model + category prediction
│   ├── views.py            ← All page logic
│   ├── forms.py            ← Django forms
│   ├── apps.py
│   └── templatetags/
│       └── expense_extras.py  ← Custom template filter
│
└── templates/
    └── expenses/
        ├── base.html          ← Sidebar layout
        ├── login.html         ← Login page
        ├── signup.html        ← Signup page
        ├── dashboard.html     ← Dashboard with charts
        ├── add_expense.html   ← Add / Edit expense form
        ├── expense_list.html  ← All expenses with filters
        ├── analytics.html     ← Charts & category breakdown
        ├── confirm_delete.html
        └── pdf_report.html    ← Printable report
```

---

## ✨ Features

- 🔐 User Login / Signup (Django auth)
- ➕ Add, Edit, Delete expenses
- 🤖 Smart category prediction (keyword-based)
- 📅 Filter: Today / This Week / This Month / All Time
- 🔍 Search by description or category
- 📊 Dashboard with bar + donut charts (Chart.js)
- 📈 Analytics page with daily spending
- 📥 Download CSV report
- 🖨️ Print-friendly PDF report

---

## 🔑 Smart Category Prediction

Type a description and the app will auto-suggest a category:
- "uber ride" → 🚗 Travel
- "pizza order" → 🍽️ Food
- "netflix" → 🎬 Entertainment
- "amazon purchase" → 🛍️ Shopping
- "electricity bill" → ⚡ Utilities
