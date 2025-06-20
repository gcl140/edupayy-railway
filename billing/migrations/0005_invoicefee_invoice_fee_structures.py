# Generated by Django 4.2.20 on 2025-05-26 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0004_studentprofile_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoiceFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fee_structure', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='billing.feestructure')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoice_fees', to='billing.invoice')),
            ],
        ),
        migrations.AddField(
            model_name='invoice',
            name='fee_structures',
            field=models.ManyToManyField(through='billing.InvoiceFee', to='billing.feestructure'),
        ),
    ]
