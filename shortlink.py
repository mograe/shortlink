from os import rename
from flask import Flask,request,jsonify,redirect,g
from flask.globals import current_app
import hash
import sql as dbsl
import account
from flask_jwt_extended import JWTManager
from FDataBase import FDataBase
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
import sqlite3




app = Flask(__name__)
app.register_blueprint(account.account_api)
app.config["JWT_SECRET_KEY"] = "VXhr2LfjK*|lwF|~tNv41qnG?#OzJufz3nwGco09ChOZY8|cC41}QH35CqVh35smuEP1x3j8Dt{3~cZMxEZP?aak9?tnkLtXAT"
jwt = JWTManager(app)
DATABASE = 'db.db'
DEBUG = True
SECRET_KEY = 'euorhgudfv%$%hnjdfv8j6y4723hr'
dba = None

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



@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/short')
@jwt_required()
def short():
    db = get_db()
    dba = FDataBase(db)
    current_user = get_jwt_identity()
    user_id = dba.getUserID(current_user)
    url = request.json.get('url', None)
    la = request.json.get('la',None)
    lai = int(la)
    if url and user_id and la and lai<3:
        dbsl.shortlink(user_id,url,la)
        message = {"message":"Ссылка была сокращена успешно","short_link":f"http://127.0.0.1:5000/{dbsl.ret_sl(user_id,url)}"}
        return jsonify(message)
    elif not url:
        message = {"message":"Не задан url для сокращения"}
        return jsonify(message)
    elif not user_id:
        message = {"message":"Не задан айди пользователя"}
        return jsonify(message)
    elif la == None:
        message = {"message":"Не задан уровень доступа к ссылке"}
        return jsonify(message)
    elif lai > 3:
        message = {"message":"Не корректно задан уровень доступа к ссылке"}
        return jsonify(message)
    


@app.route('/<shortlink>')
@jwt_required()
def redir(shortlink):
    if(dbsl.check_name(shortlink)):
        print(dbsl.get_la(shortlink))
        if(dbsl.get_la(shortlink)==0):
            return redirect(dbsl.ret_fulllink(shortlink),code=302)
        elif(dbsl.get_la(shortlink)==1):
            db = get_db()
            dba = FDataBase(db)
            current_user = get_jwt_identity()
            return redirect(dbsl.ret_fulllink(shortlink),code=302)
        else:
            db = get_db()
            dba = FDataBase(db)
            current_user = get_jwt_identity()
            if(dbsl.get_user(shortlink)==current_user):
                return redirect(dbsl.ret_fulllink(shortlink),code=302)
            else:
                message = {"message":"Эта ссылка доступна только автору"}
                return jsonify(message)

    else:
        message = {"message":"Данной ссылки не существует"}
        return jsonify(message)


@app.route('/name')
@jwt_required()
def name():
    db = get_db()
    dba = FDataBase(db)
    current_user = get_jwt_identity()
    user_id = dba.getUserID(current_user)
    name = request.json.get("name", None)
    url = request.json.get('url')
    la = request.json.get('la',None)
    lai = int(la)
    if url and user_id and name and la and lai<3:
        if dbsl.check_name(name):
            message = {"message":"Данный псевдоним занят"}
            return jsonify(message)
        else:
            dbsl.add_name(user_id,url,name,la)
            message = {"message":"Ссылка была сокращена успешно","short_link":f"http://127.0.0.1:5000/{name}"}
            return jsonify(message)
    elif not name:
        message = {"message":"Нет псевдонима для url"}
        return jsonify(message)
    elif not url:
        message = {"message":"Не задан url для сокращения"}
        return jsonify(message)
    elif not user_id:
        message = {"message":"Не задан айди пользователя"}
        return jsonify(message)
    elif la == None:
        message = {"message":"Не задан уровень доступа к ссылке"}
        return jsonify(message)
    elif lai > 3:
        message = {"message":"Не корректно задан уровень доступа к ссылке"}
        return jsonify(message)

@app.route('/list/', methods=['GET'])
@jwt_required()
def list():
    if request.method == "GET":
        db = get_db()
        dba = FDataBase(db)
        current_user = get_jwt_identity()
        user_id = dba.getUserID(current_user)        
        if not user_id:
            return jsonify({"message":"Не задан айди пользователя"})
        message = {}
        if len(dbsl.return_links(user_id))==0:
            return jsonify({"message":"У вас нет сокращённых ссылок"})
        for i in range(len(dbsl.return_links(user_id))):
            message.update({f"Link {i+1}":{"Long URL":dbsl.return_links(user_id)[i][1], "Short Link":f"http://127.0.0.1:5000/{dbsl.return_links(user_id)[i][0]}","Level of Access":dbsl.get_la(dbsl.return_links(user_id)[i][0])}})
        return jsonify(message)




@app.route('/list/<number_link>', methods=['LINK','UNLINK','DELETE','UNLOCK','LOCK','VIEW'])
@jwt_required()
def ch_link(number_link):
    if request.method == "LINK":
        db = get_db()
        dba = FDataBase(db)
        current_user = get_jwt_identity()
        user_id = dba.getUserID(current_user)       
        number_link = int(number_link) - 1
        name = request.json.get("name", None)
        if not user_id:
            return jsonify({"message":"Не задан айди пользователя"})
        if number_link==None:
            return jsonify({"message":"Нет номера ссылки"})
        if not name:
            return jsonify({"message":"Нет желаемого псевдонима"})
        if number_link >=  len(dbsl.return_links(user_id)):
            return jsonify({"message":"У вас нет ссылки под таким номером"})
        if number_link < 0 or type(number_link)!=int:
            return jsonify({"message":"Вы ввели не допустимый номер ссылки"})
        if dbsl.check_name(name):
            message = {"message":"Данный псевдоним занят"}
            return jsonify(message)
        dbsl.rename_link(name,dbsl.get_slink(user_id,number_link),user_id)
        return jsonify({"message":"Ссылка переименовавна успешно","link":f"http://127.0.0.1:5000/{name}"})
    elif request.method == "UNLINK":
        db = get_db()
        dba = FDataBase(db)
        current_user = get_jwt_identity()
        user_id = dba.getUserID(current_user)
        number_link = int(number_link) - 1
        if not user_id:
            return jsonify({"message":"Не задан айди пользователя"})
        if number_link==None:
            return jsonify({"message":"Нет номера ссылки"})
        namelink = dbsl.get_slink(user_id,number_link)
        hashlink = dbsl.hashlink(user_id,dbsl.ret_fulllink(namelink))
        dbsl.rename_link(hashlink,namelink,user_id)
        return jsonify({"message":"Псевдоним был удалён успешно","link":f"http://127.0.0.1:5000/{hashlink}"})
    elif request.method == "DELETE":
        db = get_db()
        dba = FDataBase(db)
        current_user = get_jwt_identity()
        user_id = dba.getUserID(current_user)
        number_link = int(number_link) - 1
        if not user_id:
            return jsonify({"message":"Не задан айди пользователя"})
        if number_link==None:
            return jsonify({"message":"Нет номера ссылки"})
        dbsl.delete_link(dbsl.get_slink(user_id,number_link),user_id)
        return jsonify({"message":"Ссылка удалена успешно"})
    elif request.method == "UNLOCK":
        db = get_db()
        dba = FDataBase(db)
        current_user = get_jwt_identity()
        user_id = dba.getUserID(current_user)
        number_link = int(number_link) - 1
        dbsl.ch_la(dbsl.get_slink(user_id,number_link),user_id,0)
        return jsonify({"message":"Ссылка стала открыта для всех"})
    elif request.method == "LOCK":
        db = get_db()
        dba = FDataBase(db)
        current_user = get_jwt_identity()
        user_id = dba.getUserID(current_user)
        number_link = int(number_link) - 1
        dbsl.ch_la(dbsl.get_slink(user_id,number_link),user_id,2)
        return jsonify({"message":"Ссылка стала доступной только для его владельца"})

    elif request.method == "VIEW":
        db = get_db()
        dba = FDataBase(db)
        current_user = get_jwt_identity()
        user_id = dba.getUserID(current_user)
        number_link = int(number_link) - 1
        dbsl.ch_la(dbsl.get_slink(user_id,number_link),user_id,1)
        return jsonify({"message":"Ссылка стала доступной только для авторизовнных пользователей"})


if __name__ == '__main__':
    app.run()