
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
dirname = os.path.dirname(__file__)

"""
nombre: getItemsOt
params: el id de la ot
return: un json el cual contiene todos los items de la ot
"""
def getItemsOt(ot,user,conn):
    try:
        with conn.cursor() as cursor:
            consulta = "SELECT DISTINCT I.Pro_Item_No,I.Pro_Item_Cantidad  FROM propuestas_items AS I,propuesta_crm AS P,ciudades AS C WHERE I.Cli_Pro_Id=P.Pro_Cli_HijaId AND P.Prop_Crm_Ot=?"
            cursor.execute(consulta,ot)
            rows = cursor.fetchall()
            items=[]
            itemsTable=[]
            guardarRemision(ot,user,conn)
            remision_id = getLastRemision(ot,conn)
            for row in rows:
                cant = int(row.Pro_Item_Cantidad)
                for i in range(cant):
                    sub_item_id = str(remision_id)+"-"+str(row.Pro_Item_No)+"-"+str(i+1)
                    obj={"item":row.Pro_Item_No,"nro": (i+1),"ot":ot,"id":sub_item_id}
                    obj1=[ot,sub_item_id,row.Pro_Item_No,(i+1)]
                    items.append(obj)
                    itemsTable.append(obj1)
            
            for reg in items:
                    guardarSubItemOt(reg["id"], remision_id, reg["item"],reg["nro"],user,conn)
            return {"message": "ok", "data":items, "remision_id":remision_id}
    except Exception as e:
        return {"message": "Ocurrio un error a la base de datos: "+str(e), "data":[]}
"""
nombre: guardarRemision
params: el id de la ot, el id del usuario
return: un booleano el cual representa la accion de guardar remision
"""
def guardarRemision(ot,user,conn):
    try:
        cursor = conn.cursor()
        consulta = "INSERT INTO remision (Prop_Crm_Ot,crea_Id,edita_Id) VALUES (?,?,?)"
        cursor.execute(consulta,ot,user,user)
        conn.commit()
        return True
    except Exception as e:
        print("error: "+ str(e))
        return False

"""
nombre: getLastRemision
params: el id de la ot
return: el id de la ultima remision guardada en la DB
"""
def getLastRemision(ot,conn):
    try:
        with conn.cursor() as cursor:
            consulta = "SELECT TOP 1 remision_id from remision where Prop_Crm_Ot = ? ORDER BY remision_id DESC"
            cursor.execute(consulta,ot)
            rows = cursor.fetchall()
            for row in rows:
                return row.remision_id
    except Exception as e:
        print("Error: " + str(e))
        return 0

"""
nombre: consultarSubItemOt
params: el id de la ot, el id del item, y el consecutivo de la cantidad
return: un boolean diciendo si el sub_item existe o no
"""
def consultarSubItemOt(ot,item,nro,conn):
    try:
        with conn.cursor() as cursor:
            consulta = "SELECT COUNT(I.id_sub_item) AS cantidad FROM rem_sub_item AS I, remision AS R WHERE R.remision_id=I.remision_id AND R.Prop_Crm_Ot = ?  AND I.Pro_Item_No = ? AND I.cons_cant = ?"
            cursor.execute(consulta,ot,item,nro)
            rows = cursor.fetchall()
            for row in rows:
                cant = int(row.cantidad)
                if cant > 0:
                    return True
                else:
                    return False
    except Exception:
        return False
"""
nombre: guardarSubItemOt
params: el id de la ot, el id del item, el consecutivo de la cantidad y el usuario
return: un boolean diciendo si el sub_item se inserto o no con exito
"""
def guardarSubItemOt(id_sub_item,remision_id,item,nro,user,conn):
    try:
        cursor = conn.cursor()
        consulta = "INSERT INTO rem_sub_item (id_sub_item,remision_id,Pro_Item_No,cons_cant,crea_id,edit_id) VALUES (?,?,?,?,?,?)"
        cursor.execute(consulta,id_sub_item,remision_id,item,nro,user,user)
        conn.commit()
        return True
    except Exception as e:
        print("error: "+ str(e))
        return False


"""
nombre: getComponentesItem
params: el nro del item, el id de la ot y la conexion a la bd
return: un json el cual contiene todos los compoenentes necesarios para construir un item
"""
def getComponentesItem(item,nro,ot,id_sub_item,conn):
    try:
        with conn.cursor() as cursor:
            consulta = """SELECT cpte_item.cantidad2 as cant_aux,cpte_item.Item_Id,cpte_item.Prop_Det_Id,cpte_item.Prop_Det_Desc,ISNULL(cpte_rem_item.compte_cant,cpte_item.cantidad2) AS cantidad,ISNULL(cpte_rem_item.compte_obs,'') AS obs,ISNULL(cpte_rem_item.requerida,0) AS requerida 
                        FROM (SELECT DISTINCT PD.Item_Id AS Item_Id,PD.Prop_Det_Id AS Prop_Det_Id,Prop_Det_Desc AS Prop_Det_Desc,PD.Prop_Det_Cantidad AS cantidad2 
                        FROM propuestas_items AS I,propuesta_crm AS P,propuesta_detalle AS PD WHERE I.Cli_Pro_Id=P.Pro_Cli_HijaId AND PD.Pro_Item_Id=I.Pro_Item_Id AND I.Pro_Item_No = ? AND P.Prop_Crm_Ot = ?) AS cpte_item 
                        LEFT JOIN 
                        (SELECT RC.Prop_Det_Id AS Prop_Det_Id,RC.compte_cant AS compte_cant,RC.compte_obs AS compte_obs,RC.requerida AS requerida FROM rem_sub_item as RS,rem_cpte_sub_item as RC where RS.id_sub_item=RC.id_sub_item  AND RS.id_sub_item=?) AS cpte_rem_item 
                        ON cpte_item.Prop_Det_Id=cpte_rem_item.Prop_Det_Id"""

            cursor.execute(consulta,item,ot,id_sub_item)
            rows = cursor.fetchall()
            componentes=[]
            for row in rows:
                obj={"cant_aux":str(row.cant_aux),"id_aux":row.Item_Id,"id":row.Prop_Det_Id,"descripcion":row.Prop_Det_Desc,"item":item,"nro":nro,"ot":ot,"id_sub_item":id_sub_item,"requerida":row.requerida,"cantidad":str(row.cantidad),"obs":row.obs}
                componentes.append(obj)
            return {"message": "ok", "data":componentes}
    except Exception as e:
        return {"message": "Ocurrio un error a la base de datos: "+str(e), "data":[]}

"""
nombre: saveComponenteSubItem
params: el id del sub_item, el id del componente, el id del usuario, un booleano y una conexion a la BD
return: un json el cual contiene un mensaje que indica el resultado de la operacion
"""
def saveComponenteSubItem(id_sub_item,id_componente,user,requerida,compte_cant,compte_obs,item,nro,ot,conn):
    try:
        cursor = conn.cursor()
        consulta = "INSERT INTO rem_cpte_sub_item (id_sub_item,Prop_Det_Id,compte_cant,compte_obs,crea_id,edit_id) VALUES (?,?,?,?,?,?)"
        existe = consultarCompteSubItem(id_sub_item,id_componente,conn)
        if(existe == True):
            actualizarCompteSubItm(requerida,compte_cant,compte_obs,id_sub_item,id_componente,user,conn)
        else:
            cursor.execute(consulta,id_sub_item,id_componente,compte_cant,compte_obs,user,user)
            conn.commit()
        return getComponentesItem(item,nro,ot,id_sub_item,conn)
    except Exception as e:
        return {"message": "error, "+str(e)}

"""
nombre: consultarCompteSubItem
params: el id del sub_item, el id del componente
return: un booleano indicando si existe o no el componente del subitem
"""
def consultarCompteSubItem(id_sub_item,id_componente,conn):
    try:
        with conn.cursor() as cursor:
            consulta = "SELECT COUNT(I.id_sub_item) AS cantidad FROM rem_cpte_sub_item AS I WHERE I.id_sub_item = ? AND I.Prop_Det_Id = ?"
            cursor.execute(consulta,id_sub_item,id_componente)
            rows = cursor.fetchall()
            for row in rows:
                cant = int(row.cantidad)
                if cant > 0:
                    return True
                else:
                    return False
    except Exception:
        return False
"""
nombre: actualizarCompteSubItm
params: un booleano, id del sub_item, id del componente, usuario y conexion a la BD
return: un JSON que indica un mensaje con el resultado de la operacion
"""
def actualizarCompteSubItm(requerida,compte_cant,compte_obs,id_sub_item,id_componente,user,conn):
    try:
        cursor = conn.cursor()
        consulta = "UPDATE rem_cpte_sub_item SET requerida = ?,compte_cant = ?,compte_obs = ?, edit_id = ? WHERE id_sub_item = ? AND Prop_Det_Id = ?"
        cursor.execute(consulta,requerida,compte_cant,compte_obs,user,id_sub_item,id_componente)
        conn.commit()
        return {"message": "ok, registro realizado"}
    except Exception as e:
        return {"message": "error, "+str(e)}
"""
nombre: getComponentesSubItem
params: el id del sub_item
return: un JSON el cual muestra todos los componentes que se estan usando o no en un sub_item
"""
def getComponentesSubItem(item_id,conn):
    try:
        with conn.cursor() as cursor:
            consulta = "SELECT S.id_sub_item, S.Prop_Crm_Ot, S.Pro_Item_No, S.cons_cant,PD.Prop_Det_Desc,PD.Prop_Det_Id,C.requerida FROM compte_sub_item AS C, sub_item AS S, propuesta_detalle AS PD WHERE C.id_sub_item=S.id_sub_item AND C.Prop_Det_Id=PD.Prop_Det_Id AND  C.id_sub_item = ?"
            cursor.execute(consulta,item_id)
            rows = cursor.fetchall()
            componentes=[]
            for row in rows:
                obj={"id_sub_item":row.id_sub_item,"id_compte":row.Prop_Det_Id,"ot":row.Prop_Crm_Ot,"item":row.Pro_Item_No,"nro":row.cons_cant,"descripcion":row.Prop_Det_Desc,"requerida":row.requerida}
                componentes.append(obj)
            return {"message": "ok", "data":componentes}
    except Exception as e:
        return {"message": "Ocurrio un error a la base de datos: "+str(e), "data":[]}

"""
nombre: searchOt
params: el id de la ot
return: un JSON el cual muestra toda la informacion del encabezado de la remision
"""
def searchOt(ot_id,conn):
    try:
        remisiones = getRemisiones(ot_id,conn)
        with conn.cursor() as cursor:
            consulta = """SELECT E.Ter_Nombre as cliente,E.Ter_Rut as rut,E.Ter_Direccion as direccion,(SELECT DISTINCT C.Ciu_Ciudad FROM propuestas_items AS P, propuesta_crm AS CR, ciudades AS C WHERE P.Cli_Pro_Id=CR.Pro_Cli_HijaId AND P.Pro_Item_Ciu_Id=C.Id_Ciu AND CR.Prop_Crm_Ot=E.OT_No) as ciudad,E.Contacto,E.OT_No,
                        (SELECT DISTINCT PER.Per_Nombres FROM propuesta_clientes AS PC, personas AS PER,propuesta_crm AS CR WHERE PC.Pro_Cli_PapaId=CR.Pro_Cli_PapaId AND PC.Pro_Cli_Id_Vendedor=PER.Per_Id AND CR.Prop_Crm_Ot=E.OT_No) AS vendedor,
                        (SELECT DISTINCT PC.Pro_Cli_OC  FROM propuesta_clientes AS PC, propuesta_crm AS CR WHERE PC.Pro_Cli_PapaId=CR.Pro_Cli_PapaId AND CR.Prop_Crm_Ot=E.OT_No) AS orden
                        FROM OT_Encabezado AS E  where E.OT_No = ?"""
            cursor.execute(consulta,ot_id)
            rows = cursor.fetchall()
            obj={"cliente":"","rut":"","direccion":"","ciudad":"","contacto":"","ot":"","vendedor":"","orden":"", "remisiones":[]}
            for row in rows:
                obj={"cliente":row.cliente,"rut":row.rut,"direccion":row.direccion,"ciudad":row.ciudad,"contacto":row.Contacto,"ot":row.OT_No,"vendedor":row.vendedor,"orden":row.orden, "remisiones":remisiones}
            return obj
    except Exception:
        return {}
"""
nombre: getRemisiones
params: el id de la ot
return: un JSON el cual muestra todas las remisiones realizadas con el numero de ot
"""
def getRemisiones(ot_id,conn):
    try:
        with conn.cursor() as cursor:
            consulta = """
            select remision_id as id, Prop_Crm_Ot as ot,FORMAT (fecha_crea, 'yyyy-MM-dd') as fecha_crea,R.activo as activo  from remision  as R where R.Prop_Crm_Ot = ?
            """
            cursor.execute(consulta,ot_id)
            rows = cursor.fetchall()
            remisiones=[]
            for row in rows:
                obj={"id":row.id,"ot":row.ot,"fecha_crea":row.fecha_crea,"activo":row.activo}
                remisiones.append(obj)
            return remisiones
    except Exception:
        return []

"""
nombre: getRemision
params: el id de la remision
return: un JSON el cual muestra toda la informacion de la remision buscada
"""
def getRemision(id_rem,conn):
    try:
        with conn.cursor() as cursor:
            consulta = """
            select S.Pro_Item_No as item, S.cons_cant as nro,R.Prop_Crm_Ot as ot,S.id_sub_item as id from remision as R, rem_sub_item as S where R.remision_id=S.remision_id AND R.remision_id = ?
            """
            cursor.execute(consulta,id_rem)
            rows = cursor.fetchall()
            items=[]
            for row in rows:
                obj={"item":row.item,"nro":row.nro,"ot":row.ot,"id":row.id}
                items.append(obj)
            return {"message": "ok", "data":items, "remision_id":id_rem}
    except Exception:
        return []



