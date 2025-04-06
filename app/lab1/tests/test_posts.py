import sys
import os

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# # sys.path.append('..')

import pytest
from lab1.app import app, posts_list
from flask import url_for

@pytest.fixture
def client():
    with app.test_client() as client:
        with app.app_context():
            yield client

@pytest.fixture
def sample_post():
    return posts_list[0]

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!doctype html>' in response.data
    assert 'Задание к лабораторной работе' in response.data.decode('utf-8')

def test_post_template_used(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    assert response.status_code == 200
    assert b'<h1 class="text-center">' in response.data

def test_post_title_rendered(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    assert sample_post["title"] in response.data.decode()

def test_post_author_displayed(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    assert sample_post["author"] in response.data.decode()

def test_post_text_displayed(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    assert sample_post["text"] in response.data.decode()

def test_post_date_format(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    date_str = sample_post["date"].strftime('%d.%m.%Y')
    assert date_str in response.data.decode()

def test_post_image_displayed(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    assert sample_post["image_id"] in response.data.decode()

def test_comment_form_present(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    assert 'Оставьте комментарий' in response.data.decode()
    assert '<textarea' in response.data.decode()

def test_comments_rendered(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    for comment in sample_post["comments"]:
        assert comment["author"] in response.data.decode()
        assert comment["text"] in response.data.decode()

def test_comment_replies_rendered(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    for comment in sample_post["comments"]:
        if "replies" in comment:
            for reply in comment["replies"]:
                assert reply["author"] in response.data.decode()
                assert reply["text"] in response.data.decode()

def test_404_for_missing_post(client):
    response = client.get('/posts/9999')  
    assert response.status_code == 404

def test_footer_present(client):
    response = client.get('/')
    assert 'ФИО' in response.data.decode() or 'группа' in response.data.decode()

def test_response_is_html(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    assert response.content_type == 'text/html; charset=utf-8'

def test_post_page_not_empty(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    assert len(response.data) > 100  

def test_no_500_error(client, sample_post):
    response = client.get(f'/posts/{sample_post["id"]}')
    assert response.status_code != 500
