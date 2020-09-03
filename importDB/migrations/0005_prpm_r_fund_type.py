# Generated by Django 3.0.3 on 2020-04-07 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('importDB', '0004_prpm_v_grt_pj_budget_eis'),
    ]

    operations = [
        migrations.CreateModel(
            name='PRPM_r_fund_type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fund_type_id', models.IntegerField()),
                ('fund_type_th', models.CharField(max_length=300)),
                ('fund_source_id', models.CharField(max_length=2)),
                ('fund_type_group', models.IntegerField()),
            ],
        ),
    ]
