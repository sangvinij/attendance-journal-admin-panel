# Generated by Django 4.2.1 on 2023-06-04 09:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_studyfield_user_date_added_user_is_metodist_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="дата создания"),
        ),
        migrations.AlterField(
            model_name="user",
            name="last_update",
            field=models.DateTimeField(auto_now=True, verbose_name="дата последнего обновления"),
        ),
    ]