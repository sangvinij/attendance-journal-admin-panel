# Generated by Django 4.2.1 on 2023-06-06 13:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_alter_user_date_added_alter_user_last_update"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="study_fields",
            field=models.ManyToManyField(blank=True, null=True, to="accounts.studyfield", verbose_name="направления"),
        ),
    ]