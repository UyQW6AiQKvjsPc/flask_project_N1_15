def number_of_sales(present: int, previous: int):
    """
        Количество продаж
        present - количество на складе
        previous - остаток

    """
    '''print(f'present {present}')
    print(f'previous {previous}')'''
    result = present - previous
    return int(result)


def revenue_for_day(sales: int, price: int):
    """
        Выручка за день
        sales - количество продаж
        price - цена товара

    """
    result = sales * price
    return result


def average_revenue(revenue: int, sales: int):
    """
        Средняя выручка за товар
        revenue - вся выручка
        sales - всего продаж

    """
    result = revenue / sales
    return result


def brand_rating(ratings, count):
    """
        Расчет рейтинга бренда
        ratings - в сумме рейтинг всех продуктов
        count - количество продуктов
    """
    result = round((ratings / count), 2)
    return result
