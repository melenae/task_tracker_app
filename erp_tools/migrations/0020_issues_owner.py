from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('erp_tools', '0019_alter_issues_applicant_content_type_nullable'),
    ]

    operations = [
        migrations.AddField(
            model_name='issues',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='erp_tools.projects', verbose_name='Проект'),
        ),
    ]
