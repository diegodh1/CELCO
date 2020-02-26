from flask import Flask,jsonify,request
from users import users
from controllers.login import userLogin
from controllers.connection import conn
from controllers.componenteItem import searchOt,getItemsOt,getComponentesItem,saveComponenteSubItem,getComponentesSubItem
from controllers.fileHandler import getRutas,getFilesFromPath,getFile64bits,saveImage
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
    content=request.get_json()
    path=content['path']
    b64=getFile64bits(path)
    return b64
""" Nombre: uploadFile
    Tipo de peticion:POST
    descripcion: recibe una peticion post la cual tiene como parametro una imagen de 64 bits, un path y un nombre
    return: retorna un mensaje el cual indica si la operacion se realizo o no exitosamente
"""
@app.route('/uploadFile',methods=['POST'])
def uploadFile():
    content=request.get_json()
    data=content['image']
    path=content['path']
    name=content['name']
    return saveImage(data, path,name)

""" Nombre: getItems
    Tipo de peticion:POST
    descripcion: recibe una peticion post la cual tiene como parametro el numero de la OT
    return: retorna un json con los items de la OT y un mensaje de error o exito al realizar la operacion
"""
@app.route('/getItems',methods=['POST'])
def getItems():
    content=request.get_json()
    ot=content['ot']
    user=content['user']
    retult = getItemsOt(ot,user, conn)
    return jsonify(retult)

""" Nombre: getComponentes
    Tipo de peticion:POST
    descripcion: recibe una peticion post la cual tiene como parametro el numero de la OT, el item, el nro: consecutivo cantidad
    return: retorna un json con los componentes del Item y un mensaje de error o exito al realizar la operacion
"""
@app.route('/getComponentes',methods=['POST'])
def getComponentes():
    content=request.get_json()
    ot=content['ot']
    item=content['item']
    nro=content['nro']
    retult = getComponentesItem(item,nro,ot, conn)
    return jsonify(retult)

""" Nombre: saveComponente
    Tipo de peticion:POST
    descripcion: recibe una peticion post la cual tiene como parametro el id del sub_item, el id del componente, el usuario y si es requerido o no el material
    return: retorna un json el cual contiene un mensaje de error o exito al realizar la operacion
"""
@app.route('/saveComponente',methods=['POST'])
def saveComponente():
    content=request.get_json()
    id_sub_item=content['id_sub_item']
    componente=content['id_componente']
    user=content['id_usuario']
    requerida=content['requerida']
    item=content['item']
    nro=content['nro']
    ot=content['ot']
    result = saveComponenteSubItem(id_sub_item,componente,user, requerida,item,nro,ot,conn)
    return jsonify(result)

""" Nombre: getCompteSubItem
    Tipo de peticion:POST
    descripcion: recibe una peticion post la cual tiene como parametro el id del sub_item
    return: retorna un json con los componentes del sub_item y un mensaje de error o exito al realizar la operacion
"""
@app.route('/getCompteSubItem',methods=['POST'])
def getCompteSubItem():
    content=request.get_json()
    id_sub_item=content['id_sub_item']
    retult = getComponentesSubItem(id_sub_item, conn)
    return jsonify(retult)

""" Nombre: search_ot
    Tipo de peticion:POST
    descripcion: recibe una peticion post la cual tiene como parametro el id de la OT
    return: retorna un json con el encabezado de la de la remision
"""
@app.route('/search_ot',methods=['POST'])
def search_ot():
    content=request.get_json()
    ot_id = content['ot']
    retult = searchOt(ot_id, conn)
    return jsonify(retult)

#inicializamos el servidor el cual escucha en el puerto 4000 y se reinicia cada vez q hayan cambios
if __name__=='__main__':
    app.run(host="0.0.0.0",port=4000,debug=True)
