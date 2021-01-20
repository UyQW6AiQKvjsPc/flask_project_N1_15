from random import randint

from flask import Blueprint, request, redirect, url_for, flash, render_template, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message

from re_handlers import Handlers
from models import Users, TemporaryData
from main import app, db, mail

log_reg = Blueprint(
    'log_reg',
    __name__,
    template_folder='templates',
    static_folder='static'
    )


@log_reg.route(r'/login/<int:id>/', methods=['get', 'post'])
def login_b(id):
    """ comment """
    check = Handlers()
    if request.method == 'POST':
        if request.form.get('log_in'):
            res = Users.query.filter_by(login=request.form.get('username')).all()
            if not res:
                flash('Неверный логин', category='alert-danger')
                return render_template('log_reg/login.html', title='Добро пожаловать')
            if not check_password_hash(res[0].psw, request.form.get('password')):
                flash('Неверный пароль', category='alert-danger')
                return render_template('log_reg/login.html', title='Авторизация')
            session['log'] = {'login': True, 'user_id': res[0].user_id}
            return redirect(f'/rates/')
        elif request.form.get('log_up'):
            login = check.re_login(request.form.get('login'))
            if login:
                if len(login) == 2:
                    if login[1] == 'error_len':
                        flash('Минимальная длина логина - 10 симфолов', category='alert-danger')
                    else:
                        flash('Не используйте кириллицу и пробельные символы в логине', category='alert-danger')
                    return render_template('log_reg/login.html', title='Добро пожаловать')
            phone = check.re_number(request.form.get('phone'))
            if not phone:
                flash('Введите ваш номер корректно', category='alert-danger')
                return render_template('log_reg/login.html', title='Добро пожаловать')
            if request.form.get('passwordsignin') != request.form.get('confirmpassword'):
                flash('Пароли не совпадают', category='alert-danger')
                return render_template('log_reg/login.html', title='Добро пожаловать')
            psw = check.re_psw(request.form.get('passwordsignin'))
            if psw:
                if len(psw) == 2:
                    if psw[1] == 'error_len':
                        flash('Минимальная длина логина - 12 симфолов', category='alert-danger')
                    else:
                        flash('Не используйте кириллицу и пробельные символы в пароле', category='alert-danger')
                    return render_template('log_reg/login.html', title='Добро пожаловать')
            random_n = f'{randint(100, 10000000)}-{randint(1, 1000)}'
            if not request.form.get('agree'):
                flash('Прежде чем зарестирироваться, вам нужно согласиться с нашими правилами', category='alert-danger')
                return render_template('log_reg/login.html', title='Добро пожаловать')
            users = Users(login=login[0], email=request.form.get('email'), psw=generate_password_hash(psw[0]), phone=phone[0],
                          status_reg='waiting', user_id=random_n)
            temp_user = TemporaryData(users=users)
            db.session.add(users)
            try:
                db.session.commit()
            except:
                flash('Такой логин и/или почта и/или номер уже используются', category='alert-danger')
                return render_template('log_reg/login.html', title='Регистрация')
            msg = Message("Подтверждение регистрации", recipients=[request.form.get('email')])
            msg.html = f'<h1>Перейдите по ссылке, чтобы подтвердить регистрацию</h1><p><a href="Полный путь/confirmation/{random_n}/">Полный путь/confirmation/{random_n}/</a></p>'
            mail.send(msg)
            flash('Письмо с подтверждением отправлено вам на почту', category='alert-success')
    return render_template('log_reg/login.html', title='Добро пожаловать')
