from flask import Flask, request, render_template, redirect, make_response, url_for
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/url')
def url_params():
    return render_template('url_params.html', params=request.args)

@app.route('/headers')
def headers():
    return render_template('headers.html', headers=request.headers)

@app.route('/cookies')
def cookies():
    cookie_name = 'example_cookie'
    resp = make_response(render_template('cookies.html', cookie=request.cookies.get(cookie_name)))
    if cookie_name in request.cookies:
        resp.set_cookie(cookie_name, '', max_age=0)  # Удаление cookie
    else:
        resp.set_cookie(cookie_name, 'my_value')     # Установка cookie
    return resp

@app.route('/form', methods=['GET', 'POST'])
def form_params():
    if request.method == 'POST':
        return render_template('form_params.html', form_data=request.form)
    return render_template('form_params.html')

@app.route('/phone', methods=['GET', 'POST'])
def phone():
    error = None
    phone_number = ""
    formatted_number = ""

    if request.method == 'POST':
        phone_number = request.form.get('phone', '').strip()
        digits = re.sub(r'\D', '', phone_number)

        if not re.match(r'^[\d\s\-\.\(\)\+]*$', phone_number):
            error = 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'
        elif not (len(digits) == 10 or (len(digits) == 11 and (digits.startswith('8') or digits.startswith('7')))):
            error = 'Недопустимый ввод. Неверное количество цифр.'
        else:
            if len(digits) == 11:
                digits = digits[-10:]
            formatted_number = f"8-{digits[0:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}"

    return render_template('phone_form.html',
                           error=error,
                           original_input=phone_number,
                           formatted=formatted_number)
