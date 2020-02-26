
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
            for row in rows:
                cant = int(row.Pro_Item_Cantidad)
                for i in range(cant):
                    sub_item_id = str(ot)+"-"+str(row.Pro_Item_No)+"-"+str(i+1)
                    obj={"item":row.Pro_Item_No,"nro": (i+1),"ot":ot,"id":sub_item_id}
                    obj1=[ot,sub_item_id,row.Pro_Item_No,(i+1)]
                    items.append(obj)
                    itemsTable.append(obj1)
            for reg in items:
                existe = consultarSubItemOt(reg["ot"], reg["item"],reg["nro"],conn)
                if existe == False:
                    guardarRemision(ot,conn)
                    remision_id = getRemision(ot,conn)
                    guardarSubItemOt(reg["id"], reg["ot"], reg["item"],reg["nro"],user,remision_id,conn)
            remision_id = getRemision(ot,conn)
            return {"message": "ok", "data":items, "remision_id":remision_id}
    except Exception as e:
        return {"message": "Ocurrio un error a la base de datos: "+str(e), "data":[]}

def guardarRemision(ot,conn):
    try:
        cursor = conn.cursor()
        consulta = "INSERT INTO remision (Prop_Crm_Ot) VALUES (?)"
        cursor.execute(consulta,ot)
        conn.commit()
        return True
    except Exception as e:
        print("error: "+ str(e))
        return False

def getRemision(ot,conn):
    try:
        with conn.cursor() as cursor:
            consulta = "SELECT remision_id from remision where Prop_Crm_Ot = ?"
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
            consulta = "SELECT COUNT(I.id_sub_item) AS cantidad FROM sub_item AS I WHERE I.Prop_Crm_Ot = ?  AND I.Pro_Item_No = ? AND I.cons_cant = ?"
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
def guardarSubItemOt(id_sub_item,ot,item,nro,user,remision_id,conn):
    try:
        cursor = conn.cursor()
        consulta = "INSERT INTO sub_item (id_sub_item,Prop_Crm_Ot,Pro_Item_No,cons_cant,crea_id,edit_id,remision_id) VALUES (?,?,?,?,?,?,?)"
        cursor.execute(consulta,id_sub_item,ot,item,nro,user,user,remision_id)
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
def getComponentesItem(item,nro,ot,conn):
    try:
        with conn.cursor() as cursor:
            consulta = """SELECT DISTINCT PD.Prop_Det_Id,Prop_Det_Desc,
            isnuLl((SELECT cpte.requerida FROM compte_sub_item as cpte,sub_item as si where cpte.id_sub_item=si.id_sub_item and si.Pro_Item_No=I.Pro_Item_No and si.Prop_Crm_Ot=P.Prop_Crm_Ot and si.cons_cant = ? and cpte.Prop_Det_Id=PD.Prop_Det_Id ),0) AS requerida
             FROM propuestas_items AS I,propuesta_crm AS P,propuesta_detalle AS PD WHERE I.Cli_Pro_Id=P.Pro_Cli_HijaId AND PD.Pro_Item_Id=I.Pro_Item_Id AND I.Pro_Item_No = ? AND P.Prop_Crm_Ot = ? """

            cursor.execute(consulta,nro,item,ot)
            rows = cursor.fetchall()
            componentes=[]
            for row in rows:
                obj={"id":row.Prop_Det_Id,"descripcion":row.Prop_Det_Desc,"item":item,"nro":nro,"ot":ot,"requerida":row.requerida}
                componentes.append(obj)
            return {"message": "ok", "data":componentes}
    except Exception as e:
        return {"message": "Ocurrio un error a la base de datos: "+str(e), "data":[]}

"""
nombre: saveComponenteSubItem
params: el id del sub_item, el id del componente, el id del usuario, un booleano y una conexion a la BD
return: un json el cual contiene un mensaje que indica el resultado de la operacion
"""
def saveComponenteSubItem(id_sub_item,id_componente,user,requerida,item,nro,ot,conn):
    try:
        cursor = conn.cursor()
        consulta = "INSERT INTO compte_sub_item (id_sub_item,Prop_Det_Id,crea_id,edit_id) VALUES (?,?,?,?)"
        existe = consultarCompteSubItem(id_sub_item,id_componente,conn)
        if(existe == True):
            actualizarCompteSubItm(requerida,id_sub_item,id_componente,user,conn)
        else:
            cursor.execute(consulta,id_sub_item,id_componente,user,user)
            conn.commit()
        return getComponentesItem(item,nro,ot,conn)
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
            consulta = "SELECT COUNT(I.id_sub_item) AS cantidad FROM compte_sub_item AS I WHERE I.id_sub_item = ? AND I.Prop_Det_Id = ?"
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
def actualizarCompteSubItm(requerida,id_sub_item,id_componente,user,conn):
    try:
        cursor = conn.cursor()
        consulta = "UPDATE compte_sub_item SET requerida = ?, edit_id = ? WHERE id_sub_item = ? AND Prop_Det_Id = ?"
        cursor.execute(consulta,requerida,user,id_sub_item,id_componente)
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
        with conn.cursor() as cursor:
            consulta = """SELECT E.Ter_Nombre as cliente,E.Ter_Rut as rut,E.Ter_Direccion as direccion,(SELECT DISTINCT C.Ciu_Ciudad FROM propuestas_items AS P, propuesta_crm AS CR, ciudades AS C WHERE P.Cli_Pro_Id=CR.Pro_Cli_HijaId AND P.Pro_Item_Ciu_Id=C.Id_Ciu AND CR.Prop_Crm_Ot=E.OT_No) as ciudad,E.Contacto,E.OT_No,
                        (SELECT DISTINCT PER.Per_Nombres FROM propuesta_clientes AS PC, personas AS PER,propuesta_crm AS CR WHERE PC.Pro_Cli_PapaId=CR.Pro_Cli_PapaId AND PC.Pro_Cli_Id_Vendedor=PER.Per_Id AND CR.Prop_Crm_Ot=E.OT_No) AS vendedor,
                        (SELECT DISTINCT PC.Pro_Cli_OC  FROM propuesta_clientes AS PC, propuesta_crm AS CR WHERE PC.Pro_Cli_PapaId=CR.Pro_Cli_PapaId AND CR.Prop_Crm_Ot=E.OT_No) AS orden
                        FROM OT_Encabezado AS E  where E.OT_No = ?"""
            cursor.execute(consulta,ot_id)
            rows = cursor.fetchall()
            for row in rows:
                obj={"cliente":row.cliente,"rut":row.rut,"direccion":row.direccion,"ciudad":row.ciudad,"contacto":row.Contacto,"ot":row.OT_No,"vendedor":row.vendedor,"orden":row.orden}
            return obj
    except Exception:
        return {}

