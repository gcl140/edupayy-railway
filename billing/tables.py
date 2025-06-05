# import django_tables2 as tables
# from .models import Invoice

# class InvoiceTable(tables.Table):
#     class Meta:
#         model = Invoice
#         template_name = "forms/bootstrap4.html"  # Or tailwind/table.html if using Tailwind
#         fields = ("id", "student", "term", "due_date", "total_amount", "status")


import django_tables2 as tables
from .models import Invoice

class InvoiceTable(tables.Table):
    student = tables.Column(accessor='student.user.first_name', verbose_name="Student")
    due_date = tables.DateColumn(format="Y-m-d", verbose_name="Due Date")
    total_amount = tables.Column(attrs={"td": {"class": "text-right font-medium"}})
    status = tables.Column(attrs={"td": {"class": "uppercase text-sm font-semibold"}})

    class Meta:
        model = Invoice
        template_name = "django_tables2/bootstrap4.html"  # or tailwind if using Tailwind
        fields = ("id", "student", "term", "due_date", "total_amount", "status")
