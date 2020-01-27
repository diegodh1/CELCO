from flask import Flask,jsonify,request
from users import users
from controllers.login import userLogin
from controllers.connection import conn
from controllers.fileHandler import getRutas,getFilesFromPath,getFile64bits
from flask_cors import CORS

app=Flask(__name__)
CORS(app)
""" Nombre: login
    Tipo de peticion:POST
    descripcion: recibe en la peticion un usuario y una contrasena la cual se verifica en la base de datos que
    coincidan para poder permitir el ingreso de un usuario a la aplicacion
    return:retorna un JSON el cual tiene el id del usuario y un mensaje de bienvenida
"""

@app.route('/login',methods=['POST'])
def login():
    content=request.get_json()
    user=content['user']
    password=content['password']
    userId= userLogin(user,password,conn)
    if userId =="":
        return {
            "userId":"",
            "message":"usuario y/o contraseña incorrectos"
        }
    else:
        return {
            "userId":userId,
            "message":"Ingreso Realizado"
        }

""" Nombre: getServerRoutes
    Tipo de peticion:GET
    descripcion: recibe una peticion get la cual da como resultado los directorios disponibles que tiene el usuario
    para ver los archivos
    return:retorna un JSON el cual tiene un array de todas las rutas de los directorios disponibles
"""
@app.route('/getRoutes',methods=['GET'])
def getServerRoutes():
    routes=getRutas(conn)
    return jsonify({"routes":routes})

""" Nombre: getFiles
    Tipo de peticion:POST
    descripcion: recibe una peticion post la cual tiene como parametro una ruta donde queremos ver los archivos
    disponibles
    return:retorna un JSON el cual tiene un array de todos los archivos y directorios disponibles de la ruta
"""
@app.route('/getFiles',methods=['POST'])
def getFiles():
    content=request.get_json()
    path=content['path']
    dire=getFilesFromPath(path)
    return jsonify({
        "directory":dire,
        "message":"status 200, ok"
        })

""" Nombre: getb64bits
    Tipo de peticion:POST
    descripcion: recibe una peticion post la cual tiene como parametro una ruta de un archivo y da como resultado
    el archivo decodificado en 64bits
    return:retorna un texto el cual es un archivo decodificado en cadena de caracteres
"""
@app.route('/getb64bits',methods=['POST'])
def getb64bits():
    path=request.form['path']
    b64=getFile64bits(path)
    return b64


#inicializamos el servidor el cual escucha en el puerto 4000 y se reinicia cada vez q hayan cambios
if __name__=='__main__':
    app.run(host="0.0.0.0",port=4000,debug=True)
