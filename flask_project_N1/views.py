import datetime

from flask import request, render_template, url_for, redirect, session

from main import app, db
from models import Users


@app.route('/')
def index():
    return redirect('/main/')


@app.route('/confirmation/<user_id>/', methods=['POST', 'GET'])
def confirmation(user_id):
    res = Users.query.filter_by(user_id=user_id).all()
    if res:
        if res[0].status_reg == 'waiting':
            rows = Users.query.filter_by(user_id=user_id).update({'status_reg': 'success'})
            db.session.commit()
        session['log'] = {'login': True, 'user_id': user_id}
        return redirect(url_for('main'))
    return redirect('/welcome/login/0/')


@app.route('/rates/', methods=['POST', 'GET'])
def start_buy():
    try:
        ses = session.get('log')
    except:
        return redirect('/welcome/login/0/')
    if request.method == 'POST':
        trial = ''
        trial_end = ''
        rate_name = ''
        if request.form.get('trial'):
            trial = datetime.datetime.today()
            trial = trial.strftime("%Y-%m-%d-%H.%M.%S")
            trial_end = trial.split('-')
            trial_end[2] = str(int(trial_end[2]) + 5)
            trial_end = '-'.join(trial_end)
            rate_name = 'trial'
        tr = Users.query.filter_by(user_id=session.get('log')['user_id']).update({'rate_start': trial,
                                                                                  'rate_end': trial_end,
                                                                                  'rate_name': rate_name})
        db.session.commit()
        return redirect(f'/in/{session.get("log")["user_id"]}/')
    res = Users.query.filter_by(user_id=session.get('log')['user_id']).all()
    return render_template('start_buy.html', title='Тарифы', items=res[0])


@app.route('/main/', methods=['POST', 'GET'])
def main():
    return render_template('start.html', title='Лендинг')