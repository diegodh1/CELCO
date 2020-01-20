from flask import Flask,jsonify,request
from users import users
from controllers.login import userLogin
from controllers.connection import conn

app=Flask(__name__)
@app.route('/',methods=['GET'])
def ping():
    return jsonify({"response":"hello world"})
@app.route('/users')
def usersHandler():
    return jsonify({"users":users})
@app.route('/login',methods=['POST'])
def login():
    user=request.form['user']
    password=request.form['password']
    userId= userLogin(user,password,conn)
    if userId =="":
        return {
            "userId":"",
            "message":"Problemas al iniciar sección"
        }
    else:
        return {
            "userId":userId,
            "message":"Bienvenido "+user
        }


if __name__=='__main__':
    app.run(host="0.0.0.0",port=4000,debug=True)
