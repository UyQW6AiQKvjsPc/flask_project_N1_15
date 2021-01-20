from random import randint

from flask import Blueprint, request, redirect, url_for, flash, render_template, session
from flask_mail import Message
from werkzeug.security import check_password_hash

from config import Config
from models import Users, TemporaryData
from main import db, mail
from re_handlers import Handlers


profile_b = Blueprint(
    'profile_b',
    __name__,
    template_folder='templates',
    static_folder='static'
    )


@profile_b.route('/<user_id>/', methods=['post', 'get'])
def profile_p(user_id):
    """ comment """
    res = Users.query.filter_by(user_id=user_id).all()
    if not res or res[0].status_reg == 'waiting':
        return redirect('/welcome/login/0/')
    changes = ';'
    re = Handlers()
    if request.method == 'POST':
        if request.form.get('cancel'):
            return render_template('profile_p/profile.html', title='Профиль', items=res[0])
        if request.form.get('submit'):
            login = request.form.get('login')
            if res[0].login != login:
                login = re.re_login(login)
                if len(login) == 2:
                    flash('Не используйте кириллицу и пробельные символы', category='alert-danger')
                    return render_template('profile_p/profile.html', title='Профиль', items=res[0])
                changes = changes + 'login:' + login[0] + ';'
            email = request.form.get('email')
            if res[0].email != email:
                changes['email'] = email
            phone = request.form.get('phone')
            if res[0].phone != phone:
                phone = re.re_number(phone)
                if len(phone) == 2:
                    flash('Введите корректно ваш номер', category='alert-danger')
                    return render_template('profile_p/profile.html', title='Профиль', items=res[0])
                changes = changes + 'phone:' + phone[0] + ';'
            birth = request.form.get('datepicker')
            if res[0].birth:
                if res[0].birth != birth:
                    changes = changes + 'birth:' + birth + ';'
            else:
                changes = changes + 'birth:' + birth + ';'
            gender = request.form.get('gender')
            if res[0].gender:
                if res[0].gender != gender:
                    changes = changes + 'gender:' + gender + ';'
            else:
                changes = changes + 'gender:' + gender + ';'
            if changes:
                temp_user = TemporaryData.query.filter_by(user_id=session.get('log')['user_id']).update(
                    {'temp_items': changes, 'status': 'waiting'})
                db.session.commit()
                return redirect(url_for('profile_b.conf_pass', user_id=user_id))
    return render_template('profile_p/profile.html', title='Профиль', items=res[0])


@profile_b.route('/<user_id>/conf-pass/', methods=['post', 'get'])
def conf_pass(user_id):
    """ comment """
    if user_id != session.get('log')['user_id']:
        return redirect('/welcome/login/0/')
    res = Users.query.filter_by(user_id=user_id).all()
    if request.method == 'POST':
        if request.form.get('psw1') != request.form.get('psw2'):
            flash('Пароли не совпадают', category='alert-danger')
            return render_template('profile_p/passwordconf.html', title='Подтверждение паролем', items=res[0])
        if not check_password_hash(res[0].psw, request.form.get('psw1')):
            flash('Не правильный пароль', category='alert-danger')
            return render_template('profile_p/passwordconf.html', title='Подтверждение паролем', items=res[0])
        change_id = randint(100, 100000)
        temp_user = TemporaryData.query.filter_by(user_id=session.get('log')['user_id']).all()
        if not temp_user:
            return redirect(url_for('profile_p', user_id=user_id))
        temp_user[0].temp_items = temp_user[0].temp_items + 'change_id:' + str(change_id)
        db.session.commit()
        msg = Message("Подтверждение изменения данных", recipients=[res[0].email])
        msg.html = f'''<h3>Перейдите по ссылке, чтобы подтвердить изменения</h3>
                                                <p><a href="{Config.DOMAIN}/change/{user_id}/{change_id}/">{Config.DOMAIN}/change/{user_id}/{change_id}/</a></p>'''
        mail.send(msg)
        flash(f'Письмо с подтверждением отправлено вам на почту: {res[0].email}', category='alert-success')
    return render_template('profile_p/passwordconf.html', title='Подтверждение паролем', items=res[0])


@profile_b.route('/change/<user_id>/<change_id>/', methods=['post', 'get'])
def change_profile(user_id, change_id):
    """ comment """
    temp_res = TemporaryData.query.filter_by(user_id=user_id).all()[0]
    temp_items = temp_res.temp_items.split(';')[1:]
    for i in range(len(temp_items)):
        temp_items[i] = temp_items[i].split(':')
    if temp_items[-1][-1] == change_id:
        if temp_res.status == 'waiting':
            for i in temp_items[:-1]:
                rows = Users.query.filter_by(user_id=user_id).update({i[0]: i[1]})
                db.session.commit()
            rows = TemporaryData.query.filter_by(user_id=user_id).update({'status': 'success'})
            db.session.commit()
    return redirect(url_for('profile_b.profile_p', user_id=user_id))



