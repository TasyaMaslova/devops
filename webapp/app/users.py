from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import  login_required, current_user
from sqlalchemy.exc import SQLAlchemyError
from auth import admin_required
from models import db, Films, Genres, Stills, Users, Comments, WatchedFilms 
import os
from werkzeug.utils import secure_filename
from uuid import uuid4

user=Users()

bp = Blueprint('users', __name__, url_prefix='/users')

# Личный кабинет
@bp.route('/personal_account')
@login_required
def personal_account():
    id_user = current_user.id
    user_record = db.get_or_404(Users, id_user)
    film_record = film_record = db.session.query(WatchedFilms).filter(WatchedFilms.id_user == id_user).all()

    return render_template("users/personal_account.html", user_record=user_record, film_record=film_record)

# Удаление фильма из отложенных в личном кабинете
@bp.route('/watch_film/<int:id>/delete_watch_film', methods = ['POST'])
@login_required
def delete_film(id):
    try:
        watch_film_delete = db.session.query(WatchedFilms).filter_by(id=id).first()
        db.session.delete(watch_film_delete)
        db.session.commit()
        flash('Выбранный фильм успешно удален', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Произошла ошибка при удалении фильма: {str(e)}', 'danger')
        return render_template('users/personal_account.html')
    
    return redirect(url_for('users.personal_account'))

# Страница редактирования данных пользователя
@bp.route('/edit_user', methods=['GET', 'POST'])
@login_required
def edit_user():
    user_record = db.session.query(Users).filter_by(id=current_user.id).first()
    if request.method == 'POST':
        try:
            login = request.form['login']
            name = request.form['name']
            lastname = request.form['lastname']

            user_record.login = login
            user_record.name = name
            user_record.lastname = lastname
            db.session.commit()

            flash('Данные успешно обновлены.', 'success')
            return redirect(url_for('users.edit_user'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Произошла ошибка при удалении фильма: {str(e)}', 'danger')
            return render_template("users/edit_user.html", user_record=user_record)
    return render_template("users/edit_user.html", user_record=user_record)

# Страница изменения пароля пользователя
@bp.route('/edit_password', methods=['GET', 'POST'])
@login_required
def edit_password():
    user_record = db.session.query(Users).filter_by(id=current_user.id).first()
    if request.method == 'POST':
        try:
            old_password = request.form.get('old_password')
            new_password = request.form.get('new_password')
            password_repeat = request.form.get('password_repeat')

            if not user_record.check_password(old_password):
                flash('Неверный старый пароль.', 'danger')
            elif new_password != password_repeat:
                flash('Новый пароль и его подтверждение не совпадают.', 'danger')
            else:
                user_record.set_password(new_password)
                db.session.commit()
                flash('Данные успешно обновлены.', 'success')
                return redirect(url_for('users.personal_account'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Произошла ошибка при удалении фильма: {str(e)}', 'danger')
            return render_template("users/edit_password.html", user_record=user_record)
    return render_template("users/edit_password.html")