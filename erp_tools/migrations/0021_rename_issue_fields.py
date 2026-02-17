from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erp_tools', '0020_issues_owner'),
    ]

    operations = [
        migrations.RenameField(
            model_name='issues',
            old_name='Companies',
            new_name='companies',
        ),
        migrations.RenameField(
            model_name='issues',
            old_name='DataBases',
            new_name='databases',
        ),
        migrations.RenameField(
            model_name='issues',
            old_name='Services',
            new_name='services',
        ),
    ]
