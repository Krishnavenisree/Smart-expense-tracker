from django.db import models
from django.contrib.auth.models import User

CATEGORY_CHOICES = [
    ('Food', 'Food'),
    ('Travel', 'Travel'),
    ('Shopping', 'Shopping'),
    ('Health', 'Health'),
    ('Utilities', 'Utilities'),
    ('Entertainment', 'Entertainment'),
    ('Education', 'Education'),
    ('Other', 'Other'),
]

KEYWORD_MAP = {
    'Food': ['pizza','burger','food','restaurant','cafe','lunch','dinner','breakfast','snack','coffee','tea','grocery','groceries','swiggy','zomato','dominos','kfc','mcdonalds','subway','bread','milk','eggs','rice'],
    'Travel': ['uber','ola','taxi','bus','train','flight','petrol','fuel','diesel','metro','cab','auto','rickshaw','toll','parking','ticket','airfare','hotel','booking'],
    'Shopping': ['amazon','flipkart','myntra','clothes','shirt','shoes','bag','mall','store','shop','purchase','buy','online','meesho','ajio'],
    'Health': ['medicine','doctor','hospital','pharmacy','clinic','health','gym','fitness','yoga','chemist','medical','tablet','syrup','dentist'],
    'Utilities': ['electricity','water','internet','wifi','broadband','phone','bill','recharge','gas','cylinder','rent','maintenance'],
    'Entertainment': ['movie','netflix','spotify','youtube','prime','game','concert','event','show','disney','hotstar','music'],
    'Education': ['book','course','tuition','school','college','fees','exam','coaching','study','library','stationery'],
}


def predict_category(description):
    lower = description.lower()
    for category, keywords in KEYWORD_MAP.items():
        if any(kw in lower for kw in keywords):
            return category
    return 'Other'


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.description} - ₹{self.amount} ({self.category})"
