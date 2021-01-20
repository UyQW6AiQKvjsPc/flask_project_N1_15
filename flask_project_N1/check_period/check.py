import datetime

from main import db

from models import Users


def check():
    res = Users.query.all()
    time_now = datetime.datetime.today()
    time_now = time_now.strftime("%Y-%m-%d-%H.%M.%S")
    time_now = time_now.split('-')
    time_now[-1] = time_now[-1].split('.')
    for items in res:
        time_end = items.rate_end.split('-')
        time_end[-1] = time_end[-1].split('.')
        try:
            if int(time_now[0]) < int(time_end[0]):
                raise ValueError
            elif int(time_now[0]) == int(time_end[0]) and int(time_now[1]) < int(time_end[1]):
                raise ValueError
            elif int(time_now[0]) == int(time_end[0]) and int(time_now[1]) == int(time_end[1]) and \
                    int(time_now[2]) < int(time_end[2]):
                raise ValueError
            elif int(time_now[0]) == int(time_end[0]) and int(time_now[1]) == int(time_end[1]) and \
                    int(time_now[2]) == int(time_end[2]) and int(time_now[3]) < int(time_end[3]):
                raise ValueError
            elif int(time_now[0]) == int(time_end[0]) and int(time_now[1]) == int(time_end[1]) and \
                    int(time_now[2]) == int(time_end[2]) and int(time_now[3]) < int(time_end[3]) and \
                    int(time_now[4]) < int(time_end[4]):
                raise ValueError
            elif int(time_now[0]) == int(time_end[0]) and int(time_now[1]) == int(time_end[1]) and \
                    int(time_now[2]) == int(time_end[2]) and int(time_now[3]) < int(time_end[3]) and \
                    int(time_now[4]) == int(time_end[4]) and int(time_now[5]) < int(time_end[5]):
                raise ValueError
        except ValueError:
            reload = Users.query.filter_by(user_id=items.user_id).update({
                'rate_start': None,
                'rate_end': None,
                'rate_name': None
            })
            db.session.commit()
    return 0


if __name__ == '__main__':
    check()



