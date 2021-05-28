import sqlite3
import os
from FDataBase import FDataBase
from flask import Flask, render_template, url_for, request, flash, g, redirect, abort,jsonify, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

account_api = Blueprint('account_api', __name__)





DATABASE = 'db.db'
DEBUG = True
SECRET_KEY = 'euorhgudfv%$%hnjdfv8j6y4723hr'





def connect_db():
    connect = sqlite3.connect(DATABASE)
    connect.row_factory = sqlite3.Row
    return connect


def create_db():
    """Function to create database"""
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


def get_db():
    """Connection with DB"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db





@account_api.route('/login')
def login():
    db = get_db()
    dbase = FDataBase(db)
    if not (dbase.checkUser(request.json.get('email')) and check_password_hash(dbase.retPSW(request.json.get('email')),request.json.get('psw'))) :
        return jsonify({"message": "Не верный логин или пароль"}), 401

    access_token = create_access_token(identity=request.json.get('email'))
    return jsonify(access_token=access_token)
        


@account_api.route('/register', methods=['POST'])
def register():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == 'POST':
        if len(request.json.get('name')) > 3 and len(request.json.get('email')) > 5 \
                and len(request.json.get('psw')) > 3 and request.json.get('psw') == request.json.get('psw2'):
            hash = generate_password_hash(request.json.get('psw'))
            res = dbase.addUser(request.json.get('name'), request.json.get('email'), hash)
            if res:
                return jsonify({"message":"Вы успешно зарегестрировались"})
            elif dbase.checkUser(request.json.get('email')):
                return jsonify({"message":"Введёный Вами email занят"})

            else:
                return jsonify({"message":"У Вас какие-то проблемы. попробуйте ещё раз"})

        elif len(request.json.get('name')) <= 3:
            return jsonify({"message":"Слишком короткое имя"})
        elif len(request.json.get('email')) <= 5:
            return jsonify({"message":"Слишком короткий email"})
        elif len(request.json.get('psw')) <= 3:
            return jsonify({"message":"Слишком короткий пароль"})
        elif request.json.get('psw') == request.json.get('psw2'):
            return jsonify({"message":"Пароли не совпадают"})

    return jsonify({"message":"Что-то пошло не так"})
