import re

from libs_flask import calculations


class Handlers:
    """ comment """
    def re_email(self, email):
        """ comment """
        if email:
            self.__res = re.findall(r'^\w+@\w+(?:\.)\w{2,5}$', str(email))
            return self.__res
        return 0

    def re_number(self, number):
        """ comment """
        if number:
            self.__res = re.findall(r'^(?:8|\+7)[1-9][-]*[0-9]{2}[-]*[0-9]{3}[-]*[0-9]{2}[-]*[0-9]{2}$', str(number))
            if not self.__res:
                return [0, 'error']
            return self.__res
        return 0

    def re_login(self, login):
        """ comment """
        if login:
            self.__res = re.findall(r'[А-Яа-я\s]', login)
            if self.__res:
                return [0, 'error']
            self.__res = re.findall(r'^.{10,60}$', login)
            if not self.__res:
                return [0, 'error_len']
            return self.__res
        return 0

    def full_names(self, first_name=None, last_name=None):
        """ comment """
        if first_name:
            self.__res = re.findall(r'^[А-Яа-я]{2,20}$', first_name)
            if not self.__res:
                return [0, 'error_first']
            return self.__res
        elif last_name:
            self.__res = re.findall(r'^[А-Яа-я]{2,25}$', last_name)
            if not self.__res:
                return [0, 'error_first']
            return self.__res
        return 0

    def re_psw(self, psw):
        """ comment """
        if psw:
            self.__res = re.findall(r'[А-Яа-я\s]', psw)
            if self.__res:
                return [0, 'error']
            self.__res = re.findall(r'^.{12,100}$', psw)
            if not self.__res:
                return [0, 'error_len']
            return self.__res
        return 0

    def revenue(self, product_size, price, today_date):
        if product_size:
            information = []
            sales = 0
            for i in product_size:
                if str(i.date) == str(today_date):
                    if information:
                        item = []
                        for j in information:
                            if i.product not in j or i.size not in j:
                                item.append([i.product, i.size, str(i.date), i.store_title, int(i.count), 0])
                        information.append(item[0])
                    else:
                        information.append([
                            i.product, i.size, str(i.date), i.store_title, int(i.count), 0
                        ])
            for i in information:
                for j in product_size:
                    if int(i[2].split('-')[-1]) == int(str(j.date).split('-')[-1]) + 1 and i[0] == j.product and \
                            i[1] == j.size and i[3] == j.store_title:
                        if int(j.count) > i[4]:
                            i[-1] += int(j.count) - i[4]
                            i[4] = int(j.count)
                            i[2] = j.date
                        elif int(j.count) < i[4]:
                            i[4] = int(j.count)
                sales += i[-1]
            res = calculations.revenue_for_day(sales, price)
            return sales, res
        return 0, 0

    def split_temp_items(self, item, email=None, db=None):
        """ comment """
        if item:
            self.__res = re.findall(r'__\w*__', item)
            if email:
                item = item.replace(self.__res[0], '')
            if db:
                return self.__res[0].replace('__', '')
            return item
        return 0


