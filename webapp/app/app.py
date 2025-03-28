
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import current_user, login_required
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from models import db, Films, Genres,Comments, WatchedFilms, Users 
from auth import bp as auth_bp, init_login_manager
from admin_films import bp as admin_films_bp
from users import bp as users_bp
import os
from zipfile import ZipFile


from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
application = app
app.config.from_pyfile('config.py')

db.init_app(app)
migrate = Migrate(app, db)

init_login_manager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(admin_films_bp)
app.register_blueprint(users_bp)

# Загрузка главной страницы с фильмами
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    name_genre = request.args.get('name_genre', '')
    genres = db.session.query(Genres).all()
    query = db.session.query(Films)
    if name_genre:
        query = query.join(Films.genre).filter(Genres.name_genre == name_genre)
    pagination = db.paginate(query, per_page=12, page=page)
    films = pagination.items
    return render_template("index.html", films=films, genres=genres, pagination=pagination, name_genre=name_genre)

# Загрузка страницы с выбранным фильмом
@app.route('/watch_film')
def watch_film():
    id_film = request.args.get('id', type=int)
    film_record = db.get_or_404(Films, id_film)
    return render_template("watch_film.html", film_record=film_record)

# Определение endpoint media
@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory('media', filename)

# Добавление комментария
@app.route('/add_comment/<int:id_film>', methods=['POST'])
@login_required
def add_comment(id_film):
    try:
        text_comment = request.form['comment']
        id_parent = request.form.get('id_parent')
        if id_parent is not None and id_parent.isdigit():
            id_parent = int(id_parent)
        else:
            id_parent = None
        comment = Comments(id_user=current_user.id, id_film=id_film, text_comment=text_comment, id_parent=id_parent)
        db.session.add(comment)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Ошибка при добавлении комментария: {str(e)}', 'danger')
        return render_template('watch_film', id=id_film)

    return redirect(url_for('watch_film', id=id_film))

# Загрузка кадров фильма
@app.route('/download_stills/<int:id_film>', methods=['GET', 'POST'])
def download_stills(id_film):
    film_record = db.get_or_404(Films, id_film)
    stills_directory = os.path.join(app.config['UPLOAD_FOLDER'], 'stills')
    
    # Создание архива с кадрами
    zip_filename = f'stills_{film_record.id}.zip'
    with ZipFile(zip_filename, 'w') as zip:
        for still in film_record.stills:
            still_path = os.path.join(stills_directory, still.name_file + '.jpg')
            zip.write(still_path, os.path.basename(still_path))

    return send_from_directory(directory='.', path=zip_filename, as_attachment=True)

# Добавление записи в таблицу watch_films при нажатии на кнопку "Буду смотреть"
@app.route('/add_to_watchlist/<int:id_film>', methods=['POST'])
@login_required
def add_to_watchlist(id_film):
    try:
        
        watched_film = db.session.query(WatchedFilms).filter_by(id_film=id_film, id_user=current_user.id).first()
        if watched_film:
            flash('Вы уже добавили этот фильм в список "Буду смотреть".', 'warning')
        else:
            new_watched_film = WatchedFilms(id_film=id_film, id_user=current_user.id)
            db.session.add(new_watched_film)
            db.session.commit()
            flash('Фильм добавлен в список "Буду смотреть".' , 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Ошибка при добавлении фильма в список "Буду смотреть": {str(e)}', 'danger')
        return render_template('watch_film', id=id_film)
    
    return redirect(url_for('watch_film', id=id_film))