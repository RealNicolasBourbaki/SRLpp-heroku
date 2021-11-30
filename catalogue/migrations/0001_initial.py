# Generated by Django 3.2 on 2021-11-30 13:17

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CatalogueEntries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_path', models.CharField(default='', max_length=200)),
                ('entry_name', models.CharField(default='', max_length=100)),
                ('entry_version', models.CharField(default='', max_length=50)),
                ('belongs_to_sub_directory', models.CharField(default='', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='GraphEntries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry_path', models.CharField(default='', max_length=200)),
                ('entry_id', models.CharField(default='', max_length=200)),
                ('entry_name', models.CharField(default='', max_length=200)),
                ('entry_version', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='SubmittedCatelogueEntries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('docfile', models.FileField(upload_to='submitted/%Y/%m/%d')),
                ('username', models.CharField(default='', max_length=200)),
                ('user_email', models.CharField(default='', max_length=200)),
                ('status', models.CharField(choices=[('i', 'In process'), ('a', 'Accepted'), ('r', 'Rejected')], default='i', max_length=20)),
            ],
        ),
    ]
