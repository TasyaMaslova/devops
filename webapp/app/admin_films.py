from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import  login_required
from sqlalchemy.exc import SQLAlchemyError
from auth import admin_required
from models import db, Films, Genres, Stills, Users, Comments 
import os
from werkzeug.utils import secure_filename
from uuid import uuid4

user=Users()

bp = Blueprint('admin_films', __name__, url_prefix='/admin_films')

# Загрузка страницы редактирования фильмов 
@bp.route('/edit_films')
@login_required
@admin_required
def edit_films():
    id_film = request.args.get('id_film', 1, type=int)
    film_record = db.get_or_404(Films, id_film)
    genres = db.session.query(Genres).all()
    return render_template("admin_films/edit_films.html", film_record=film_record, genres=genres)

# Страница Администрирование фильмами
@bp.route('/administrate_films')
@login_required
@admin_required
def administrate_films():
    page = request.args.get('page', 1, type=int)
    film_record = db.session.query(Films)
    pagination = db.paginate(film_record, per_page=10, page=page)
    films = pagination.items
    return render_template("admin_films/administrate_films.html", pagination=pagination, films=films)

# Обновление данных фильма (запрос к базе данных)
@bp.route('/update_film/<int:film_id>', methods=['POST'])
@login_required
@admin_required
def update_film(film_id):
    film = db.get_or_404(Films, film_id)

    film.name_film = request.form['nameFilm']
    film.director = request.form['director']
    film.description = request.form['desc_film']
    genre_name = request.form['genre']

    try:
        
        genre = db.session.query(Genres).filter_by(name_genre=genre_name).first()
        film.id_genre = genre.id

        if 'poster' in request.files:
            poster = request.files['poster']
            if poster and poster.filename != '':
                poster_filename = secure_filename(f"{film.uuid_poster}.jpg")
                poster_path = os.path.join(current_app.config['UPLOAD_FOLDER'], poster_filename)
                if os.path.exists(poster_path):
                    os.remove(poster_path)
                poster.save(poster_path)

        stills_files = [('still1', film.stills[0]), ('still2', film.stills[1]), ('still3', film.stills[2])]
        for still_field, still_record in stills_files:
            if still_field in request.files:
                still_file = request.files[still_field]
                if still_file and still_file.filename != '':
                    still_filename = secure_filename(f"{still_record.name_file}.jpg")
                    still_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'stills', still_filename)
                    if os.path.exists(still_path):
                        os.remove(still_path)
                    still_file.save(still_path)

        db.session.commit()
        flash('Фильм успешно обновлен', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Ошибка при обновлении фильма: {str(e)}', 'danger')

    return redirect(url_for('admin_films.edit_films', id_film=film.id))

# Добаление нового фильма (запрос к базе данных)
@bp.route('/add_film', methods=['GET', 'POST'])
@login_required
@admin_required
def add_film():
    genres = db.session.query(Genres).all()
    if request.method == 'POST':
        name_film = request.form['nameFilm']
        director = request.form['director']
        description = request.form['desc_film']
        poster = request.files['poster']
        still1 = request.files['still1']
        still2 = request.files['still2']
        still3 = request.files['still3']
        genre_name = request.form['genre']
        try:
            genre = db.session.query(Genres).filter_by(name_genre=genre_name).first()
            id_genre = genre.id

            if not name_film or not id_genre or not director or not description or not poster or not still1 or not still2 or not still3:
                flash('Все поля должны быть заполнены', 'danger')
            else:
                poster_filename = uuid4().hex

                film = Films(name_film=name_film, director=director, uuid_poster=poster_filename, description=description, id_genre=id_genre)
                db.session.add(film)
                db.session.commit()

                
                poster_path = os.path.join(current_app.config['UPLOAD_FOLDER'], poster_filename + '.jpg')
                poster.save(poster_path)

                still_files = [still1, still2, still3]
                for i, still_file in enumerate(still_files, start=1):
                    if still_file and still_file.filename != '':
                        still_filename = f"{film.id}_{i}"
                        still_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'stills', still_filename + '.jpg')
                        still_file.save(still_path)
                        still_record = Stills(id=str(uuid4()), id_film=film.id, name_file=still_filename)
                        db.session.add(still_record)
                
                db.session.commit()
                flash('Фильм успешно добавлен', 'success')
                return redirect(url_for('admin_films.administrate_films'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Ошибка при добавлении фильма: {str(e)}', 'danger')
            return render_template('admin_films/new_film.html', genres=genres)
    return render_template("admin_films/new_film.html", genres=genres)

# Удаление фильма
@bp.route('/<int:id>/delete_film', methods = ['POST'])
@login_required
@admin_required
def delete_film(id):
    try:
        film_delete = db.session.query(Films).filter_by(id=id).first()

        comments = db.session.query(Comments).filter_by(id_film=id).all()
        for comment in comments:
            db.session.delete(comment)

        for still in film_delete.stills:
            db.session.delete(still)

        db.session.delete(film_delete)
        db.session.commit()

        for still in film_delete.stills:
            still_filename = still.name_file + '.jpg'
            still_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'stills', still_filename)
            if os.path.exists(still_path):
                os.remove(still_path)
        
        poster_filename = film_delete.uuid_poster + '.jpg'
        poster_path = os.path.join(current_app.config['UPLOAD_FOLDER'], poster_filename)
        if os.path.exists(poster_path):
            os.remove(poster_path)

        flash('Выбранный фильм успешно удален', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Произошла ошибка при удалении фильма: {str(e)}', 'danger')
    
    return redirect(url_for('admin_films.administrate_films'))
