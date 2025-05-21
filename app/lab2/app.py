from flask import Flask, request, render_template, redirect, make_response, url_for
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/url')
def url_params():
    params = request.args
    return render_template('url.html', params=params)

@app.route('/headers')
def headers():
    headers = request.headers
    return render_template('headers.html', headers=headers)


@app.route('/cookie')
def cookie():
    response = render_template('cookie.html')
    test_cookie = request.cookies.get('visited')
    if test_cookie:
        response = app.make_response(render_template('cookie.html', cookie=test_cookie))
        response.set_cookie('visited', '', expires=0)
    else:
        response = app.make_response(render_template('cookie.html', cookie=None))
        response.set_cookie('visited', 'yes')
    return response



@app.route('/form', methods=['GET', 'POST'])
def form_data():
    data = None
    if request.method == 'POST':
        data = request.form
    return render_template('form.html', data=data)



@app.route('/phone', methods=['GET', 'POST'])
def phone():
    error = None
    formatted = None
    raw = ''

    if request.method == 'POST':
        raw = request.form['phone']
        digits = re.sub(r'\D', '', raw)
        allowed = re.match(r'^[\d\s\-\+\(\)\.]+$', raw)

        if not allowed:
            error = 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'
        elif len(digits) not in (10, 11):
            error = 'Недопустимый ввод. Неверное количество цифр.'
        elif len(digits) == 11 and digits.startswith(('8', '7')):
            formatted = f'8-{digits[-10:-7]}-{digits[-7:-4]}-{digits[-4:-2]}-{digits[-2:]}'
        elif len(digits) == 10:
            formatted = f'8-{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}'
        else:
            error = 'Недопустимый ввод. Неверное количество цифр.'

    return render_template('phone.html', error=error, raw=raw, formatted=formatted)