import requests
from bs4 import BeautifulSoup


def get_html(url):
    response = requests.get(url)
    return response.text


def parse_news():
    url = 'https://stopgame.ru/news'  # Замените на URL страницы с новостями
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')

    container = soup.find('div', class_='list-view')
    news_items = container.find_all('div',
                                    class_='_card_1tbpr_1')  # Замените на соответствующий CSS-селектор для элементов новостей
    for item in news_items:
        try:
            prelink = item.find('a', class_='_title_1tbpr_49')['href']  # Замените на CSS-селектор для ссылки на новость
            link = f'https://stopgame.ru{prelink}'
            print(link)
        except Exception as e:
            print(f"Ошибка при обработке новости: {e}")


all_news_data = parse_news()
