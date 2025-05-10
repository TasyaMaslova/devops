import os
import pytest
from app.app import create_app
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, render_template, request, redirect, url_for
from extensions import db
from app.models import Users, WatchedFilms, Genres, Films, Stills
db.Model.metadata.clear()


@pytest.fixture
def client():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'SECRET_KEY': b'afd41e94b269e053cc3f6d065a717cffde51ee5208928463ce897faed531006b',
    'ADMIN_ROLE_ID': 1,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'UPLOAD_FOLDER': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
    })
    with app.app_context():
        db.metadata.clear()
        db.create_all()

        admin_user = Users(
            id=8,
            name="admin",
            lastname="user",
            login="admin_user",
            password_hash=generate_password_hash("admin_pass"),
            id_role=1  
        )
        db.session.add(admin_user)
         # Создаем тестовые данные
        genre1 = Genres(id=1, name_genre="drama")
        genre2 = Genres(id=2, name_genre="fantastica")
        film1 = Films(
            id=1,
            name_film="test Film",
            director="test Director",
            uuid_poster="test_uuid",
            description="test Description",
            id_genre=1
        )
        film2 = Films(
            id=2,
            name_film="test Film2",
            director="test Director2",
            uuid_poster="test_uuid2",
            description="test Description2",
            id_genre=2
        )
        db.session.add_all([genre1, genre2, film1, film2])
        #Создаем тестовые просмотренные фильмы
        films1 = WatchedFilms(id_film=1, id_user=8)
        films2 = WatchedFilms(id_film=2, id_user=8)
        db.session.add_all([films1, films2])

        # Создаем и добавляем кадры для фильма 1
        still1 = Stills(id='s1', id_film=1, name_file='still1')
        still2 = Stills(id='s2', id_film=1, name_file='still2')
        still3 = Stills(id='s3', id_film=1, name_file='still3')

        still4 = Stills(id='s4', id_film=2, name_file='still4')

        db.session.add_all([still1, still2, still3, still4])
        db.session.commit()


    with app.test_client() as client:
        # Войти под пользователем
        client.post('/auth/login', data={
            'login': 'admin_user',
            'password': 'admin_pass'
        }, follow_redirects=True)
        yield client

    # Очистка базы
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client2():
    app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'SECRET_KEY': b'afd41e94b269e053cc3f6d065a717cffde51ee5208928463ce897faed531006b',
    'ADMIN_ROLE_ID': 1,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_ECHO': True,
    'UPLOAD_FOLDER': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')
    })
    with app.app_context():
        db.metadata.clear()
        db.create_all()
        
        yield app.test_client()
        db.session.remove()
        db.drop_all()


# 1        
def test_edit_films_admin_access(client):
    """Тест доступа для администратора"""
    client.post('/auth/login', data={
        'login': 'admin_user',
        'password': 'admin_pass'
    }, follow_redirects=True)
    response = client.get('/admin_films/edit_films?id_film=1')
   
   
    assert response.status_code == 200
    assert b"test Film" in response.data
    assert b"drama" in response.data

# 2
def test_edit_password_mismatch(client):
    """Тест с несовпадающими новыми паролями"""
    response = client.post('/users/edit_password', data={
        'old_password': 'admin_pass',
        'new_password': 'new_secure_password',
        'password_repeat': 'different_password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    print(response.data.decode('utf-8'))
    assert "Новый пароль и его подтверждение не совпадают." in response.data.decode('utf-8')

# 3
def test_edit_password_wrong_old(client):
    """Тест с неверным старым паролем"""
    response = client.post('/users/edit_password', data={
        'old_password': 'wrong_admin_pass',
        'new_password': 'new_secure_password',
        'password_repeat': 'new_secure_password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert "Неверный старый пароль." in response.data.decode('utf-8')

# 4
def test_edit_password_success(client):
    """Тест успешного изменения пароля"""
    response = client.post('/users/edit_password', data={
        'old_password': 'admin_pass',
        'new_password': 'new_secure_password',
        'password_repeat': 'new_secure_password'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert "Данные успешно обновлены." in response.data.decode('utf-8')

    # Проверяем что пароль изменился
    with client.application.app_context():
        user = db.session.get(Users, 8)
        assert user.check_password("new_secure_password")

# 5
def test_edit_password_unauthorized(client2):
    """Тест доступа к странице изменения пароля для неавторизованного пользователя"""
    response = client2.get('/users/edit_password', follow_redirects=True)
    assert response.status_code == 200
    assert "/auth/login" in response.request.path
    assert "Для доступа к данной странице необходимо пройти процедуру аутентификации." in response.data.decode('utf-8')

# 6
def test_edit_password_page_authorized(client):
    """Тест доступа к странице изменения пароля для авторизованного пользователя"""
    response = client.get('/users/edit_password', follow_redirects=True)
    assert response.status_code == 200
    assert "/users/edit_password" in response.request.path

# 7
def test_edit_user_success(client):
    """Тест успешного обновления данных пользователя"""
    response = client.post('/users/edit_user', data={
        'login': 'new_login',
        'name': 'new_name',
        'lastname': 'new_lastname'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "Данные успешно обновлены." in response.data.decode('utf-8')
    
    updated_user = db.session.get(Users, 8)
    assert updated_user.login == 'new_login'
    assert updated_user.name == 'new_name'
    assert updated_user.lastname == 'new_lastname'

# 8
def test_edit_user_unauthorized(client2):
    """Тест попытки доступа неавторизованного пользователя"""
    response = client2.get('/users/edit_user', follow_redirects=True)

    assert response.status_code == 200
    assert "/auth/login" in response.request.path
    assert "Для доступа к данной странице необходимо пройти процедуру аутентификации." in response.data.decode('utf-8')

# 9
def test_edit_user_page_authorized(client):
    """Тест доступа к странице редактирования для авторизованного пользователя"""        
    response = client.get('/users/edit_user', follow_redirects=True)
    assert response.status_code == 200
    assert "edit_user" in response.request.path

# 10
def test_personal_account_watched_films(client):
    """Тест получения списка просмотренных фильмов"""
    login_response = client.post('/auth/login', data={
        'login': 'existing_user',
        'password': 'supermegasecretpass123'
    }, follow_redirects=True)
    assert login_response.status_code == 200
    response = client.get('/users/personal_account', follow_redirects=True)
    
    assert response.status_code == 200
    assert b"test Film" in response.data  
    assert b"test Film2" in response.data  
    
    # Проверяем данные в БД
    films = db.session.scalars(db.select(WatchedFilms).where(WatchedFilms.id_user == 8)).all()
    assert len(films) == 2
    assert films[0].id_film == 1
    assert films[1].id_film == 2

# 11
def test_personal_account_unauthorized_access(client2):
    """Тест попытки доступа неавторизованного пользователя к личному кабинету"""
    response = client2.get('/users/personal_account', follow_redirects=True)
    
    assert response.status_code == 200
    assert "/auth/login" in response.request.path
    assert "Для доступа к данной странице необходимо пройти процедуру аутентификации." in response.data.decode('utf-8')

# 12
def test_personal_account_authorized_access(client):
    """Тест доступа к личному кабинету авторизованного пользователя"""   
    response = client.get('/users/personal_account', follow_redirects=True)
        
    assert response.status_code == 200
    assert "personal_account" in response.request.path

# 13
def test_registration_existing_login(client):
    """Тест регистрации с существующим логином"""
    response = client.post('/auth/reg', data={
        'name': 'test',
        'lastname': 'user',
        'login': 'admin_user',
        'password': 'supermegasecretpass123',
        'password_repeat': 'supermegasecretpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert "Пользователь с таким логином уже существует." in response.data.decode('utf-8')

# 14
def test_registration_passwords_mismatch(client2):
    """Тест несовпадения паролей при регистрации"""
    response = client2.post('/auth/reg', data={
        'name': 'test',
        'lastname': 'user',
        'login': 'new_user',
        'password': 'supermegasecretpass123',
        'password_repeat': 'differentpass'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert "Пароли не совпадают." in response.data.decode('utf-8')

# 15
def test_registration_success(client2):
    """Тест успешной регистрации"""
    response = client2.post('/auth/reg', data={
        'name': 'test',
        'lastname': 'user',
        'login': 'new_user',
        'password': 'supermegasecretpass123',
        'password_repeat': 'supermegasecretpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert "Вы успешно зарегистрировались." in response.data.decode('utf-8')
    assert response.request.path == '/' 

    # Проверяем что пользователь действительно создан
    with client2.application.app_context():
        user = db.session.scalars(db.select(Users).where(Users.login =='new_user')).first()
        assert user is not None
        assert user.name == 'test'
        assert user.lastname == 'user'
        assert user.id_role == 2 

# 16
def test_registration_get_request(client):
    """Тест GET-запроса на страницу регистрации"""
    response = client.get('/auth/reg')
    assert response.status_code == 200

# 17
def test_auth_valid(client):
    response = client.post('/auth/login',  data={'login': 'admin_user', 'password': 'admin_pass' },
                            follow_redirects=True)
    assert response.status_code == 200  
    assert "Вы успешно аутентифицированы." in response.data.decode('utf-8')

# 18
def test_auth_page_accessible(client2):
    response = client2.get('/auth/login', follow_redirects=True)
    assert response.status_code == 200  

# 19
def test_auth_invalid(client):
    response = client.post('/auth/login',  data={'login': 'fail_user', 'password': 'fail_pass' },
                            follow_redirects=True)
    assert response.status_code == 200
    assert "Введены неверные логин и/или пароль" in response.data.decode('utf-8')
    
# 20
def test_logout(client):
    client.post('/auth/login', 
               data={'login': 'admin_user', 'password': 'admin_pass'},
               follow_redirects=True)
    response = client.get('auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert response.request.path == '/'  
    

