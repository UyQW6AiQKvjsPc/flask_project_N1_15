# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import fake_useragent
import requests

from datetime import date, datetime
from random import choice

from bs4 import BeautifulSoup
from multiprocessing import Pool
from libs_flask.utils import slugify
from models import WildBerriesCategory, WildBerriesSubcategory, WildBerriesSubSubcategory, WildBerriesProduct
from models import WildBerriesProductInfo, WildBerriesStore, WildBerriesSize, WildBerriesCount
from main import db


DATE = date.today()
LOGFILE = f"logs/{ DATE }.txt"
PROXIES = open("proxies.txt").read().split("\n")
URLS = [url for url in open("urls.txt").read().split("\n")]

STORES = {
    "117986": "Казань",
    "507": "Коледино",
    "1699": "Краснодар",
    "2737": "Санкт-Петербург",
    "1733": "Екатеринбург",
    "119400": "Пушкино",
    "116433": "Домодедово",
    "115577": "Крекшино",
    "117501": "Подольск",
    "1193": "Хабаровск",
    "686": "Новосибирск",
    "119261": "FBS",
    "120762": "New"
    }

STORES_LIST = [
    'Подольск',
    'Коледино',
    'Домодедово',
    'Пушкино',
    'Новосибирск',
    'Хабаровск',
    'Краснодар',
    'Екатеринбург',
    'Крекшино',
    'Санкт-Петербург',
    'Казань',
    'FBS'
]


class WildBerries():

    def __init__(self, url):
        print(f"Взял: { url }")
        self.proxies = self.get_proxies()
        self.url = url
        self.constant_url = url
        self.path = self.constant_url.replace('https://www.wildberries.ru/catalog/', '')
        category_and_subcategory = self.path.split('/')
        self.category = category_and_subcategory[0]
        self.subcategory = category_and_subcategory[1]
        self.soup = self.get_soup()
        try:
            self.file_name = self.soup.find("h1", class_="c-h1 catalog-title").text
        except:
            pass
        self.parse()

    @staticmethod
    def get_proxies():
        result = []
        for proxy in PROXIES:
            splitted = proxy.split(":")
            result.append(f"{splitted[2]}:{splitted[3]}@{splitted[0]}:{splitted[1]}")
        return result

    def create_headers_and_proxy(self):
        proxies = {"https:": f"https://{choice(self.proxies)}"}
        headers = {"User-Agent": fake_useragent.UserAgent().random}
        return headers, proxies

    def get_html(self):
        while True:
            try:
                self.headers, self.proxy = self.create_headers_and_proxy()
                req = requests.get(self.url, headers=self.headers, proxies=self.proxy)
                break
            except:
                pass
        return req

    def get_soup(self):
        html = self.get_html()
        soup = BeautifulSoup(html.text, "lxml")
        return soup

    def page_check(self):
        if self.soup.find("div", class_="content404") or self.soup.find("div", id="divGoodsNotFound"):
            print(f"Спарсил: {self.url}")
            return False
        else:
            return True

    def parse(self):
        page_count = 1

        while True:
            self.url = f"{self.constant_url}?page={page_count}"
            print(self.url)
            self.soup = self.get_soup()
            page_count += 1
            check = self.page_check()
            if check:
                data = self.get_content()
                self.save(data)
            else:
                break

    def get_content(self):
        items = self.soup.find_all('div', class_='dtList i-dtList j-card-item')
        titles_1 = self.soup.find_all("strong", class_="brand-name c-text-sm")
        titles_2 = self.soup.find_all("span", class_="goods-name c-text-sm")
        product_links = self.soup.find_all("a", class_="ref_goods_n_p j-open-full-product-card")
        image_links = self.soup.find_all("img", class_="thumbnail")
        commentary_counts = self.soup.find_all("span", class_="dtList-comments-count c-text-sm")
        # Титульники old
        titles_firsts = [title_1.text for title_1 in titles_1]
        titles_seconds = [title_2.text for title_2 in titles_2]
        # Титульники
        NAMES = [title_1.text.replace("/", "")[:-2] for title_1 in titles_1]
        BRANDS = [title_2.text for title_2 in titles_2]

        COMMENTARY_COUNT = [comm.text for comm in commentary_counts][3:]

        PRODUCT_LINKS = ["https://www.wildberries.ru" + link.get("href")[:-13] for link in product_links]

        IMAGE_LINKS = ["http:" + link.get("src") for link in image_links if
                       link.get("src") != " //static.wbstatic.net/i/blank.gif"]

        PRICES, DISCOUNTS, RATINGS, ARTICULES, SIZE_COUNT = self.price_rating_sizename_store_count(items)
        DATA = [
            (name, brand, price, discount, rating, commentary_count, articule, product_link, image_links, size_count)
            for
            name, brand, price, discount, rating, commentary_count, articule, product_link, image_links, size_count
            in
            zip(NAMES, BRANDS, PRICES, DISCOUNTS, RATINGS, COMMENTARY_COUNT, ARTICULES, PRODUCT_LINKS, IMAGE_LINKS,
                SIZE_COUNT)]
        return DATA

    def price_rating_sizename_store_count(self, items):
        api_request = "https://nm-2-card.wildberries.ru/enrichment/v1/api?spp=0&pricemarginCoeff=1.0&onlineBonus=0&emp=0&nm="
        item_order = []
        for block in items:
            checked_ids = []
            item_id = block.get("data-nm-ids")[1:-1]
            checked_ids.append(item_id)
            item_order.append(item_id)
            api_request += item_id + ";"
        while True:
            try:
                response = requests.get(api_request, headers=self.headers, proxies=self.proxy).json()
                break
            except:
                self.headers, self.proxy = self.create_headers_and_proxy()
        RESULT_SHUFLED = []
        RESULT = []
        i = 0
        for price in response["data"]["products"]:
            sale_price = price["salePrice"]
            discount = str(price["price"] - sale_price) + "р"
            RESULT_SHUFLED.append([str(sale_price) + "р", price["rating"], str(price["id"]), discount, []])

            # {117986, 1699, 1733, 119400, 686, 2737, 116433, 115577, 507, 117501}
            # {117986 - Казань, 1699 - Краснодар, 507 - Коледино, 2737 - Санкт - Петербург, 1733 - Екатеринбург, 119400 - Пушкино, 116433 - Домодедово, 115577 - Крекшино
            for size in price["sizes"]:
                for stock in size["stocks"]:
                    RESULT_SHUFLED[i][4].append((size["origName"], stock["qty"], stock["wh"]))
            i += 1
        for id in item_order:
            for data in RESULT_SHUFLED:
                if data[2] == id:
                    RESULT.append([data[0], data[1], data[2], data[3], data[4]])

        # Было значение 100 - хз что оно значит, поставил 110, т.к. была ошибка
        SIZE_COUNT = [[[] for _ in range(24)] for _ in range(110)]
        storage_items = [items[4] for items in RESULT]
        x = 0
        for items in storage_items:
            for item in items:
                size = item[0]
                count = item[1]
                storage_name = STORES[str(item[2])]
                # Т.к. возникала ошибка, сделал логирование в файл
                try:
                    sizes_row = SIZE_COUNT[x]
                    if storage_name == "Подольск":
                        sizes_row[0].append(size)
                        sizes_row[1].append(count)
                    elif storage_name == "Коледино":
                        sizes_row[2].append(size)
                        sizes_row[3].append(count)
                    elif storage_name == "Домодедово":
                        sizes_row[4].append(size)
                        sizes_row[5].append(count)
                    elif storage_name == "Пушкино":
                        sizes_row[6].append(size)
                        sizes_row[7].append(count)
                    elif storage_name == "Новосибирск":
                        sizes_row[8].append(size)
                        sizes_row[9].append(count)
                    elif storage_name == "Хабаровск":
                        sizes_row[10].append(size)
                        sizes_row[11].append(count)
                    elif storage_name == "Краснодар":
                        sizes_row[12].append(size)
                        sizes_row[13].append(count)
                    elif storage_name == "Екатеринбург":
                        sizes_row[14].append(size)
                        sizes_row[15].append(count)
                    elif storage_name == "Крекшино":
                        sizes_row[16].append(size)
                        sizes_row[17].append(count)
                    elif storage_name == "Санкт-Петербург":
                        sizes_row[18].append(size)
                        sizes_row[19].append(count)
                    elif storage_name == "Казань":
                        sizes_row[20].append(size)
                        sizes_row[21].append(count)
                    elif storage_name == "FBS":
                        sizes_row[22].append(size)
                        sizes_row[23].append(count)
                except:
                    with open(LOGFILE, 'a', encoding='utf-8') as file:
                        file.write(f"\n{ DATE } ошибка на числе { x }\n\n")
            x += 1
        PRICES = [i[0] for i in RESULT]
        RATINGS = [i[1] for i in RESULT]
        ARTICULES = [i[2] for i in RESULT]
        DISCOUNTS = [i[3] for i in RESULT]
        return PRICES, DISCOUNTS, RATINGS, ARTICULES, SIZE_COUNT

    def save(self, data):
        """ Функция сохранения в БД """

        # Проверяем наличие склада в БД
        for i in STORES:
            try:
                store = WildBerriesStore.query.filter_by(title=STORES[i]).first_or_404()
            except:
                store = False
            if not store:
                # Создаём склад
                w_store = WildBerriesStore(
                    title=STORES[i],
                    slug=slugify(STORES[i])
                    )
                db.session.add(w_store)
                db.session.commit()

        #Запись информации о товарах в БД
        for name, brand, price, discount, rating, comm_count, articule, product_link, image_link, size_count in data:
            products_path = product_link.replace('https://www.wildberries.ru/catalog/', '')
            wildberries_id_and_prefix = products_path.split('/')
            wildberries_id = wildberries_id_and_prefix[0]

            # Ищем категорию
            try:
                category = WildBerriesCategory.query.filter_by(slug=self.category).first_or_404()
            except:
                category = False
            if not category:
                # Создаём категорию
                w_category = WildBerriesCategory(title='Новая категория', slug=self.category)
                db.session.add(w_category)
                db.session.commit()
                with open(LOGFILE, 'a', encoding='utf-8') as file:
                    file.write(f"{ DATE } создана новая категория { self.category }\n\n")
                category = WildBerriesCategory.query.filter_by(slug=self.category).first()

            # Ищем подкатегорию
            try:
                subcategory = WildBerriesSubcategory.query.filter_by(cat_id=category.id, slug=self.subcategory).first_or_404()
            except:
                subcategory = False
            if not subcategory:
                # Создаём подкатегорию
                sub_cat = WildBerriesSubcategory(
                    category=category.title,
                    cat_id=category.id,
                    title='Новая подкатегория',
                    slug=self.subcategory
                    )
                db.session.add(sub_cat)
                db.session.commit()
                with open(LOGFILE, 'a', encoding='utf-8') as file:
                    file.write(f"{ DATE } создана новая подкатегория { self.subcategory }\n\n")
                subcategory = WildBerriesSubcategory.query.filter_by(cat_id=category.id, slug=self.subcategory).first()

            # Ищем под-подкатегорию
            try:
                sub_subcategory = WildBerriesSubSubcategory.query.filter_by(cat_id=subcategory.id, title=brand).first_or_404()
            except:
                sub_subcategory = False
            if not sub_subcategory:
                # Создаём под-подкатегорию
                sub_sub_cat = WildBerriesSubSubcategory(
                    category=category.title,
                    cat_id=category.id,
                    subcat_id=subcategory.id,
                    subcategory=subcategory.title,
                    title=brand,
                    )
                db.session.add(sub_sub_cat)
                db.session.commit()
                with open(LOGFILE, 'a', encoding='utf-8') as file:
                    file.write(f"{ DATE } создана новая под-подкатегория { brand }\n\n")
                sub_subcategory = WildBerriesSubSubcategory.query.filter_by(cat_id=subcategory.id, title=brand).first()

            # Ищем продукт
            try:
                product = WildBerriesProduct.query.filter_by(slug=wildberries_id).first_or_404()
            except:
                product = False
            if not product:
                # Создаём продукт
                w_product = WildBerriesProduct(
                    category=category.title,
                    cat_id=category.id,
                    subcategory=subcategory.title,
                    subcat_id=subcategory.id,
                    sub_subcategory=sub_subcategory.title,
                    sub_subcategory_id=sub_subcategory.id,
                    title=name,
                    slug=wildberries_id,
                    article=articule,
                    product_link=product_link,
                    image_link=image_link
                    )
                db.session.add(w_product)
                db.session.commit()
                with open(LOGFILE, 'a', encoding='utf-8') as file:
                    file.write(f"{ DATE } создан новый продукт {name} - slug: { wildberries_id }\n\n")
                product = WildBerriesProduct.query.filter_by(slug=wildberries_id).first()

            # Заполняем информацию о продукте
            product_info = WildBerriesProductInfo(
                category=category.title,
                subcategory=subcategory.title,
                sub_subcategory=sub_subcategory.title,
                product=product.title,
                product_id=product.id,
                date=DATE,
                price=price,
                discount=discount,
                rating=rating,
                comments_count=comm_count
                )
            db.session.add(product_info)
            db.session.commit()

            # Заполняем информацией о размерах и наличии на складе
            # Разбиваем size_count по складам
            stores_size_count = list(zip(*[iter(size_count)]*2))
            # Цикл по количеству складов
            for store in range(len(stores_size_count)):
                if len(stores_size_count[store][0]) > 0:
                    # Цикл по количеству размеров на складе
                    for i in range(len(stores_size_count[store][0])):
                        city = STORES_LIST[store]
                        size = str(stores_size_count[store][0][i])
                        count = stores_size_count[store][1][i]
                        store_bd = WildBerriesStore.query.filter_by(title=city).first()
                        # Ищем размер в базе
                        try:
                            print("Ищем размер в базе")
                            size_db = WildBerriesSize.query.filter_by(title=size).first_or_404()
                        except:
                            size_db = False
                        if not size_db:
                            print("Создаём размер")
                            w_size = WildBerriesSize(
                                product=product.title,
                                product_id=product.id,
                                title=size
                                )
                            db.session.add(w_size)
                            db.session.commit()
                            size_db = WildBerriesSize.query.filter_by(title=size).first()
                        # Записываем информацио о количестве на складе нужного размера
                        print("Записываем количество")
                        w_count = ''
                        w_count = WildBerriesCount(
                            product=product.title,
                            size=size_db.title,
                            product_id=product.id,
                            date=DATE,
                            store_id=store_bd.id,
                            store_slug=store_bd.slug,
                            store_title=store_bd.title,
                            count=count
                            )
                        db.session.add(w_count)
                        db.session.commit()
                else:
                    pass


""" Запуск парсера """
if __name__ == '__main__':
    # Меняем лимит рекурсии
    sys.setrecursionlimit(3000)
    # Создаём лог-файл
    with open(LOGFILE, 'w', encoding='utf-8') as file:
        file.write("\n")
    # Время старта парсинга
    start = datetime.now().time()
    # Парсинг
    with Pool(1) as f:
        f.map(WildBerries, URLS)
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
