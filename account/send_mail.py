from django.core.mail import send_mail

HOST = 'localhost:8000'


def send_confirmation_email(user, code):
    link = f'http://{HOST}/api/v1/accounts/activate/{code}/'

    server_link = '/api/v1/account/activate/'

    send_mail(
        'Здраствуйте, активируйте ваш аккаунт!',
        f'Что бы активировать ваш аккаунт нужно перейти по ссылке ниже'
        f'\n{link}'
        f'\nСсылка рабоDeleteтает один раз!',
        'satavamas@mail.ru',
        [user],
        fail_silently=False,

    )


def send_confirmation_seller_email(user, code):
    link = f'http://{HOST}/api/v1/accounts/activate_seller/{code}/'

    server_link = '/api/v1/account/activate_seller/'

    send_mail(
        'Здраствуйте, активируйте ваш аккаунт!',
        f'Что бы активировать ваш аккаунт нужно перейти по ссылке ниже'
        f'\n{link}'
        f'\nСсылка рабоDeleteтает один раз!',
        'satavamas@mail.ru',
        [user],
        fail_silently=False,

    )
