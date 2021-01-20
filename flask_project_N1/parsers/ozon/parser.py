# -*- coding: utf-8 -*-
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import date, datetime
from random import choice

import csv
import fake_useragent
import json
import requests

from models import OzonCategory, OzonProduct, OzonProductInfo
from libs_flask.utils import slugify
from multiprocessing import Pool

from main import db


DATE = date.today()
LOGFILE = f"logs/{ DATE }.txt"
PROXIES = open("proxies.txt").read().split("\n")


class OzonPars():

    def __init__(self, url, category_url):
        print(f"Взял: {url}")
        self.csv_name = category_url
        self.proxies = self.get_proxies()
        self.main_url = "https://www.ozon.ru"
        self.url = url
        self.dict = self.get_json()
        self.RESULT = self.parser()
        self.save()

    def parser(self):
        # Размер(0),Бренд(0),Группа(0),Скидка(0),
        LINKS = []
        BRANDS = []
        TITLES = []
        CATEGORIES = []
        ARTICLES = []
        PRICES = []
        DISCOUNTS = []
        IMAGE_LINKS = []
        RATINGS = []
        COMMENTS_COUNT = []
        PRODUCT_COUNT = []

        JSON = self.dict
        state_id = JSON["layout"][0]["stateId"]
        if not state_id.startswith("searchResultsV2"):
            state_id = JSON["layout"][1]["stateId"]

        JSON = json.loads(JSON["widgetStates"][state_id])["items"]
        for item in range(len(JSON)):
            product = JSON[item]
            try:
                cell_tracking_info = product["cellTrackingInfo"]
                component = product["templateState"][0]["components"]
                images = component[0]["components"][0]
                rating_comments_count = component[1]["components"][0]["components"][2]
            except Exception as e:
                continue
            CATEGORIES.append(cell_tracking_info["category"].split("/")[-2])
            BRANDS.append(cell_tracking_info["brand"])
            TITLES.append(cell_tracking_info["title"])
            id = str(cell_tracking_info["id"])
            ARTICLES.append(id)
            try:
                count = self.get_item_count(id)
            except:
                count = "0"
            PRODUCT_COUNT.append(count)
            final_price = cell_tracking_info["finalPrice"]
            DISCOUNTS.append(str(cell_tracking_info["price"] - final_price) + "р")

            PRICES.append(str(final_price) + "р")
            LINKS.append(self.main_url + product["link"])
            try:
                RATINGS.append(round(rating_comments_count["rating"], 3))
            except:
                RATINGS.append("-")
            try:
                COMMENTS_COUNT.append(rating_comments_count["commentsCount"])
            except:
                COMMENTS_COUNT.append("0")
            IMAGE_LINKS.append(images["images"][0])
        # "Название", "Бренд", "Цена", "Скидка", "Рейтинг", "Артикуль", "Количество(шт)", "Кол-во Комментариев",
        #                  "Категория", "Ссылка на товар",
        #                  "Ссылка на картинку товара"
        RESULT = [(name, brand, category, price, discount, rating, article, product_count, comm_count, product_link,
                   image_link) for
                  name, brand, category, price, discount, rating, article, product_count, comm_count, product_link, image_link
                  in
                  zip(TITLES, BRANDS, CATEGORIES, PRICES, DISCOUNTS, RATINGS, ARTICLES, PRODUCT_COUNT, COMMENTS_COUNT,
                      LINKS, IMAGE_LINKS)]
        return RESULT

    def get_item_count(self, id):
        headers, proxies = self.create_headers_and_proxy()
        html = requests.get(
            f"https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=%2Fcart%3Fitem%3D{id}%26tab%3D0%26qty%3D9",
            headers=headers, proxies=proxies).text
        json_html = json.loads(html)
        JSON = json.loads(json_html["widgetStates"]["split-206863-default-1"])
        return JSON["items"][0]["maxQuantity"]

    def csv_writer(self):
        with open(f"Результат/Товары.csv", "a", newline='', encoding="UTF-8") as file:
            writer = csv.writer(file, delimiter=',')
            # name, brand, price, discount, rating, article, product_count, comm_count, product_link, image_link
            for name, brand, category, price, discount, rating, article, product_count, comm_count, product_link, image_link in self.RESULT:
                writer.writerow((name, brand, category, price, discount, rating, article, product_count, comm_count,
                                 product_link, image_link))
            print("Обновил данные")

    def save(self):
        """ Функция сохранения в БД """
        for name, brand, category, price, discount, rating, article, product_count, comm_count, product_link, image_link in self.RESULT:
            # Ищем категорию
            try:
                category_find = OzonCategory.query.filter_by(title=category).first_or_404()
            except:
                category_find = OzonCategory(title=category, slug=slugify(category))
                db.session.add(category_find)
                db.session.commit()
                with open(LOGFILE, 'a', encoding='utf-8') as file:
                    file.write(f"{ DATE } создана новая категория { category }\n\n")
                category_find = OzonCategory.query.filter_by(title=category).first_or_404()

            # Создаём продукт
            ozon_product = OzonProduct(
                category=category_find.title,
                cat_id=category_find.id,
                title=name,
                brand=brand,
                slug=article,
                article=article,
                product_link=product_link,
                image_link=image_link
            )
            db.session.add(ozon_product)
            db.session.commit()
            with open(LOGFILE, 'a', encoding='utf-8') as file:
                file.write(f"{ DATE } создан новый продукт { name }  - slug: { article }\n\n")
            product = OzonProduct.query.filter_by(slug=article).first_or_404()

            # Заполняем информацию о продукте
            ozon_product_info = OzonProductInfo(
                category=category_find.title,
                product=product.title,
                product_id=product.id,
                date=DATE,
                price=price,
                discount=discount,
                rating=rating,
                count=product_count,
                comments_count=comm_count
            )
            db.session.add(ozon_product_info)
            db.session.commit()

    def create_headers_and_proxy(self):
        proxies = {"https:": f"https://{choice(self.proxies)}"}
        headers = {"User-Agent": fake_useragent.UserAgent().random}
        return headers, proxies

    @staticmethod
    def get_proxies():
        result = []
        for proxy in PROXIES:
            splitted = proxy.split(":")
            result.append(f"{splitted[2]}:{splitted[3]}@{splitted[0]}:{splitted[1]}")
        return result

    def get_json(self):
        headers, proxies = self.create_headers_and_proxy()
        html = requests.get(self.url, headers=headers, proxies=proxies).json()
        return html


def main(category_url):
    page = 1
    while True:
        request_url = f"https://www.ozon.ru/api/composer-api.bx/page/json/v2?url=%2Fcategory%2F{category_url}%2F%3Flayout_container%3DcategoryMegapagination%26layout_page_index%3D{page}%26page%3D{page}"
        try:
            OzonPars(request_url, category_url)
        except Exception as e:
            print(e)
            break
        page += 1
    print(f"Спарсил: https://www.ozon.ru/category/{category_url}/")


""" Запуск парсера """
if __name__ == '__main__':
    # Меняем лимит рекурсии
    sys.setrecursionlimit(3000)
    # Создаём лог-файл
    with open(LOGFILE, 'w', encoding='utf-8') as file:
        file.write("\n")
    # Время старта парсинга
    start = datetime.now().time()
    urls = open("urls.txt").read().split("\n")
    URLS = [url.split("/")[-2] for url in urls]
    # Парсинг
    with Pool(22) as f:
        f.map(main, URLS)
    # Время завершения парсинга
    finish = datetime.now().time()
    # Вывод результатов парсинга в лог-файл
    with open(LOGFILE, 'a', encoding='utf-8') as file:
        file.write("----------------------------\n")
        file.write(f"======== { DATE } ========\n")
        file.write("----------------------------\n")
        file.write(f"Начато:    { start }\n")
        file.write(f"Закончено: { finish }\n")
        file.write("----------------------------\n")
