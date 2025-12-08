from django import forms
from django.contrib.auth.models import User
from django.utils.text import slugify

from .models import Accounts, ClientTeams, Companies, DataBases, Issues, Projects, ProjectTeams, Services, Sprints, Users


class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Введите пароль"}),
    )


class EmailRegisterForm(forms.Form):
    name = forms.CharField(
        label="Имя",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Ваше имя"}),
    )
    email = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Не менее 8 символов"}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Повторите пароль"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Пароли должны совпадать.")
        return cleaned_data


class AccountCreateForm(forms.ModelForm):
    class Meta:
        model = Accounts
        fields = ["name", "slug", "content"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название аккаунта"}),
            "slug": forms.TextInput(attrs={"class": "form-control", "placeholder": "slug-unique"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Описание"}),
        }

    manager = forms.ModelChoiceField(
        queryset=Users.objects.none(),
        required=False,
        label="Управляющий",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, **kwargs):
        manager_queryset = kwargs.pop("manager_queryset", Users.objects.none())
        self.is_admin = kwargs.pop("is_admin", False)
        self.instance = kwargs.get("instance", None)
        super().__init__(*args, **kwargs)
        self.fields["manager"].queryset = manager_queryset
        self.fields["manager"].required = self.is_admin
        if self.is_admin:
            if self.instance and self.instance.user_id:
                self.fields["manager"].initial = self.instance.user_id
        else:
            self.fields.pop("manager")

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name")
        if not slug and name:
            slug = slugify(name)
        if not slug:
            raise forms.ValidationError("Нужно указать slug или название.")
        return slug


class AdminUserCreateForm(forms.Form):
    name = forms.CharField(
        label="Имя",
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Полное имя"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "user@example.com"}),
    )
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "+7..."}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Пароль пользователя"}),
    )
    owner = forms.ModelChoiceField(
        queryset=Accounts.objects.all(),
        required=False,
        label="Владелец (Account)",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email


class AdminUserUpdateForm(forms.ModelForm):
    class Meta:
        model = Users
        fields = ["name", "phone", "role", "email", "owner"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Имя"}),  
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+7..."}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "owner": forms.Select(attrs={"class": "form-control"}),
        }


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = ["name", "description", "owner"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название проекта"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Описание проекта"}),
            "owner": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "name": "Название проекта",
            "description": "Описание",
            "owner": "Владелец (Аккаунт)",
        }

    def __init__(self, *args, **kwargs):
        account_queryset = kwargs.pop("account_queryset", Accounts.objects.all())
        super().__init__(*args, **kwargs)
        self.fields["owner"].queryset = account_queryset
        self.fields["owner"].required = True


class ProjectTeamCreateForm(forms.ModelForm):
    class Meta:
        model = ProjectTeams
        fields = ["user", "role", "topic", "job_title"]
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "topic": forms.TextInput(attrs={"class": "form-control", "placeholder": "Тема"}),
            "job_title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Должность"}),
        }
        labels = {
            "user": "Пользователь",
            "role": "Роль",
            "topic": "Тема",
            "job_title": "Должность",
        }

    def __init__(self, *args, **kwargs):
        user_queryset = kwargs.pop("user_queryset", Users.objects.all())
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = user_queryset
        self.fields["user"].required = True


class ProjectTeamUpdateForm(forms.ModelForm):
    class Meta:
        model = ProjectTeams
        fields = ["role", "topic", "job_title"]
        widgets = {
            "role": forms.Select(attrs={"class": "form-control"}),
            "topic": forms.TextInput(attrs={"class": "form-control", "placeholder": "Тема"}),
            "job_title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Должность"}),
        }
        labels = {
            "role": "Роль",
            "topic": "Тема",
            "job_title": "Должность",
        }


class CompanyCreateForm(forms.ModelForm):
    class Meta:
        model = Companies
        fields = ["name", "tax_code", "code", "content"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название компании"}),
            "tax_code": forms.TextInput(attrs={"class": "form-control", "placeholder": "ИНН"}),
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "Код компании"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Описание"}),
        }
        labels = {
            "name": "Название компании",
            "tax_code": "ИНН",
            "code": "Код компании",
            "content": "Описание",
        }


class DatabaseCreateForm(forms.ModelForm):
    class Meta:
        model = DataBases
        fields = ["path", "server", "content", "comment"]
        widgets = {
            "path": forms.TextInput(attrs={"class": "form-control", "placeholder": "Путь к базе данных"}),
            "server": forms.TextInput(attrs={"class": "form-control", "placeholder": "Сервер"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Описание"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Комментарий"}),
        }
        labels = {
            "path": "Путь",
            "server": "Сервер",
            "content": "Описание",
            "comment": "Комментарий",
        }


class CompanyServiceDeskForm(CompanyCreateForm):
    owner = forms.ModelChoiceField(
        queryset=Projects.objects.none(),
        label="Проект",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta(CompanyCreateForm.Meta):
        fields = ["owner"] + CompanyCreateForm.Meta.fields

    def __init__(self, *args, project_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = project_queryset or Projects.objects.none()
        self.fields["owner"].queryset = queryset


class DatabaseServiceDeskForm(DatabaseCreateForm):
    owner = forms.ModelChoiceField(
        queryset=Projects.objects.none(),
        label="Проект",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta(DatabaseCreateForm.Meta):
        fields = ["owner"] + DatabaseCreateForm.Meta.fields

    def __init__(self, *args, project_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = project_queryset or Projects.objects.none()
        self.fields["owner"].queryset = queryset


class ServiceCreateForm(forms.ModelForm):
    class Meta:
        model = Services
        fields = [
            "company",
            "price",
            "time_check",
            "time_dead_line",
            "user",
            "supervisor",
            "applicant",
            "content",
            "to_do_task",
            "create_sd_issue",
            "tags",
        ]
        widgets = {
            "company": forms.Select(attrs={"class": "form-control"}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "time_check": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "time_dead_line": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "user": forms.Select(attrs={"class": "form-control"}),
            "supervisor": forms.Select(attrs={"class": "form-control"}),
            "applicant": forms.Select(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "to_do_task": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "create_sd_issue": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "tags": forms.Textarea(
                attrs={"class": "form-control", "rows": 2, "placeholder": '["tag1", "tag2"]'}
            ),
        }
        labels = {
            "company": "Компания",
            "price": "Цена",
            "time_check": "Время проверки",
            "time_dead_line": "Время дедлайна",
            "user": "Ответственный",
            "supervisor": "Контролер",
            "applicant": "Заявитель",
            "content": "Содержание",
            "to_do_task": "Запросить данные",
            "create_sd_issue": "Создание SD Issue",
            "tags": "Теги",
        }

    def __init__(self, *args, company_queryset=None, user_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        companies = company_queryset or Companies.objects.none()
        users = user_queryset or Users.objects.none()
        self.fields["company"].queryset = companies
        self.fields["company"].required = True
        self.fields["company"].empty_label = "---------"
        self.fields["user"].queryset = users
        self.fields["user"].empty_label = "---------"
        self.fields["supervisor"].queryset = users
        self.fields["supervisor"].empty_label = "---------"
        self.fields["supervisor"].required = False
        self.fields["applicant"].queryset = users
        self.fields["applicant"].empty_label = "---------"
        self.fields["applicant"].required = False

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        if isinstance(tags, str) and tags.strip():
            try:
                import json

                return json.loads(tags)
            except json.JSONDecodeError:
                raise forms.ValidationError("Укажите теги в формате JSON, например [\"tag1\", \"tag2\"].")
        return tags or []


class IssueForm(forms.ModelForm):
    APPLICANT_TYPE_CHOICES = [
        ("user", "Пользователь"),
        ("client", "Заказчик"),
    ]

    class Meta:
        model = Issues
        fields = [
            "name",
            "content",
            "Companies",
            "DataBases",
            "Services",
            "users",
            "supervisor",
            "status",
            "priority",
            "parent",
            "sprint",
            "deadline",
            "date_check",
            "date_start_plan",
            "date_end_plan",
            "time_dead_line",
            "time_check",
            "sla_reac",
            "sla_exec",
            "sla_check",
            "sla_deadline",
            "comment",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Название заявки"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Описание"}),
            "Companies": forms.Select(attrs={"class": "form-control"}),
            "DataBases": forms.Select(attrs={"class": "form-control"}),
            "Services": forms.Select(attrs={"class": "form-control"}),
            "users": forms.Select(attrs={"class": "form-control"}),
            "supervisor": forms.Select(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
            "parent": forms.Select(attrs={"class": "form-control"}),
            "sprint": forms.Select(attrs={"class": "form-control"}),
            "deadline": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "date_check": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "date_start_plan": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "date_end_plan": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "time_dead_line": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "time_check": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "sla_reac": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "sla_exec": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "sla_check": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "sla_deadline": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Комментарий"}),
        }
        labels = {
            "name": "Название",
            "content": "Содержание",
            "Companies": "Компания",
            "DataBases": "База данных",
            "Services": "Услуга",
            "users": "Пользователь",
            "applicant": "Заявитель",
            "supervisor": "Руководитель",
            "status": "Статус",
            "priority": "Приоритет",
            "parent": "Родительская заявка",
            "sprint": "Спринт",
            "deadline": "Срок выполнения",
            "date_check": "Дата проверки",
            "date_start_plan": "Дата начала планирования",
            "date_end_plan": "Дата окончания планирования",
            "time_dead_line": "Время дедлайна",
            "time_check": "Время проверки",
            "sla_reac": "СЛА реакции",
            "sla_exec": "СЛА выполнения",
            "sla_check": "СЛА проверки",
            "sla_deadline": "СЛА дедлайна",
            "comment": "Комментарий",
        }

    def __init__(self, *args, parent_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["Companies"].queryset = Companies.objects.order_by("name")
        self.fields["Companies"].required = False
        self.fields["DataBases"].queryset = DataBases.objects.order_by("path")
        self.fields["DataBases"].required = False
        self.fields["Services"].queryset = Services.objects.order_by("id")
        self.fields["Services"].required = False
        users_qs = Users.objects.order_by("name")
        self.fields["users"].queryset = users_qs
        self.fields["supervisor"].queryset = users_qs
        self.fields["supervisor"].required = False
        self.fields["parent"].queryset = (parent_queryset or Issues.objects.all()).order_by("-date_create")
        self.fields["parent"].required = False
        self.fields["sprint"].queryset = Sprints.objects.order_by("-date_create")
        self.fields["sprint"].required = False
        self.fields["priority"].required = False
        self.fields["deadline"].required = False
        self.fields["date_check"].required = False
        self.fields["date_start_plan"].required = False
        self.fields["date_end_plan"].required = False
        self.fields["time_dead_line"].required = False
        self.fields["time_check"].required = False
        self.fields["sla_reac"].required = False
        self.fields["sla_exec"].required = False
        self.fields["sla_check"].required = False
        self.fields["sla_deadline"].required = False
        
        # Сохраняем исходный статус для проверки изменения
        if self.instance and self.instance.pk:
            self.initial_status = self.instance.status
        else:
            self.initial_status = None

        # Поля для инициатора (GenericForeignKey)
        # Поле выбора типа инициатора
        applicant_type_initial = "user"
        applicant_user_initial = None
        applicant_client_initial = None
        
        if self.data.get(self.add_prefix("applicant_type")):
            applicant_type_initial = self.data.get(self.add_prefix("applicant_type"))
        elif self.instance and self.instance.pk:
            # Определяем тип инициатора из GenericForeignKey
            if self.instance.applicant_content_type:
                if self.instance.applicant_content_type.model == 'users':
                    applicant_type_initial = "user"
                    applicant_user_initial = self.instance.applicant_object_id
                elif self.instance.applicant_content_type.model == 'clientteams':
                    applicant_type_initial = "client"
                    applicant_client_initial = self.instance.applicant_object_id
        
        self.fields["applicant_type"] = forms.ChoiceField(
            choices=self.APPLICANT_TYPE_CHOICES,
            initial=applicant_type_initial,
            widget=forms.Select(attrs={"class": "form-control"}),
            label="Тип инициатора",
            required=False,
        )
        
        self.fields["applicant_user"] = forms.ModelChoiceField(
            queryset=Users.objects.order_by("name"),
            required=False,
            widget=forms.Select(attrs={"class": "form-control"}),
            label="Инициатор (пользователь)",
        )
        if applicant_user_initial:
            self.fields["applicant_user"].initial = applicant_user_initial
        
        self.fields["applicant_client"] = forms.ModelChoiceField(
            queryset=ClientTeams.objects.select_related("company").order_by("company__name", "role"),
            required=False,
            widget=forms.Select(attrs={"class": "form-control"}),
            label="Инициатор (клиент)",
        )
        if applicant_client_initial:
            self.fields["applicant_client"].initial = applicant_client_initial

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get("status")
        comment = cleaned_data.get("comment", "").strip()
        applicant_user = cleaned_data.get("applicant_user")
        applicant_client = cleaned_data.get("applicant_client")
        applicant_type = cleaned_data.get("applicant_type") or "user"
        
        if applicant_type == "user":
            if not applicant_user:
                self.add_error("applicant_user", "Выберите пользователя-инициатора.")
            cleaned_data["applicant_client"] = None
        elif applicant_type == "client":
            if not applicant_client:
                self.add_error("applicant_client", "Выберите клиента-инициатора.")
            cleaned_data["applicant_user"] = None
        else:
            self.add_error("applicant_type", "Нужно выбрать тип инициатора.")
        
        # Проверяем, изменился ли статус
        if self.instance and self.instance.pk:
            old_status = self.initial_status
        else:
            old_status = None
        
        # Если статус изменился, комментарий обязателен
        if old_status and status and old_status != status:
            if not comment:
                self.add_error(
                    "comment",
                    "При изменении статуса необходимо указать комментарий."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        applicant_type = self.cleaned_data.get("applicant_type")
        applicant_user = self.cleaned_data.get("applicant_user")
        applicant_client = self.cleaned_data.get("applicant_client")
        
        from django.contrib.contenttypes.models import ContentType
        
        # Устанавливаем GenericForeignKey
        if applicant_type == "user" and applicant_user:
            instance.applicant_content_type = ContentType.objects.get_for_model(Users)
            instance.applicant_object_id = applicant_user.id
        elif applicant_type == "client" and applicant_client:
            instance.applicant_content_type = ContentType.objects.get_for_model(ClientTeams)
            instance.applicant_object_id = applicant_client.id
        else:
            instance.applicant_content_type = None
            instance.applicant_object_id = None
        
        if commit:
            instance.save()
        return instance


class ClientTeamForm(forms.ModelForm):
    class Meta:
        model = ClientTeams
        fields = ["content", "email", "phone", "role", "user", "topic"]
        widgets = {
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Комментарий"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "email@example.com"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "+7..."}),
            "role": forms.Select(attrs={"class": "form-control"}),
            "user": forms.Select(attrs={"class": "form-control"}),
            "topic": forms.TextInput(attrs={"class": "form-control", "placeholder": "Тема"}),
        }
        labels = {
            "content": "Комментарий",
            "email": "Email",
            "phone": "Телефон",
            "role": "Роль",
            "user": "Ответственный",
            "topic": "Тема",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = Users.objects.order_by("name")
        self.fields["user"].required = False
