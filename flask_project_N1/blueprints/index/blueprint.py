from datetime import datetime

from flask import Blueprint, request, redirect, url_for, flash, render_template, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from libs_flask import calculations

from re_handlers import Handlers
from models import *
from main import app, db, mail


indexx = Blueprint(
    'indexx',
    __name__,
    template_folder='templates',
    static_folder='static'
    )


def f(l):
    n = []
    for i in l:
        if i not in n:
            n.append(i)
    return n


@indexx.route('/<user_id>/', methods=['post', 'get'])
def index(user_id):
    """ comment """
    try:
        if user_id != session.get('log')['user_id']:
            return redirect('/welcome/login/0/')
    except:
        return redirect('/welcome/login/0/')
    res = Users.query.filter_by(user_id=user_id).all()
    return render_template('index/index.html', items=res[0], sellers=0, products=0, sales=0, brands=0, title='Главная')


@indexx.route('/<user_id>/categories/<magazine>/', methods=['post', 'get'])
def categories(user_id, magazine):
    """ comment """
    try:
        if user_id != session.get('log')['user_id']:
            return redirect('/welcome/login/0/')
    except:
        return redirect('/welcome/login/0/')
    res = Users.query.filter_by(user_id=user_id).all()
    categories = []
    len_items = []
    sub_subcat = []
    # Этот код делает что-то очень интересное
    if magazine == 'wildberries':
        categories = WildBerriesCategory.query.all()
        len_subcat = [len(i.wild_sub) for i in categories]
        len_sub_subcat = []
        for i in categories:
            gap = []
            gap_info = []
            for j in i.wild_sub:
                l = 0
                sub_gap_info = []
                for h in i.wild_sub_sub:
                    if j.id == h.subcat_id:
                        l += 1
                        sub_gap_info.append(h)
                gap_info.append(sub_gap_info)
                gap.append(l)
            sub_subcat.append(gap_info)
            len_sub_subcat.append(gap)
        len_items = {
            'cat': len(categories),
            'subcat': len_subcat,
            'sub_subcat': len_sub_subcat
        }
    elif magazine == 'ozon':
        categories = [
            3,
            {
                'title': 'Настольные игры',
                'len_body': 4,
                'body': ['Цитадели', 'Cluedo', 'Манчкин', 'Uno']
            },
            {
                'title': 'Одежда',
                'len_body': 4,
                'body': ['Детская', 'Взрослая', 'Шапки', 'Куртки']
            },
            {
                'title': 'Кухонные предметы',
                'len_body': 4,
                'body': ['Ножи', 'Вилки', 'Ложки', 'Тарелки']
            }
        ]
    return render_template('index/categories.html', sub_subcat=sub_subcat, len_items=len_items, categories=categories,
                           items=res[0], title=f'Категории {magazine.capitalize()}', magazine=magazine.capitalize())


@indexx.route('/<user_id>/<magazine>/<int:cat>/<int:subcat>/<int:sub_subcat>/', methods=['post', 'get'])
def wildberries(user_id, magazine, cat, subcat, sub_subcat):
    """ comment """
    try:
        if user_id != session.get('log')['user_id']:
            return redirect('/welcome/login/0/')
    except:
        return redirect('/welcome/login/0/')
    date_now = datetime.today()
    date_now = date_now.strftime("%Y-%m-%d")
    date_now = '2021-01-19'
    items_magazine = []
    products = []
    sub_id, sub_cat, sub_subcategory, category, product_name = 0, '', '', 0, ''
    file = ''
    else_inform = {}
    if magazine == 'wildberries':
        items_magazine = WildBerriesCategory.query.filter_by(id=cat).first()
        for i in items_magazine.wild_sub:
            if i.id == subcat:
                sub_cat = i.title
        for i in items_magazine.wild_sub_sub:
            if i.id == sub_subcat:
                sub_subcategory = i.title
        category = items_magazine.title
    elif magazine == 'ozon':
        items_magazine = OzonProduct.query.filter_by(id=cat).first()
    re_project = Handlers
    res = Users.query.filter_by(user_id=user_id).all()
    if request.method == 'POST':
        if request.form.get('subcat'):
            file = 'subcat.html'
            if magazine == 'wildberries':
                for i in items_magazine.wild_product:
                    if i.sub_subcategory_id == sub_subcat:
                        for j in i.wild_size:
                            products.append({
                                'category': f'{sub_subcategory} {i.title} {j.title}',
                                'rating': i.wild_product_info[0].rating,
                                'comments': i.wild_product_info[0].comments_count,
                                'products': f'',
                                'sales': f'',
                                'revenue': f''
                            })
            elif magazine == 'ozon':
                print(2)
        elif request.form.get('brands'):
            file = 'brands.html'
            all_revenue = 0
            all_sales = 0
            all_else_revenue = 0
            all_else_sales = 0
            all_else = []
            if magazine == 'wildberries':
                for i in items_magazine.wild_product:
                    if i.sub_subcategory_id == sub_subcat:
                        rating = 0
                        comments = 0
                        for j in i.wild_product_info:
                            rating += int(j.rating)
                            if str(date_now) == str(j.date).split(' ')[0]:
                                comments += int(j.comments_count)
                        products.append({
                            'name': f'{i.title}',
                            'rating': '',
                            'comments': '',
                            'products': 0,
                            'sales': 0,
                            'revenue': 0
                        })
                        products = f(products)
                        products[-1]['rating'] = calculations.brand_rating(rating, len(i.wild_product_info))
                        products[-1]['comments'] = comments
                        products[-1]['sales'], products[-1]['revenue'] = re_project.revenue(
                            product_size=i.wild_info,
                            price=int(i.wild_product_info[0].price.replace('р', '')),
                            today_date=date_now, self=''
                        )
                        for j in i.wild_info:
                            if j.date == str(date_now):
                                products[-1]['products'] += int(j.count)
                        all_sales += products[-1]['sales']
                        all_revenue += products[-1]['revenue']
            elif magazine == 'ozon':
                print(2)
            max_sales = 0
            max_revenue = 0
            for i in range(6):
                title_salse = ''
                title_revenue = ''
                max_s = 0
                max_r = 0
                for j in range(len(products)):
                    if i == 0:
                        if products[j]['sales'] > max_sales:
                            title_salse = products[j]['name']
                            max_sales = products[j]['sales']
                        if products[j]['revenue'] > max_revenue:
                            title_revenue = products[j]['name']
                            max_revenue = products[j]['revenue']
                    else:
                        if products[j]['sales'] > max_s and products[j]['sales'] < max_sales:
                            title_salse = products[j]['name']
                            max_s = products[j]['sales']
                        if products[j]['revenue'] > max_r and products[j]['revenue'] < max_revenue:
                            title_revenue = products[j]['name']
                            max_r = products[j]['revenue']
                if i != 0:
                    max_sales = max_s
                    max_revenue = max_r
                    all_else.append({
                        'title_salse': title_salse,
                        'title_revenue': title_revenue,
                        'max_sales': max_sales,
                        'max_revenue': max_revenue
                    })
                else:
                    all_else.append({
                        'title_salse': title_salse,
                        'title_revenue': title_revenue,
                        'max_sales': max_sales,
                        'max_revenue': max_revenue
                    })
                all_else_revenue += max_revenue
                all_else_sales += max_sales
            else_inform = {
                'all_sales': all_sales,
                'all_revenue': all_revenue,
                'all_else': all_else,
                'all_else_sales': all_sales - all_else_sales,
                'all_else_revenue': all_revenue - all_else_revenue
            }
        elif request.form.get('sellers'):
            file = 'sellers.html'
            if magazine == 'wildberries':
                for i in items_magazine.wild_product:
                    if i.sub_subcategory_id == sub_subcat:
                        products.append({
                            'seller': f'{i.title}',
                            'products': f'',
                            'sales': f'',
                            'revenue': f''
                        })
            elif magazine == 'ozon':
                print(2)
        elif request.form.get('trends'):
            file = 'trend.html'
            if magazine == 'wildberries':
                for i in items_magazine.wild_product:
                    if i.sub_subcategory_id == sub_subcat:
                        products.append({
                            'week': f'{str(i.wild_product_info[0].date).split(" ")[0]}',
                            'sales': f'',
                            'revenue': f'',
                            'products': f'',
                            'brands': f'',
                            'reven_product': f''
                        })
            elif magazine == 'ozon':
                print(2)
        elif request.form.get('for_dates'):
            if magazine == 'wildberries':
                for i in items_magazine.wild_product:
                    if i.sub_subcategory_id == sub_subcat:
                        products.append({
                            'frame': f'',
                            'products': f'',
                            'sales': f'',
                            'revenue': f'',
                            'average_price': f'',
                            'average_price_product': f'',
                            'rey': f'',
                            'comments': i.wild_product_info[0].comments_count
                        })
            elif magazine == 'ozon':
                print(2)
            file = 'for_day.html'
    if not file:
        file = 'products.html'
    if file == 'products.html':
        if magazine == 'wildberries':
            for i in items_magazine.wild_product:
                if i.sub_subcategory_id == sub_subcat:
                    for j in i.wild_size:
                        products.append({
                            'photo': i.image_link,
                            'brand': i.title,
                            'sku': i.article,
                            'seller': i.title,
                            'name': f'{sub_subcategory} {j.title}'
                        })
        elif magazine == 'ozon':
            print(2)
    numbers = {
        'category': category,
        'subcat': sub_cat,
        'sub_subcat': sub_subcategory,
        'cat_id': cat,
        'subcat_id': subcat
    }
    len_items = len(products)
    return render_template(f'index/{file}', len_items=len_items, numbers=numbers, items=res[0], title='Сводка', magazine='Wildberries',
                           values=products, else_inform=else_inform)


@indexx.route('/<user_id>/wildberries/<int:cat>/<int:subcat>/item/<product>/', methods=['post', 'get'])
def magazine_item(user_id, cat, subcat, product):
    """ comment """
    try:
        if user_id != session.get('log')['user_id']:
            return redirect('/welcome/login/0/')
    except:
        return redirect('/welcome/login/0/')
    res = Users.query.filter_by(user_id=user_id).all()
    values = {
        'len': 7,
        'else': [
            {
                'date': '16.02.2020', 'product': '43246', 'remains': '5347232', 'price': '6747234',
                'from_warehouse': '5347', 'summ': '253', 'comments': '', 'rating': ''
            },
            {
                'date': '16.02.2020', 'product': '43246', 'remains': '5347232', 'price': '6747234',
                'from_warehouse': '5347', 'summ': '253', 'comments': '', 'rating': ''
            },
            {
                'date': '16.02.2020', 'product': '43246', 'remains': '5347232', 'price': '6747234',
                'from_warehouse': '5347', 'summ': '253', 'comments': '', 'rating': ''
            },
            {
                'date': '16.02.2020', 'product': '43246', 'remains': '5347232', 'price': '6747234',
                'from_warehouse': '5347', 'summ': '253', 'comments': '', 'rating': ''
            },
            {
                'date': '16.02.2020', 'product': '43246', 'remains': '5347232', 'price': '6747234',
                'from_warehouse': '5347', 'summ': '253', 'comments': '', 'rating': ''
            },
            {
                'date': '16.02.2020', 'product': '43246', 'remains': '5347232', 'price': '6747234',
                'from_warehouse': '5347', 'summ': '253', 'comments': '', 'rating': ''
            },
            {
                'date': '16.02.2020', 'product': '43246', 'remains': '5347232', 'price': '6747234',
                'from_warehouse': '5347', 'summ': '253', 'comments': '', 'rating': ''
            },
        ]
    }
    return render_template('index/items.html', title='Описание', items=res[0], values=values)
