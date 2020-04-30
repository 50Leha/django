import datetime

from django.db import models


class Employee(models.Model):
    """
    Модель сотрудник.
    Для сотрудника определены: имя, фамилия, отчество,
    должность, статус (работает или нет), паспортные данные.
    К паспортным данным относятся: серия, номер, кем выдан паспорт,
    дата выдачи паспорта, мето регистрации.
    """

    first_name = models.CharField(
        max_length=50,
        help_text='Имя сотрудника',
        verbose_name='Имя',
    )
    second_name = models.CharField(
        max_length=50,
        help_text='Фамилия сотрудника',
        verbose_name='Фамилия',
    )
    patronymic = models.CharField(
        max_length=50,
        help_text='Отчество сотрудника',
        verbose_name='Отчество',
    )
    job_duty = models.CharField(
        max_length=50,
        help_text='Должность работника',
        verbose_name='Должность',
    )

    WORKING = 'Работает'
    FIRED = 'Не работает'
    STATUS_CHOICES = [
        (WORKING, 'Работает'),
        (FIRED, 'Не работает'),
    ]
    status_choices = models.CharField(
        max_length=11,
        choices=STATUS_CHOICES,
        default=WORKING,
        verbose_name='Статус сотрудника',
    )

    # Определяем паспортные данные сотрудника
    passport_series = models.CharField(
        max_length=4,
        help_text='Серия паспорта',
        null=True,
        verbose_name='Серия паспорта',
    )
    passport_number = models.CharField(
        max_length=6,
        help_text='Номер паспорта',
        null=True,
        verbose_name='Номер паспорта',
    )
    gave_out_by = models.TextField(
        null=True,
        max_length=200,
        help_text='Кем выдан паспорт',
        verbose_name='Кем выдан',
    )
    gave_out_date = models.DateField(
        null=True,
        help_text='Когда выдан паспорт',
        verbose_name='Когда выдан',
    )
    registred = models.TextField(
        null=True,
        max_length=300,
        help_text='Зарегистрирован',
        verbose_name='Зарегистрирован',
    )

    class Meta:
        verbose_name = 'Сотрудника'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.second_name


class Documents(models.Model):
    """
    Модель документ.
    Для документа опеределны: дата его создания, порядковый номер,
    наименование документа, аннотация к документу, авторы интеллектуальной
    деятельности, язык программирования.
    """

    date = models.DateField(
        null=True,
        help_text='Дата создания документа',
        verbose_name='Дата создания документа',
    )
    number = models.CharField(
        default=datetime.date.today().strftime("%d%m%y"),
        max_length=100,
        help_text='Шаблон без порядкового номера документа',
        verbose_name='Номер документа'
    )
    name = models.CharField(
        null=True,
        max_length=100,
        help_text='Наименование документа',
        verbose_name='Наименование документа'
    )
    annotation = models.TextField(
        null=True,
        max_length=300,
        help_text='Текст аннотации',
        verbose_name='Аннотация'
    )
    authors_of_RID = models.ManyToManyField(
        Employee,
        related_name='documents',
        through='Contribution',
        verbose_name='Авторы',
    )

    PYTHON = 'Python'
    JAVA = 'Java'
    JS = 'Java Script'
    GO = 'Go'
    C = 'C'
    C_plus = 'C++'
    LANGUAGE_CHOICES = [
        (PYTHON, 'Python'),
        (JAVA, 'Java'),
        (JS, 'Java Script'),
        (GO, 'Go'),
        (C, 'C'),
        (C_plus, 'C++')
    ]
    language_choices = models.CharField(
        max_length=20,
        choices=LANGUAGE_CHOICES,
        default=PYTHON,
        verbose_name='Язык программирования',
    )

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'

    def __str__(self):
        return '%s, %s' % (self.number, self.name)


class Contribution(models.Model):
    """
    Промежуточная модель для связи сотрудника с документами
    Сотрудники связаны с документами посредством процента
    вклада в результат интеллектуальной деятельности.
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        verbose_name='Сотрудник',
    )
    documents = models.ForeignKey(
        Documents,
        on_delete=models.CASCADE,
        verbose_name='Документы',
    )
    contrib_percent = models.IntegerField(
        help_text='Процент вклада сотрудника',
        null=True,
        verbose_name='Процент вклада',
    )

    class Meta:
        verbose_name = 'Процент вклада'
        verbose_name_plural = 'Проценты вклада'

    def __str__(self):
        return '%s с процентом его вклада в результат деятельности' % (self.employee)
