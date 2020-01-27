import os
import base64

"""
nombre: getRutas
params: una conexion a la base de datos
return: obtiene todas las rutas o directorios disponibles que tiene disponible el usuario para ver
"""
def getRutas(conn):
    try:
        with conn.cursor() as cursor:
            consulta = "SELECT Ruta_Arc_Tipo,Ruta_Arc_Ruta FROM rutas_archivos WHERE Ruta_Arc_Activo = ? AND Ruta_Arc_Tipo IN (?,?)"
            cursor.execute(consulta,"1", "Fotos_OT","Planos_OT")
            rows = cursor.fetchall()
            rutas=[]
            for row in rows:
                obj={"nombre":row.Ruta_Arc_Tipo,"ruta":row.Ruta_Arc_Ruta}
                rutas.append(obj)
            return rutas
    except Exception as e:
        print("Ocurrio un error a la base de datos: ", e)

"""
nombre: getFilesFromPath
params: una ruta o path
return: obtiene todas los archivos y directorios que hay dentro de un directorio
"""
def getFilesFromPath(ruta):
    ruta=ruta.replace("\\","/")
    files=[]
    for path in os.listdir(ruta):
        obj={}
        full_path = os.path.join(ruta, path)
        if os.path.isfile(full_path):
            ext=path.split(".")
            if len(ext)>1:
                temp=ext[1].lower()
                if(temp=="jpg" or temp=="png" or temp=="gif" or temp=="jpeg"):
                    obj={"nombre":path,"extension":ext[1],"ruta":full_path.replace("\\","/"),"tipo":"imagen"}
                    files.append(obj)
                if(temp=="pdf"):
                    obj={"nombre":path,"extension":ext[1],"ruta":full_path.replace("\\","/"),"tipo":"documento"}
                    files.append(obj)
        else:
            obj={"nombre":path,"extension":"none","ruta":full_path.replace("\\","/"),"tipo":"folder"}
            files.append(obj)
    return files

"""
nombre: getFile64bits
params: una ruta o path
return: un texto el cual contiene la informacion de un archivo decodificado en 64bits
"""
def getFile64bits(filePath):
    with open(filePath, "rb") as f:
        encoded_string = base64.b64encode(f.read())
        return encoded_string