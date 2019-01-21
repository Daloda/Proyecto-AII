# Generated by Django 2.0.8 on 2019-01-21 19:12

from django.db import migrations, models
import django.db.models.deletion
import main.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='First name')),
                ('last_name', models.CharField(blank=True, max_length=60, verbose_name='Last name')),
                ('birthdate', models.DateField(null=True, verbose_name='Birthdate')),
                ('city', models.CharField(blank=True, max_length=80, verbose_name='City')),
                ('sex', models.CharField(choices=[('M', 'Man'), ('W', 'Woman'), ('N', 'Non-binary')], max_length=1, null=True, verbose_name='Sex')),
                ('rol', models.CharField(choices=[('D', 'Deportivo'), ('A', 'Aventurero'), ('R', 'Rutero')], max_length=1, null=True)),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Is staf')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'auth_user',
            },
            managers=[
                ('objects', main.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('marcaNombre', models.CharField(max_length=30, primary_key=True, serialize=False, verbose_name='Name')),
                ('logo', models.CharField(max_length=100, verbose_name='Logo')),
            ],
        ),
        migrations.CreateModel(
            name='Moto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.CharField(max_length=30, null=True, verbose_name='Photo')),
                ('modelo', models.CharField(max_length=30, verbose_name='Model')),
                ('cilindrada', models.CharField(max_length=30, verbose_name='Displacement')),
                ('potencia_maxima', models.CharField(blank=True, max_length=30, verbose_name='Maximum power')),
                ('periodo_comercializacion', models.CharField(blank=True, max_length=30, verbose_name='Marketing period')),
                ('marcaNombre', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Marca')),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='moto',
            field=models.ManyToManyField(to='main.Moto'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
    ]
