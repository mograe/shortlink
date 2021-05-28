from os import rename
from flask import Flask,request,jsonify,redirect
import hash
import sql
import account
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.register_blueprint(account.account_api)
app.config["JWT_SECRET_KEY"] = "VXhr2LfjK*|lwF|~tNv41qnG?#OzJufz3nwGco09ChOZY8|cC41}QH35CqVh35smuEP1x3j8Dt{3~cZMxEZP?aak9?tnkLtXAT"
jwt = JWTManager(app)
DATABASE = 'db.db'
DEBUG = True
SECRET_KEY = 'euorhgudfv%$%hnjdfv8j6y4723hr'


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/short')
def short():
    user_id = request.json.get('user_id',None)
    url = request.json.get('url', None)
    if url and user_id:
        sql.shortlink(user_id,url)
        message = {"message":"Ссылка была сокращена успешно","short_link":f"http://127.0.0.1:5000/{sql.ret_sl(user_id,url)}"}
        return jsonify(message)
    elif not url:
        message = {"message":"Не задан url для сокращения"}
        return jsonify(message)
    elif not user_id:
        message = {"message":"Не задан айди пользователя"}
        return jsonify(message)


@app.route('/<shortlink>')
def redir(shortlink):
    if(sql.check_name(shortlink)):
        return redirect(sql.ret_fulllink(shortlink),code=302)
    else:
        message = {"message":"Данной ссылки не существует"}
        return jsonify(message)

@app.route('/name')
def name():
    user_id = request.json.get("user_id", None)
    name = request.json.get("name", None)
    url = request.args.get('url')
    if url and user_id:
        if sql.check_name(name):
            message = {"message":"Данный псевдоним занят"}
            return jsonify(message)
        else:
            sql.add_name(user_id,url,name)
            message = {"message":"Ссылка была сокращена успешно","short_link":f"http://127.0.0.1:5000/{name}"}
            return jsonify(message)
    elif name:
        message = {"message":"Нет псевдонима для url"}
        return jsonify(message)
    elif not url:
        message = {"message":"Не задан url для сокращения"}
        return jsonify(message)
    elif not user_id:
        message = {"message":"Не задан айди пользователя"}
        return jsonify(message)

@app.route('/list/', methods=['GET'])
def list():
    if request.method == "GET":
        user_id = request.json.get("user_id", None)
        if not user_id:
            return jsonify({"message":"Не задан айди пользователя"})
        message = {}
        if len(sql.return_links(user_id))==0:
            return jsonify({"message":"У вас нет сокращённых ссылок"})
        for i in range(len(sql.return_links(user_id))):
            message.update({f"Link {i+1}":{"Long URL":sql.return_links(user_id)[i][1], "Short Link":f"http://127.0.0.1:5000/{sql.return_links(user_id)[i][0]}"}})
        return jsonify(message)




@app.route('/list/<number_link>', methods=['LINK','UNLINK','DELETE'])
def ch_link(number_link):
    if request.method == "LINK":
        user_id = request.json.get("user_id", None)
        number_link = int(number_link) - 1
        name = request.json.get("name", None)
        if not user_id:
            return jsonify({"message":"Не задан айди пользователя"})
        if number_link==None:
            return jsonify({"message":"Нет номера ссылки"})
        if not name:
            return jsonify({"message":"Нет желаемого псевдонима"})
        if number_link >=  len(sql.return_links(user_id)):
            return jsonify({"message":"У вас нет ссылки под таким номером"})
        if number_link < 0 or type(number_link)!=int:
            return jsonify({"message":"Вы ввели не допустимый номер ссылки"})
        if sql.check_name(name):
            message = {"message":"Данный псевдоним занят"}
            return jsonify(message)
        sql.rename_link(name,sql.get_slink(user_id,number_link),user_id)
        return jsonify({"message":"Ссылка переименовавна успешно","link":f"http://127.0.0.1:5000/{name}"})
    elif request.method == "UNLINK":
        user_id = request.json.get("user_id", None)
        number_link = int(number_link) - 1
        if not user_id:
            return jsonify({"message":"Не задан айди пользователя"})
        if number_link==None:
            return jsonify({"message":"Нет номера ссылки"})
        namelink = sql.get_slink(user_id,number_link)
        hashlink = sql.hashlink(user_id,sql.ret_fulllink(namelink))
        sql.rename_link(hashlink,namelink,user_id)
        return jsonify({"message":"Псевдоним был удалён успешно","link":f"http://127.0.0.1:5000/{hashlink}"})
    elif request.method == "DELETE":
        user_id = request.json.get("user_id", None)
        number_link = int(number_link) - 1
        if not user_id:
            return jsonify({"message":"Не задан айди пользователя"})
        if number_link==None:
            return jsonify({"message":"Нет номера ссылки"})
        sql.delete_link(sql.get_slink(user_id,number_link),user_id)
        return jsonify({"message":"Ссылка удалена успешно"})



if __name__ == '__main__':
    app.run()