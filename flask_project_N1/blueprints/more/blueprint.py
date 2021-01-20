from flask import Blueprint, redirect, render_template, session

from models import Users

moree = Blueprint(
    'moree',
    __name__,
    template_folder='templates',
    static_folder='static'
    )


@moree.route('/<page>/', methods=['post', 'get'])
def index(page):
    """ comment """
    try:
        if not session.get('log')['user_id']:
            return redirect('/welcome/login/0/')
    except:
        return redirect('/welcome/login/0/')
    res = Users.query.filter_by(user_id=session.get('log')['user_id']).all()
    file = ''
    title = ''
    if page == 'groups':
        file = 'groups.html'
        title = 'Группы'
    elif page == 'calendar':
        file = 'calendar.html'
        title = 'Календарь'
    elif page == 'widgets':
        file = 'widgets.html'
        title = 'О нас'
    elif page == 'faqs':
        file = 'faqs.html'
        title = 'Вопросы'
    if file:
        return render_template(f'more/{file}', title=title, items=res[0])
    else:
        return redirect(f"/{session.get('log')['user_id']}/")



