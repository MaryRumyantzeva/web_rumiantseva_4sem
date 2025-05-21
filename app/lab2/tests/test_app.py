import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_url_params(client):
    res = client.get('/url?name=Alice&age=30')
    assert b'Alice' in res.data
    assert b'30' in res.data

def test_headers(client):
    res = client.get('/headers', headers={'Custom-Header': 'TestValue'})
    assert b'TestValue' in res.data

def test_cookies_set_and_delete(client):
    res = client.get('/cookies')
    assert b'my_value' in res.data or b'None' in res.data  # в зависимости от захода

def test_form_post(client):
    res = client.post('/form', data={'key': 'value'})
    assert b'value' in res.data

def test_valid_phone_format(client):
    valid_numbers = ['+7 (123) 456-75-90', '8(123)4567590', '123.456.75.90']
    for number in valid_numbers:
        res = client.post('/phone', data={'phone': number})
        assert b'Отформатированный номер' in res.data

def test_invalid_characters(client):
    res = client.post('/phone', data={'phone': '123abc456'})
    assert b'встречаются недопустимые символы' in res.data

def test_wrong_digit_count(client):
    res = client.post('/phone', data={'phone': '12345'})
    assert b'неверное количество цифр' in res.data
