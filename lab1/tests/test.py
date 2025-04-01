import pytest
from flask import url_for
from app import create_app

def test_post_template_used(client, sample_post):
    response = client.get(url_for('post', post_id=sample_post.id))
    assert b"<h1 class=\"text-center\">" in response.data

def test_post_data_rendered(client, sample_post):
    response = client.get(url_for('post', post_id=sample_post.id))
    assert sample_post.title.encode() in response.data
    assert sample_post.author.encode() in response.data
    assert sample_post.text.encode() in response.data

def test_post_date_format(client, sample_post):
    response = client.get(url_for('post', post_id=sample_post.id))
    assert sample_post.date.strftime("%d.%m.%Y").encode() in response.data

def test_post_image_rendered(client, sample_post):
    response = client.get(url_for('post', post_id=sample_post.id))
    assert f'src="{url_for("static", filename="images/" + sample_post.image_id)}"'.encode() in response.data

# def test_comment_section_rendered(client, sample_post):
#     response = client.get(url_for('post', post_id=sample_post.id))
#     assert b"Оставьте комментарий" in response.data

def test_comments_rendered(client, sample_post):
    for comment in sample_post.comments:
        assert comment.author.encode() in response.data
        assert comment.text.encode() in response.data

def test_replies_rendered(client, sample_post):
    for comment in sample_post.comments:
        for reply in comment.replies:
            assert reply.author.encode() in response.data
            assert reply.text.encode() in response.data

def test_non_existent_post(client):
    response = client.get(url_for('post', post_id=9999))
    assert response.status_code == 404

# def test_footer_rendered(client):
#     response = client.get(url_for('index'))
#     assert b"Румянцева Мария Игоревна" in response.data  # Замените на реальное ФИО
#     assert b"231-329" in response.data  # Замените на реальный номер группы

def test_correct_templates_used(client):
    response = client.get(url_for('index'))
    assert b"base.html" in response.data
    response = client.get(url_for('post', post_id=1))
    assert b"post.html" in response.data