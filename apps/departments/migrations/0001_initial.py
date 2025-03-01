# Generated by Django 5.1.6 on 2025-02-19 14:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DepartmentType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Bo‘lim turi')),
            ],
            options={
                'verbose_name': 'Bo‘lim turi',
                'verbose_name_plural': 'Bo‘lim turlari',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Bo‘lim nomi')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='departments', to='departments.departmenttype', verbose_name='Bo‘lim turi')),
            ],
            options={
                'verbose_name': 'Bo‘lim',
                'verbose_name_plural': 'Bo‘limlar',
                'ordering': ['type', 'name'],
                'unique_together': {('type', 'name')},
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Lavozim nomi')),
                ('number_of_jobs', models.PositiveIntegerField(help_text='Ushbu lavozimdagi mavjud shtat birliklari soni', verbose_name='Shtat birligi soni')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='positions', to='departments.department', verbose_name='Bo‘lim')),
            ],
            options={
                'verbose_name': 'Lavozim',
                'verbose_name_plural': 'Lavozimlar',
                'ordering': ['department', 'name'],
                'unique_together': {('department', 'name')},
            },
        ),
    ]
