# Generated by Django 4.2.20 on 2025-05-30 11:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('billing', '0007_alter_invoice_student'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feestructure',
            name='class_level',
            field=models.CharField(choices=[('Grade 1', 'Grade 1'), ('Grade 7', 'Grade 7'), ('Form 1', 'Form 1'), ('Form 4', 'Form 4'), ('Form 6', 'Form 6'), ('UG', 'UG'), ('Grad', 'Grad')], max_length=50),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='term',
            field=models.CharField(choices=[('Term 1', 'Term 1'), ('Term 2', 'Term 2')], max_length=20),
        ),
        migrations.CreateModel(
            name='ParentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent', models.ForeignKey(limit_choices_to={'is_parent': True}, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='billing.studentprofile')),
            ],
        ),
    ]
