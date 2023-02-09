# Generated by Django 4.1.6 on 2023-02-09 22:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("groups", "0001_initial"),
        ("pets", "0002_rename_trait_pet_traits_alter_pet_group"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pet",
            name="group",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="pets",
                to="groups.group",
            ),
        ),
    ]