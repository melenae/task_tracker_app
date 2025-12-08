from django.conf import settings
from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Users(models.Model):

    ROLE_CHOICES = [    
        ('admin', 'Администратор'),
        ('user', 'Пользователь'),
    ]

    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=100, blank=True, null=True)
    auth_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='erp_profile',
        null=True,
        blank=True,
        verbose_name='Пользователь системы'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user', verbose_name='Роль')
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name='Имя')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey('Accounts', on_delete=models.SET_NULL, null=True, blank=True)
    permitted_accounts = models.JSONField(default=list, blank=True)

    @property
    def is_admin(self):
        return self.role == 'admin'
    
    def __str__(self):
        return self.name or self.email or f"User #{self.pk}"
    
    
 

class Accounts(models.Model):
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_expired = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')
    name = models.CharField(max_length=150, blank=True, null=True, verbose_name='Название')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='Slug')
    content = models.TextField(blank=True, null=True, verbose_name='Содержание')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='accounts',null=True,blank=True, verbose_name='Manager')  

    class Meta: 
        app_label = 'erp_tools'
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'
        ordering = ['-date_create']

    
    def __str__(self):
        return f"{self.slug} - {self.name}"

    # def save(self, *args, **kwargs):
    #     self.clean()
    #     if not self.slug:
    #         self.slug = slugify(f"{self.name}-{self.date_create}")
    #     super().save(*args, **kwargs)


class Projects(models.Model):
    owner = models.ForeignKey(
        Accounts,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='Project',
    )
    name = models.CharField(max_length=255, verbose_name='Название проекта')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    manager = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='projects',null=True,blank=True, verbose_name='Manager')

    class Meta:
        app_label = 'erp_tools'
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name or f"Project #{self.pk}"


class ProjectTeams(models.Model):

    ROLE_CHOICES = [    
        ('ProjectManager', 'Руководитель проекта'),
        ('FunctionalArchitect', 'Функциональный архитектор'),
        ('TechnicalArchitect', 'Технический архитектор'),
        ('Analyst', 'Аналитик'),
        ('Developer', 'Разработчик'),
        ('Client', 'Клиент'),    
        ('Other', 'Прочая'),
        ('Tester', 'Тестировщик'),
        ('Clerk', 'Клерк'),    
        ('OnlyIssues', 'Only Issues'),
    ]

    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='project_teams',null=True,blank=True, verbose_name='Пользователь') 
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, blank=True, null=True, verbose_name='Роль')
    topic = models.CharField(max_length=255, blank=True, null=True, verbose_name='Тема')
    job_title = models.CharField(max_length=255, blank=True, null=True, verbose_name='Должность')
    owner = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='project_teams',null=True,blank=True, verbose_name='Проект')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')


    class Meta:
        app_label = 'erp_tools'
        verbose_name = 'Команда проекта'
        verbose_name_plural = 'Команды проекта'
        ordering = ['-created_at']

    def __str__(self):
        user_label = self.user.email if self.user and self.user.email else f"User #{self.user_id}"
        return f"{user_label} - {self.role or 'участник'}"



class Companies(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название компании')
    owner = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='companies',null=True,blank=True, verbose_name='Проект')
    tax_code = models.CharField(max_length=255, verbose_name='ИНН')
    code = models.CharField(max_length=255, verbose_name='Код компании')
    content = models.TextField(blank=True, null=True, verbose_name='Содержание')
    applicant = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='companies',null=True,blank=True, verbose_name='Заявитель')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_expired = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')

    class Meta:
        app_label = 'erp_tools'
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
        ordering = ['-date_create']

    def __str__(self):
        return f"{self.name} - {self.code}"



class ClientTeams(models.Model):
    ROLE_CHOICES = [
        ('ProjectManager', 'Руководитель проекта'),
        ('FunctionalArchitect', 'Функциональный архитектор'),
        ('TechnicalArchitect', 'Технический архитектор'),
        ('Analyst', 'Аналитик'),
        ('Developer', 'Разработчик'),
        ('Client', 'Клиент'),
        ('Other', 'Прочая'),
    ]

    company = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='client_teams', verbose_name='Компания')
    content = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='Телефон')
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, blank=True, null=True, verbose_name='Роль')
    user = models.ForeignKey(Users, on_delete=models.SET_NULL, related_name='client_team_responsible', null=True, blank=True, verbose_name='Ответственный')
    topic = models.CharField(max_length=255, blank=True, null=True, verbose_name='Тема')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        app_label = 'erp_tools'
        verbose_name = 'Рабочая группа клиента'
        verbose_name_plural = 'Рабочие группы клиента'
        ordering = ['-date_create']

    def __str__(self):
        return f"{self.company.name} - {self.role or 'Участник'}"


class DataBases(models.Model):
    content = models.TextField(blank=True, null=True, verbose_name='Содержание')
    path = models.CharField(max_length=255, verbose_name='Путь')
    server = models.CharField(max_length=255, verbose_name='Сервер')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    owner = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='data_bases',null=True,blank=True, verbose_name='Проект')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        app_label = 'erp_tools'
        verbose_name = 'База данных'
        verbose_name_plural = 'Базы данных'
        ordering = ['-date_create']

    def __str__(self):
        return f"{self.path} - {self.server}"


class Services(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название услуги')
    content = models.TextField(blank=True, null=True, verbose_name='Содержание')
    owner = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='services', null=True, blank=True, verbose_name='Проект')
    applicant = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='services_as_applicant', null=True, blank=True, verbose_name='Заявитель')
    supervisor = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='services_as_supervisor', null=True, blank=True, verbose_name='Руководитель')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='services_as_user', null=True, blank=True, verbose_name='Пользователь')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_expired = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')

    class Meta:
        app_label = 'erp_tools'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['-date_create']

    def __str__(self):
        return self.name or f"Service #{self.pk}"


class Services(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    time_check = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Время проверки')
    time_dead_line = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Время дедлайна')
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='services_as_responsible', null=True, blank=True, verbose_name='Ответственный')
    content = models.TextField(blank=True, null=True, verbose_name='Содержание')
    to_do_task = models.TextField(blank=True, null=True, verbose_name='Запросить данные')
    create_sd_issue = models.BooleanField(default=False, verbose_name='Создание SD Issue')
    applicant = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='services_as_applicant', null=True, blank=True, verbose_name='Заявитель')
    tags = models.JSONField(default=list, blank=True)
    company = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='services', null=True, blank=True, verbose_name='Компания')
    supervisor = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='services_as_supervisor', null=True, blank=True, verbose_name='Контролер')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_expired = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')

    class Meta:
        app_label = 'erp_tools'
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['-date_create']

    def __str__(self):
        return f"Услуга #{self.pk} - {self.price}"
        


class Sprints(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название спринта')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    date_start = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала')
    date_end = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания')
    project = models.ForeignKey(Projects, on_delete=models.CASCADE, related_name='sprints', null=True, blank=True, verbose_name='Проект')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        app_label = 'erp_tools'
        verbose_name = 'Спринт'
        verbose_name_plural = 'Спринты'
        ordering = ['-date_create']

    def __str__(self):
        return self.name or f"Sprint #{self.pk}"


class Issues(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    content = models.TextField(blank=True, null=True, verbose_name='Содержание')
    Companies = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='issues',null=True,blank=True, verbose_name='Компания')
    date_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    DataBases = models.ForeignKey(DataBases, on_delete=models.CASCADE, related_name='issues',null=True,blank=True, verbose_name='База данных')
    Services = models.ForeignKey(Services, on_delete=models.CASCADE, related_name='issues',null=True,blank=True, verbose_name='Услуга')
    users = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='issues',null=True,blank=True, verbose_name='Пользователь')
    # applicant = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='issues_as_applicant', null=True, blank=True, verbose_name='Заявитель (пользователь)')
    # applicant_client = models.ForeignKey(ClientTeams, on_delete=models.SET_NULL, related_name='issues_as_applicant', null=True, blank=True, verbose_name='Заявитель (клиент)')
    applicant_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'model__in': ['users', 'clientteams']})
    applicant_object_id = models.PositiveIntegerField(null=True, blank=True)
    applicant = GenericForeignKey('applicant_content_type', 'applicant_object_id')
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('waiting', 'Ожидает'),
        ('testing', 'Тестирование'),
        ('done', 'Выполнена'),
        ('closed', 'Закрыта'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True, verbose_name='Родительская задача')
    supervisor = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='issues_as_supervisor', null=True, blank=True, verbose_name='Супервайзер')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    PRIORITY_CHOICES = [
        ('low', 'Низкий'),
        ('medium', 'Средний'),
        ('high', 'Высокий'),
    ]
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name='Приоритет')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='Срок выполнения')
    sprint = models.ForeignKey(Sprints, on_delete=models.CASCADE, related_name='issues',null=True,blank=True, verbose_name='Спринт')
    date_check = models.DateTimeField(null=True, blank=True, verbose_name='Дата проверки')
    date_start_plan = models.DateTimeField(null=True, blank=True, verbose_name='Дата начала планирования')
    date_end_plan = models.DateTimeField(null=True, blank=True, verbose_name='Дата окончания планирования')
    time_dead_line = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Время дедлайна')
    time_check = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Время проверки')
    sla_reac = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='СЛА реакции')
    sla_exec = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='СЛА выполнения')
    sla_check = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='СЛА проверки')
    sla_deadline = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='СЛА дедлайна')
    
    
    class Meta:
        app_label = 'erp_tools'
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-date_create']

    def __str__(self):
        return self.name or f"Issue #{self.pk}"


class IssueComments(models.Model):
    issue = models.ForeignKey(
        Issues,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
        verbose_name="Задача",
    )
    user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
        verbose_name="Пользователь",
    )
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    date_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        app_label = "erp_tools"
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-date_create"]

    def __str__(self):
        return f"Comment #{self.pk} - {self.comment}"

