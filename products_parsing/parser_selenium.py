import time
import json
import re
from urllib.parse import urlencode, urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from typing import List, Dict, Union, Tuple
from products_parsing.config import *
from filter import contains_banned_words

params = {
    'q': '',  # query
    'gl': 'ru',  # country to search from
    'hl': 'ru',  # language
    'start': 0  # элемент начиная с которого по счету отображать результаты
}

# Настройка Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

service = webdriver.chrome.service.Service('/home/artyom/prac/venv/lib/python3.8/site-packages/seleniumbase/drivers/chromedriver')  # Укажите путь к вашему chromedriver


def get_html_content_selenium(url: str):
    driver = webdriver.Chrome(service=service, options=options)
    url_with_params = f"{url}?{urlencode(params)}"
    driver.get(url_with_params)
    time.sleep(5)  # Задержка 5 секунд
    html = driver.page_source
    driver.quit()
    return html


def get_element_text(soup, css_selector) -> Union[str, None]:
    element = soup.select_one(css_selector)
    return element.text.strip() if element else None


def get_elements_text(soup, css_selector) -> List[Union[str, None]]:
    elements = soup.select(css_selector)
    return [element.text.strip() for element in elements]


def get_domain_name(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    return domain


def collect_search_result(search_url: str, product_websites) -> List[Dict]:
    html_text = get_html_content_selenium(search_url)
    soup = BeautifulSoup(html_text, 'lxml')

    for result in soup.select('.tF2Cxc'):
        title = result.select_one('.DKV0Md').text
        link = result.select_one('.yuRUbf a')['href']
        if any([re.search(marketplace, link) for marketplace in marketplaces]):
            print(f'Нашелся маркетплейс: {title}, {link}')
            continue

        domain_name = get_domain_name(link)
        if any([re.search(domain_name, get_domain_name(new_product['url'])) for new_product in product_websites]):
            print(f'Нашелся уже добавленный сайт: {domain_name}')
            continue

        product_websites.append({'title': title, 'url': link, 'domain_name': domain_name})
        print(f'Нашелся сайт который будем парсить! {domain_name}')
        print('Ожидание перед проверкой следующей страницы 5 с.')
        time.sleep(5)  # Ждём перед запросом следующей страницы
        print('Конец ожидания.')

    print(f'\nДля этой страницы поиска сайты собраны! Всего собрано: {len(product_websites)}')

    return product_websites


def get_products_info(product_websites: List[Dict]) -> List[Dict]:
    products_data = []
    for website in product_websites:
        print(f'\n\nПроверка страницы: {website["url"]}')
        try:
            product_page = get_html_content_selenium(website['url'])
            if contains_banned_words(product_page):
                print(f"Страница по адресу '{website['url']}' содержит запрещённые слова и будет пропущена.")
                continue

            product_soup = BeautifulSoup(product_page, 'html.parser')

            if website['domain_name'] in websites_css_selectors.keys():
                # отлично! селекторы для этой страницы известны!
                print(f'Для сайта с доменным именем {website["domain_name"]} нашлись селекторы!')
                time.sleep(5)

                website_info = websites_css_selectors[website['domain_name']]
                print(f'Информация о веб-сайте с доменным именем {website["domain_name"]}: {website_info}')
                print(product_soup)
                print(product_soup.select(website_info[0]))
                # определяем, находимся ли мы уже на странице товара или еще только на странице с листингом товаров
                if not product_soup.select(website_info[1]['price']):
                    print(f'Находимся на странице с листингом товаров.')
                    # находимся на странице с листингом товаров
                    products_links = product_soup.select(website_info[0])
                    for product in products_links:
                        products_data.extend(parse_product(f'https://{website["domain_name"]}{product["href"]}', website_info))
                else:
                    print('Находимся на странице конкретного товара')
                    products_data.extend(parse_product(website['url'], website_info))
            else:
                print(f'Для сайта с доменным именем {website["domain_name"]} НЕ НАШЛОСЬ селекторов!')
                continue
        except Exception as e:
            print(f"Error parsing {website['url']}: {e}")

    return products_data


def parse_product(product_url, website_params) -> Dict:
    print(f'Ищем продукт по его url: {product_url}')

    html_text = get_html_content_selenium(product_url)
    soup = BeautifulSoup(html_text, 'lxml')

    product_name = soup.select(website_params[1]['name'])
    if len(product_name) != 1:
        product_name = ['']
    else:
        product_name = [product_name[0].text]

    product_price = soup.select(website_params[1]['price'])
    if len(product_price) != 1:
        product_price = ['']
    else:
        product_price = [product_price[0].text]

    product_rating = soup.select(website_params[1]['rating'])
    if len(product_rating) != 1:
        product_rating = [product_rating[0]]
    elif get_domain_name(product_url) == 'www.dns-shop.ru':
        product_rating = [product_rating[0].get('data-rating')]
    elif get_domain_name(product_url) == 'www.vseinstrumenti.ru':
        product_rating = [product_rating[0].get('value')]
    else:
        product_rating = [product_rating[0].text]

    print(product_name, product_price, product_rating)
    product_data = {
        'name': product_name[0],
        'price': product_price[0],
        'rating': product_rating[0],
    }

    reviews_url = soup.select_one(website_params[1]['reviews'])
    product_data['reviews'] = parse_reviews(f'https://{get_domain_name(product_url)}{reviews_url["href"]}', product_data, website_params)

    return product_data


def parse_reviews(reviews_url, product_data: Dict, website_params) -> List[Dict]:
    html_text = get_html_content_selenium(reviews_url)
    soup = BeautifulSoup(html_text, 'lxml')

    print("Теперь парсим отзывы для этого сайта.")
    print(reviews_url)
    reviews = []
    for review_comment in soup.select(website_params[1]['review_comment']):
        reviews.append({'review': review_comment.text})

    print(f'Всего отзывов: {len(reviews)}')

    _ = 0
    for review_rating in soup.select(website_params[1]['review_rating']):
        reviews[_]['rating'] = review_rating
        _ += 1
        if _ == len(reviews):
            break

    return reviews


def collect_products_info(search_url: str) -> Tuple[List[Dict], List[Dict]]:
    product_websites = []
    while len(product_websites) < min_websites_count:
        print(f'Поиск на странице google: {params["start"] // 10 + 1}')
        product_websites = collect_search_result(search_url, product_websites)  # сейвим результаты поиска в google
        params['start'] += 10
        time.sleep(10)
    print(f'\nПолучили: {product_websites}')
    print('Теперь ищем инфу о товарах')
    products_data = get_products_info(product_websites)  # достаем все ссылки на товары, а по ним и инфу о продуктах
    return products_data


def parse(query):
    """
    Принимает запрос и создает json с найденными товарами и их параметрами
    :param query: текстовый запрос пользователя
    :return:
    """

    global params

    # проверка на содержание в запросе пользователя бан-вордов
    if contains_banned_words(query):
        print(f"Запрос '{query}' содержит запрещённые слова и будет отклонён.")
        return

    # в качестве поисковика используем google
    base_url = 'https://www.google.com/'
    search_url = f'https://www.google.com/search'

    cur_page = 0

    params['query'], params['start'] = query, cur_page * 10

    products_data = collect_products_info(search_url)

    print(f'Результат перед упаковкой: {products_data}')

    # Сохраняем данные в JSON файл
    with open('products.json', 'w', encoding='utf-8') as f:
        json.dump(products_data, f, ensure_ascii=False, indent=4)


# Пример использования
parse("купить микроволновку")
