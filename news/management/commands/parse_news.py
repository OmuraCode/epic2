from django.db import IntegrityError
from bs4 import BeautifulSoup as bs
from django.core.management.base import BaseCommand
from requests import get
from datetime import datetime
from multiprocessing import Pool

from news.models import News


def get_html(url: str) -> str:
    response = get(url)
    return response.text


def get_soup(html: str) -> bs:
    return bs(html, 'lxml')


def get_data(soup):
    container = soup.find('div', class_='list-view')
    news_items = container.find_all('div', class_='_card_1tbpr_1')
    res = []
    for item in news_items:
        try:
            prelink = item.find('a', class_='_title_1tbpr_49')['href']
            link = f'https://stopgame.ru{prelink}'
        except Exception as e:
            print(f"Ошибка при обработке новости: {e}")
        try:
            image = item.find('a', class_='_image_1tbpr_17').find('img').get('src')
        except Exception as e:
            print(f"Ошибка при обработке новости: {e}")
            pass
        title = item.find('div', class_='_content_1tbpr_142').find('a', class_='_title_1tbpr_49').text
        data = {
            'link': link,
            'image': image,
            'title': title
        }
        res.append(data)
    return res


def data_save(res):
    for data in res:
        try:
            news = News.objects.create(title=data['title'], image=data['image'], link=data['link'])
        except IntegrityError as e:
            print(f"Запись с title '{data['title']}' уже существует.")
            pass


# def main():
#     url = get_html('https://stopgame.ru/news')
#     soup = get_soup(url)
#     data = get_data(soup)
#     data_save(data)


# if __name__ == '__main__':
#     main()


class Command(BaseCommand):
    help = 'Parsing News'

    def handle(self, *args, **options):
        url = get_html('https://stopgame.ru/news')
        soup = get_soup(url)
        data = get_data(soup)
        data_save(data)

#Запуск
#python manage.py parse_news
