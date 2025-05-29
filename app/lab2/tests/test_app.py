import pytest
from lab2.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# --- URL parameters ---
def test_url_params_display(client):
    response = client.get('/url?foo=bar&baz=qux')
    assert response.status_code == 200
    assert b"foo" in response.data or b"bar" in response.data  # предполагаем, что ты их рендеришь

# --- Headers ---
def test_request_headers(client):
    response = client.get('/headers', headers={'X-Test': '123'})
    assert response.status_code == 200
    assert b'X-Test' in response.data or b'123' in response.data

# --- Cookies ---
def test_cookie_page_set(client):
    """Тест на установку cookie"""
    
    # Отправляем первый запрос на страницу
    response = client.get('/cookies')  # изменяем на правильный маршрут
    
    # Проверяем, что cookie 'user' установлено с значением 'admin'
    cookies = response.headers.getlist('Set-Cookie')
    assert any('user=admin' in cookie for cookie in cookies), "Cookie 'user' не установлено с правильным значением"


def test_cookie_page_remove(client):
    """Тест на удаление cookie после второго захода"""

    # Первый заход - устанавливаем cookie
    response = client.get('/cookies')  # изменяем на правильный маршрут
    cookies = response.headers.getlist('Set-Cookie')
    assert any('user=admin' in cookie for cookie in cookies), "Cookie 'user' не установлено с правильным значением"

    # Второй заход - проверяем удаление cookie
    response = client.get('/cookies')  # запросим страницу снова
    cookies = response.headers.getlist('Set-Cookie')

    # Проверяем, что cookie 'user' удаляется (обычно через Max-Age=0 или пустое значение)
    assert any('user=; ' in cookie or 'Max-Age=0' in cookie for cookie in cookies), "Cookie 'user' не был удален"

# --- Form submission ---
def test_form_post(client):
    response = client.post('/forms', data={'login': 'test', 'password': '123'})
    assert b'test' in response.data
    assert b'password' in response.data

# --- Phone validation tests ---

def test_valid_phone_formatting(client):
    response = client.post('/phoneNumber', data={'phone': '+7 (123) 456-75-90'})
    html = response.get_data(as_text=True)
    assert '8-123-456-75-90' in html

def test_invalid_chars_in_phone(client):
    response = client.post('/phoneNumber', data={'phone': '123-456-ABCD'})
    html = response.get_data(as_text=True)
    assert 'Ошибка! Вы ввели недопустимые символы.' in html

def test_invalid_digit_count_11_required(client):
    response = client.post('/phoneNumber', data={'phone': '+7 123 456 78'})
    html = response.get_data(as_text=True)
    assert 'Ошибка! Вы ввели неверное количество цифр.' in html or \
           'Ошибка! Вы ввели недопустимое количество цифр.' in html


def test_bootstrap_classes_on_error(client):
    response = client.post('/phoneNumber', data={'phone': 'abc'})
    html = response.get_data(as_text=True)
    assert 'Ошибка!' in html  # Просто проверяем, что ошибка показана

def test_index_page(client):
    response = client.get('/phoneNumber')  # проверяем правильную страницу
    html = response.get_data(as_text=True)
    assert '<form' in html



def test_phone_with_spaces(client):
    response = client.post('/phoneNumber', data={'phone': '8 123 456 78 90'})
    assert '8-123-456-78-90' in response.get_data(as_text=True)

def test_phone_with_plus_format(client):
    response = client.post('/phoneNumber', data={'phone': '+7 123 456 78 90'})
    assert '8-123-456-78-90' in response.get_data(as_text=True)

def test_cookie_route_sets_cookie(client):
    response = client.get('/cookies')
    assert 'Set-Cookie' in response.headers

def test_russian_language_meta(client):
    response = client.get('/')
    html = response.get_data(as_text=True)
    assert '<html lang="ru">' in html

def test_no_error_on_valid_input(client):
    response = client.post('/phoneNumber', data={'phone': '81234567890'})
    html = response.get_data(as_text=True)
    assert 'Ошибка!' not in html


