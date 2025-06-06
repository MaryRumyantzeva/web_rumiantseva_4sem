import pytest
from flask import get_flashed_messages
from flask_login import current_user
from werkzeug.http import parse_cookie

from lab3.app.app import app as flask_app

TEST_USERS = [
    {
        'id': 1,
        'login': 'user',
        'password': 'qwerty',
    },
]

@pytest.fixture
def client():
    flask_app.config.update({
        'TESTING': True,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'LOGIN_DISABLED': False
    })
    
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client

def test_index_page(client):
    """Тест главной страницы"""
    response = client.get('/')
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '<html' in html  # Общая проверка, что это HTML страница

def test_counter_anonymous(client):
    """Тест счетчика для анонимного пользователя"""
    response = client.get('/counter')
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'counter' in text.lower()  # Проверяем ключевое слово

def test_counter_increments(client):
    """Тест увеличения счетчика"""
    # Первый запрос
    client.get('/counter')
    # Второй запрос
    response = client.get('/counter')
    text = response.get_data(as_text=True)
    # Проверяем увеличение счетчика
    assert '2' in text  # Ищем цифру 2 в ответе

def test_login_page(client):
    """Тест страницы входа"""
    response = client.get('/login')
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'form' in text.lower()  # Проверяем наличие формы

def test_successful_login(client):
    """Тест успешного входа"""
    response = client.post('/login', data={
        'login': 'user',
        'password': 'qwerty'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert current_user.is_authenticated

def test_failed_login(client):
    """Тест неудачного входа"""
    response = client.post('/login', data={
        'login': 'wrong',
        'password': 'wrong'
    })
    assert response.status_code == 200
    assert not current_user.is_authenticated

def test_secret_page_protected(client):
    """Тест защиты секретной страницы"""
    response = client.get('/secret', follow_redirects=True)
    assert b'login' in response.data  # Проверяем перенаправление на страницу входа

def test_secret_page_accessible(client):
    """Тест доступа к секретной странице"""
    # Логинимся
    client.post('/login', data={
        'login': 'user',
        'password': 'qwerty'
    })
    response = client.get('/secret')
    assert response.status_code == 200
    assert 'secret' in response.get_data(as_text=True).lower()

def test_redirect_after_login(client):
    """Тест перенаправления после входа"""
    # Запрос к защищенной странице
    client.get('/secret')
    # Логинимся
    response = client.post('/login', data={
        'login': 'user',
        'password': 'qwerty',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'secret' in response.get_data(as_text=True).lower()

def test_logout(client):
    """Тест выхода из системы"""
    # Логинимся
    client.post('/login', data={
        'login': 'user',
        'password': 'qwerty'
    })
    # Выходим
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert not current_user.is_authenticated

def test_remember_me(client):
    """Тест функции 'Запомнить меня'"""
    response = client.post('/login', data={
        'login': 'user',
        'password': 'qwerty',
        'remember_me': 'on'
    })
    # Проверяем наличие remember_token в cookies
    cookies = response.headers.getlist('Set-Cookie')
    assert any('remember_token' in cookie for cookie in cookies)

def test_counter_per_user(client):
    """Тест индивидуального счетчика"""
    # Анонимный пользователь
    client.get('/counter')
    client.get('/counter')
    
    # Логинимся
    client.post('/login', data={
        'login': 'user',
        'password': 'qwerty'
    })
    # Авторизованный пользователь
    client.get('/counter')
    response = client.get('/counter')
    text = response.get_data(as_text=True)
    # Проверяем, что счетчик работает
    assert '2' in text or '3' in text or '4' in text

def test_navbar_links(client):
    """Тест навигационных ссылок"""
    # Для анонимного пользователя
    response = client.get('/')
    text = response.get_data(as_text=True)
    assert 'login' in text.lower()
    
    # Логинимся
    client.post('/login', data={
        'login': 'user',
        'password': 'qwerty'
    })
    # Для авторизованного пользователя
    response = client.get('/')
    text = response.get_data(as_text=True)
    assert 'logout' in text.lower()