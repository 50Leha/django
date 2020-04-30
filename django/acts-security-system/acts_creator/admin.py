import locale

from dateutil.relativedelta import relativedelta
from docxtpl import DocxTemplate

from django.contrib import admin
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse

from acts_creator.models import Employee, Documents, Contribution


locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')


@admin.register(Contribution)
class ContributionAdmin(admin.ModelAdmin):
    """
    Предоставляет возможность работы с сущностью Contribution
    в графическом интерфейсе пользователя.
    Так как данная сущность является связкой между сотрудником и документом,
    то давать пользователю прямой доступ к ней не имеет смысла. Работать с данными модели Contribution
    возможно посредством ее имплементации в инлайнах сущностей Employee или Documents.
    """
    def has_module_permission(self, request):
        """Метод для скрытия из админки промежуточной модели-связки."""
        return False


class ContributionInline(admin.TabularInline):
    """
    Реализация инлайна модели Contribution: позволяет реализовать и настроить
    отображение количества экземпляров сущности "Процент вклада".
    """
    model = Contribution
    extra = 2


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """
    Настраивает отображение атрибутов модели Employee в интерфейсе пользователя.
    Устанавливает порядок отображения атрибутов, возможность фильтрации, группирует
    атрибуты в тематические блоки, реализует возможность поиска по указанным полям.
    В отображение сущности Employee заинлайнена сущность Contribution.
    """

    inlines = (ContributionInline,)
    list_display = ('second_name', 'first_name', 'patronymic', 'id', 'job_duty', 'status_choices',)
    list_filter = ('second_name', 'first_name', 'id', 'job_duty', 'status_choices',)
    fieldsets = (
        (None, {
            'fields': ('second_name', 'first_name', 'patronymic', 'job_duty', 'status_choices',)
        }),
        ('Паспортные данные', {
            'fields': (
                'passport_series', 'passport_number', 'gave_out_by', 'gave_out_date',
                'registred',
            )
        }),
    )
    search_fields = ('second_name', 'first_name', 'job_duty', 'status_choices',)
    ordering = ('second_name', 'first_name',)


def download_rid(modeladmin, request, queryset):
    """
    Функция для формирования и скачивания РИД.
    """
    template = DocxTemplate('acts_creator/templates/acts_creator/rid.docx')
    input_vals = queryset.values()[0]
    date = input_vals['date']
    current_queryset = queryset.first()
    authors = current_queryset.authors_of_RID.all()
    doc_id = queryset.first().id

    context = {
        'date': date.strftime('%d %B %Y'),
        'number': input_vals['number'],
        'name': input_vals['name'],
        'start_date': get_prev_month(date),  # всегда первое число прошлого месяца
        'end_date': date.replace(day=1).strftime('%d.%m.%Y'),
        'annotation': input_vals['annotation'],
        'language_choices': input_vals['language_choices'],
        'authors': authors,
        'doc_id': doc_id,
    }

    template.render(context)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=%s_RID.docx' % (input_vals['number'])
    template.save(response)

    return response


download_rid.short_description = 'Скачать РИД'


def get_prev_month(date):
    """
    Функция возвращает первое число предыдущего месяца.
    """
    month_ago = date - relativedelta(month=(date.month-1))
    first_day_prev_month = month_ago.replace(day=1)

    return first_day_prev_month.strftime('%d.%m.%Y')


def download_act(modeladmin, request, queryset):
    """
    Функция по формированию и скачиванию актов.
    """
    template = DocxTemplate('acts_creator/templates/acts_creator/act.docx')
    input_vals = queryset.values()[0]
    date = input_vals['date']
    current_queryset = queryset.first()
    authors = current_queryset.authors_of_RID.all()

    context = {
        'date': date.strftime('%d %B %Y'),
        'number': input_vals['number'],
        'name': input_vals['name'],
        'authors': authors,
    }

    template.render(context)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = 'attachment; filename=%s_acts.docx' % (input_vals['number'])
    template.save(response)

    return response


download_act.short_description = 'Скачать акты'


@admin.register(Documents)
class DocumentAdmin(admin.ModelAdmin):
    """
    Настраивает отображение атрибутов модели Documents в интерфейсе пользователя.
    Устанавливает, какие атрибуты сущности будут отображаться, и порядок их отображения.
    Определяет кастомные действия администратора по отношению к документам:
    скачать РИД, скачать акты.
    В отображение сущности Documents заинлайнена сущность Contribution.
    """

    inlines = (ContributionInline,)
    list_display = ('name', 'number', 'date',)
    fields = ['date', 'number', 'name', 'annotation', 'language_choices']
    actions = [download_rid, download_act]
