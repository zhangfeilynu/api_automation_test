# Generated by Django 2.0.2 on 2018-05-11 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api_test', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='automationtestresult',
            name='host',
            field=models.CharField(max_length=1024, verbose_name='测试地址'),
        ),
    ]
