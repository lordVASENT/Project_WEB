from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3
import uuid

app = Flask(__name__)
app.secret_key = 'secret_key'


def init_db():
    conn = sqlite3.connect('members.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS MEMBERS (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        PERSONAL_CODE TEXT,
        NAME TEXT,
        SURNAME TEXT,
        EMAIL TEXT UNIQUE,
        PASSWORD TEXT,
        PHONE TEXT,
        STATUS_ENTERING TEXT,
        BUYING TEXT
    )''')
    conn.commit()
    conn.close()


init_db()


home_page = '''
<h1>Добро пожаловать на мероприятие!</h1>
<p>Информация о событии...</p>
<a href="/register">Регистрация</a> | <a href="/login">Вход</a>
'''


register_form = '''
<h2>Регистрация</h2>
<form method="post">
    Имя: <input name="name"><br>
    Фамилия: <input name="surname"><br>
    Email: <input name="email"><br>
    Пароль: <input name="password" type="password"><br>
    Телефон: <input name="phone"><br>
    Статус: <select name="status"><option>СПИКЕР</option><option>УЧАСТНИК</option></select><br>
    <input type="submit" value="Зарегистрироваться">
</form>
'''

login_form = '''
<h2>Вход</h2>
<form method="post">
    Email: <input name="email"><br>
    Пароль: <input name="password" type="password"><br>
    <input type="submit" value="Войти">
</form>
'''

cabinet_template = '''
<h2>Личный кабинет</h2>
<p>Добро пожаловать, {{ name }} {{ surname }} ({{ status }})</p>
<ul>
    <li><a href="/note">1. Оставить текст для выступления</a></li>
    <li><a href="/badge">2. Получить электронный бейдж</a></li>
    <li><a href="/access">3. Получить код доступа</a></li>
    <li><a href="/shop">4. Заказать товары</a></li>
</ul>
<a href="/logout">Выйти</a>
'''


@app.route('/')
def home():
    return home_page


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = sqlite3.connect('members.db')
        c = conn.cursor()
        try:
            personal_code = str(uuid.uuid4())
            c.execute(
                'INSERT INTO MEMBERS (PERSONAL_CODE, NAME, SURNAME, EMAIL, PASSWORD, PHONE, STATUS_ENTERING) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (
                    personal_code,
                    request.form['name'],
                    request.form['surname'],
                    request.form['email'],
                    request.form['password'],
                    request.form['phone'],
                    request.form['status']
                ))
            conn.commit()
            return redirect('/login')
        except sqlite3.IntegrityError:
            return "Пользователь с такой почтой уже существует."
        finally:
            conn.close()
    return register_form


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = sqlite3.connect('members.db')
        c = conn.cursor()
        c.execute('SELECT * FROM MEMBERS WHERE EMAIL=? AND PASSWORD=?',
                  (request.form['email'], request.form['password']))
        user = c.fetchone()
        conn.close()
        if user:
            session['user'] = {
                'id': user[0],
                'name': user[2],
                'surname': user[3],
                'email': user[4],
                'status': user[7],
                'code': user[1]
            }
            return redirect('/cabinet')
        return "Неверный логин или пароль."
    return login_form


@app.route('/cabinet')
def cabinet():
    if 'user' not in session:
        return redirect('/login')
    return render_template_string(cabinet_template, **session['user'])


@app.route('/note', methods=['GET', 'POST'])
def note():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        return f'''
            Текст сохранён: {request.form['note']}<br><br>
            <a href="/cabinet">Вернуться в кабинет</a>
        '''
    return '''
        <form method="post">
            Ваш текст:<br>
            <textarea name="note"></textarea><br>
            <input type="submit" value="Сохранить">
        </form>
<br>
        <a href="/cabinet">Вернуться в кабинет</a>
    '''


PRODUCTS = [
    "Футболка", "Кепка", "Блокнот", "Ручка", "Сумка", "Значок", "Браслет", "Наклейки",
    "Флешка", "Кружка", "Папка", "Магнит", "Шарф", "Плед", "Термокружка", "Зонт",
    "Фонарик", "Бутылка", "Брелок", "Ежедневник"]


@app.route('/shop', methods=['GET', 'POST'])
def shop():
    if 'user' not in session:
        return redirect('/login')

    user_id = session['user']['id']

    if 'selected_items' not in session:
        # При первом посещении — загрузить из БД, если есть
        conn = sqlite3.connect('members.db')
        c = conn.cursor()
        c.execute('SELECT BUYING FROM MEMBERS WHERE ID=?', (user_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            session['selected_items'] = row[0].split(', ')
        else:
            session['selected_items'] = []

    if request.method == 'POST':
        selected = request.form.getlist('items')
        session['selected_items'] = selected

        # Обновить БД
        conn = sqlite3.connect('members.db')
        c = conn.cursor()
        c.execute('UPDATE MEMBERS SET BUYING=? WHERE ID=?', (', '.join(selected), user_id))
        conn.commit()
        conn.close()

        return '''
            Заказ сохранён. Оплата на месте.<br><br>
            <a href="/cabinet">Вернуться в кабинет</a>
        '''

    # Формируем HTML-список с чекбоксами
    checkboxes = ""
    for item in PRODUCTS:
        checked = "checked" if item in session['selected_items'] else ""
        checkboxes += f'<input type="checkbox" name="items" value="{item}" {checked}> {item}<br>'

    return f'''
        <h3>Выберите товары:</h3>
        <form method="post">
            {checkboxes}
            <br><input type="submit" value="Сохранить выбор">
        </form>
        <br>
        <a href="/cabinet">Вернуться в кабинет</a>
    '''


@app.route('/badge')
def badge():
    if 'user' not in session:
        return redirect('/login')
    return f'''
        <h3>Электронный бейдж</h3>
        {session['user']['name']} {session['user']['surname']}<br>
        Статус: {session['user']['status']}<br><br>
        <a href="/cabinet">Вернуться в кабинет</a>
    '''


@app.route('/access')
def access():
    if 'user' not in session:
        return redirect('/login')
    return f'''
        <h3>Ваш персональный код доступа</h3>
        {session['user']['code']}<br><br>
        <a href="/cabinet">Вернуться в кабинет</a>
    '''


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
