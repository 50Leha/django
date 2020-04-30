"""Модуль содержит методы для интеграции с mailchimp'ом."""
from enum import Enum
import json
import logging
import requests
from requests.exceptions import ConnectionError, ReadTimeout

from mailchimp3 import MailChimp


logger = logging.getLogger(__name__)
__all__ = [
    'ping_MChimp',
    'create_mailchimp_user',
    'add_user_to_trial_workflow',
    'add_user_to_payment_workflow',
    'remove_user_from_workflow',
    'trigger_confirm_email_promo',
    'trigger_welcome_email_promo'
]


MC_ENTRYPOINT = 'https://us4.api.mailchimp.com/3.0'
MC_API_KEY = ''
MC_USER = ''
USER_LIST_ID = ''

TRIAL_WORKFLOW_ID = ''  # Цепочка писем по триалу
CONFIRMATION_EMAIL_ID = ''  # id письма с подтверждением почты
TRIAL_EMAIL_ID = ''  # id письма с приветствием в сервисе

BUY_WORKFLOW_ID = ''  # Цепочка писем по покупкам
CONGRATS_EMAIL_ID = ''  # id письма-поздравления с покупкой

PROMOCODE_WORKFLOW_ID = ''
PROMO_CONFIRM_EMAIL = ''
PROMO_EMAIL_ID = ''


class MChimpStatus(Enum):
    """Используется для преставления статусов пользователя в сервисе MailChimp."""

    subscribed = 'subscribed'
    unsubscribed = 'unsubscribed'
    cleaned = 'cleaned'
    pending = 'pending'
    transactional = 'transactional'


def ping_MChimp():
    """
    Функция посылает get запрос на сервис MailChimp и проверяет серверный ответ.
    Пишет в логи ошибки в случае недоступности сервиса или невалидности логина/API ключа.
    Выставлен таймаут запроса 10 секунд.
    """
    endpoint = '/ping'
    api_url = '{entrypoint}{endpoint}'.format(entrypoint=MC_ENTRYPOINT, endpoint=endpoint)
    auth = (MC_USER, MC_API_KEY)

    try:
        response = requests.get(api_url, auth=auth, timeout=10)
    except (ReadTimeout, ConnectionError):
        error_message = (
            'Expected Status Code is 200, but we`ve got {code} on {url} \n'
            'with auth_params: {auth}'
        ).format(code=response.status_code, url=api_url, auth=auth, data=data)
        logger.error(error_message)
    else:
        response_dict = response.json()
        health_status = response_dict.get('health_status', None)

        if health_status is None:
            error_message = (
                'Got health_status is None with ping_MChimp. Response is {response_dict}'
            ).format(response_dict=response_dict)
            logger.log('ping_MChimp', response_dict)


def create_mailchimp_user(
        email, first_name, last_name, url,
        user_status=MChimpStatus.subscribed.value
):
    """
     Функция создаёт в почтовом сервисе MailChimp пользователя.

    :param email: электронный адрес пользователя
    :param first_name: имя пользователя
    :param last_name: фамилия пользователя
    :param url: ссылка (используется для подтверждения почты)
    :param user_status: статус пользователя в сервисе MailChimp

    :return:
    """
    endpoint = '/lists/{list_id}/members'.format(list_id=USER_LIST_ID)

    api_url = '{entrypoint}{endpoint}'.format(entrypoint=MC_ENTRYPOINT, endpoint=endpoint)
    auth = (MC_USER, MC_API_KEY)

    user_info = {
        'email_address': email,
        'status': user_status,
        'merge_fields': {
            'FNAME': first_name,
            'LNAME': last_name,
            'URL': url
        }
    }
    user_info = json.dumps(user_info)

    response = requests.post(api_url, data=user_info, auth=auth)


def make_request(func_name, email, endpoint):
    """
    Функция формирует точку входа, обект запроса и посылает
    запрос к сервису MailChimp. В случае ошибки пишет сообщение в логи.
    """
    api_url = '{entrypoint}{endpoint}'.format(entrypoint=MC_ENTRYPOINT, endpoint=endpoint)
    auth = (MC_USER, MC_API_KEY)

    user_info = {
        'email_address': email,
    }
    user_info = json.dumps(user_info)

    response = requests.post(api_url, data=user_info, auth=auth)

    if response.status_code != 204:
        logger.error('{func_name} with code={code}'.format(func_name=func_name, code=response.status_code))


def trigger_confirm_email(email, workflow_id=TRIAL_WORKFLOW_ID, email_id=CONFIRMATION_EMAIL_ID):
    """
    Функция триггерит отправку письма с подтверждением почты. Случай регистрации без промокода.

    :param workflow_id: id цепочки писем
    :param email_id: id письма
    :param email: электронный адрес пользователя

    :return:
    """
    func_name = trigger_confirm_email.__name__
    endpoint = (
        '/automations/{workflow_id}/emails/{email_id}/queue'
    ).format(workflow_id=workflow_id, email_id=email_id)

    make_request(func_name, email, endpoint)


def add_user_to_trial_workflow(email, workflow_id=TRIAL_WORKFLOW_ID, email_id=TRIAL_EMAIL_ID):
    """
    Функция добавляет пользователя в очередь цепочки по рассылке писем.
    Случай регистрации без промокода.

    :param workflow_id: id цепочки писем
    :param email_id: id письма
    :param email: электронный адрес пользователя

    :return:
    """
    func_name = add_user_to_trial_workflow.__name__
    endpoint = (
        '/automations/{workflow_id}/emails/{email_id}/queue'
    ).format(workflow_id=workflow_id, email_id=email_id)

    make_request(func_name, email, endpoint)


def add_user_to_payment_workflow(email, workflow_id=BUY_WORKFLOW_ID, email_id=CONGRATS_EMAIL_ID):
    """
    Функция добавляет пользователя в очередь цепочки писем с покупками.
    """
    func_name = add_user_to_payment_workflow.__name__
    endpoint = (
        '/automations/{workflow_id}/emails/{email_id}/queue'
    ).format(workflow_id=workflow_id, email_id=email_id)

    make_request(func_name, email, endpoint)


def remove_user_from_workflow(email, workflow_id=TRIAL_WORKFLOW_ID):
    """
    Функция удаляет пользователя из цепочки писем.
    Случай регистрации без промокода.
    """
    func_name = remove_user_from_workflow.__name__
    endpoint = '/automations/{workflow_id}/removed-subscribers'.format(workflow_id=TRIAL_WORKFLOW_ID)

    make_request(func_name, email, endpoint)


def trigger_confirm_email_promo(email, workflow_id=PROMOCODE_WORKFLOW_ID, email_id=PROMO_CONFIRM_EMAIL):
    """
    Функция триггерит отправку письма с подтверждением почты. Случай регистрации c промокодом.

    :param workflow_id: id цепочки писем
    :param email_id: id письма
    :param email: электронный адрес пользователя

    :return:
    """
    func_name = trigger_confirm_email_promo.__name__
    endpoint = (
        '/automations/{workflow_id}/emails/{email_id}/queue'
    ).format(workflow_id=workflow_id, email_id=email_id)

    make_request(func_name, email, workflow_id, email_id)


def trigger_welcome_email_promo(email, workflow_id=PROMOCODE_WORKFLOW_ID, email_id=PROMO_EMAIL_ID):
    """
    Функция триггерит отправку приветственного письма. Случай регистрации c промокодом.

    :param workflow_id: id цепочки писем
    :param email_id: id письма
    :param email: электронный адрес пользователя

    :return:
    """
    func_name = trigger_welcome_email_promo.__name__
    endpoint = (
        '/automations/{workflow_id}/emails/{email_id}/queue'
    ).format(workflow_id=workflow_id, email_id=email_id)

    make_request(func_name, email, workflow_id, email_id)
