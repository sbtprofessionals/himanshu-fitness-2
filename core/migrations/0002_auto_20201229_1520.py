# Generated by Django 3.1 on 2020-12-29 09:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='memebershiprequest',
            name='order_id',
            field=models.CharField(default=123, max_length=6),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='MemeberShipPayment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('currency', models.CharField(max_length=8)),
                ('gateway_name', models.CharField(max_length=25)),
                ('response_message', models.TextField()),
                ('bank_name', models.CharField(max_length=25)),
                ('Payment_mode', models.CharField(max_length=25)),
                ('response_code', models.CharField(max_length=3)),
                ('txn_id', models.TextField()),
                ('txn_amount', models.CharField(max_length=9)),
                ('order_id', models.IntegerField()),
                ('status', models.CharField(max_length=12)),
                ('bank_txn_id', models.CharField(max_length=12)),
                ('txn_date', models.CharField(max_length=23)),
                ('refund_amount', models.IntegerField(default=0.0)),
                ('order_summary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.memebershiprequest')),
            ],
        ),
    ]
