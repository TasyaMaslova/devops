from typing import Optional, List
import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask import  current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, MetaData

class Base(DeclarativeBase):
  metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)

class Genres(Base):
   __tablename__ = 'genres'
   id: Mapped[int] = mapped_column(primary_key=True)
   name_genre: Mapped[str] = mapped_column(String(128))

   films: Mapped[list["Films"]] = relationship(back_populates="genre")

class Users(Base,  UserMixin):
   __tablename__ = 'users'
   id: Mapped[int] = mapped_column(primary_key=True)
   name: Mapped[str] = mapped_column(String(128))
   lastname: Mapped[str] = mapped_column(String(128))
   login: Mapped[str] = mapped_column(String(32), unique=True)
   password_hash: Mapped[str] = mapped_column(String(256))
   id_role: Mapped[int] = mapped_column(ForeignKey('roles.id'))

   role: Mapped["Roles"] = relationship(back_populates="users")
   comments: Mapped[list["Comments"]] = relationship(back_populates="user")
   watched_films: Mapped[list["WatchedFilms"]] = relationship(back_populates="user")

   def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        return self.password_hash

   def is_admin(self):
        return self.id_role == current_app.config['ADMIN_ROLE_ID']

   def check_password(self, password):
      return check_password_hash(self.password_hash, password)

class Films(Base):
   __tablename__ = 'films'
   id: Mapped[int] = mapped_column(primary_key=True)
   name_film: Mapped[str] = mapped_column(String(128))
   director: Mapped[str] = mapped_column(String(128))
   uuid_poster: Mapped[str] = mapped_column(String(64))
   description: Mapped[str] = mapped_column(Text())
   id_genre: Mapped[int] = mapped_column(ForeignKey('genres.id'))

   genre: Mapped["Genres"] = relationship(back_populates="films")
   stills: Mapped[list["Stills"]] = relationship(back_populates="film")
   comments: Mapped[list["Comments"]] = relationship(back_populates="film")
   watched_by_users: Mapped[list["WatchedFilms"]] = relationship(back_populates="film")

class WatchedFilms(Base):
   __tablename__ = 'watched_films'
   id: Mapped[int] = mapped_column(primary_key=True)
   id_film: Mapped[int] = mapped_column(ForeignKey('films.id'))
   id_user: Mapped[int] = mapped_column(ForeignKey('users.id'))

   user: Mapped["Users"] = relationship(back_populates="watched_films")
   film: Mapped["Films"] = relationship(back_populates="watched_by_users")

class Comments(Base):
   __tablename__ = 'comments'
   id: Mapped[int] = mapped_column(primary_key=True)
   id_film: Mapped[int] = mapped_column(ForeignKey('films.id'))
   id_user: Mapped[int] = mapped_column(ForeignKey('users.id'))
   text_comment: Mapped[str] = mapped_column(Text())
   id_parent: Mapped[Optional[int]] = mapped_column(ForeignKey('comments.id'))

   user: Mapped["Users"] = relationship(back_populates="comments")
   film: Mapped["Films"] = relationship(back_populates="comments")
   replies: Mapped[List["Comments"]] = relationship("Comments", back_populates="parent", cascade="all, delete-orphan")
   parent: Mapped[Optional["Comments"]] = relationship("Comments", back_populates="replies", remote_side=[id])

class Stills(Base):
   __tablename__ = 'stills'
   id: Mapped[str] = mapped_column(String(64), primary_key=True)
   id_film: Mapped[int] = mapped_column(ForeignKey('films.id'))
   name_file: Mapped[str] = mapped_column(String(128))

   film: Mapped["Films"] = relationship(back_populates="stills")

class Roles(Base):
   __tablename__ = 'roles'
   id: Mapped[int] = mapped_column(primary_key=True)
   name_role: Mapped[int] = mapped_column(String(128))

   users: Mapped[list["Users"]] = relationship(back_populates="role")