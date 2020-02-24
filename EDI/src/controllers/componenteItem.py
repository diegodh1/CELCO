
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
            for row in rows:
                cant = int(row.Pro_Item_Cantidad)
                for i in range(cant):
                    sub_item_id = str(ot)+"-"+str(row.Pro_Item_No)+"-"+str(i+1)
                    obj={"item":row.Pro_Item_No,"nro": (i+1),"ot":ot,"id":sub_item_id}
                    items.append(obj)
            for reg in items:
                existe = consultarSubItemOt(reg["ot"], reg["item"],reg["nro"],conn)
                if existe == False:
                    guardarSubItemOt(reg["id"], reg["ot"], reg["item"],reg["nro"],user,conn)
            return {"message": "ok", "data":items}
    except Exception as e:
        return {"message": "Ocurrio un error a la base de datos: "+str(e), "data":[]}

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
def guardarSubItemOt(id_sub_item,ot,item,nro,user,conn):
    try:
        cursor = conn.cursor()
        consulta = "INSERT INTO sub_item (id_sub_item,Prop_Crm_Ot,Pro_Item_No,cons_cant,crea_id,edit_id) VALUES (?,?,?,?,?,?)"
        cursor.execute(consulta,id_sub_item,ot,item,nro,user,user)
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
            consulta = "SELECT DISTINCT PD.Prop_Det_Id,Prop_Det_Desc FROM propuestas_items AS I,propuesta_crm AS P,propuesta_detalle AS PD WHERE I.Cli_Pro_Id=P.Pro_Cli_HijaId AND PD.Pro_Item_Id=I.Pro_Item_Id AND I.Pro_Item_No = ? AND P.Prop_Crm_Ot = ?"
            cursor.execute(consulta,item,ot)
            rows = cursor.fetchall()
            componentes=[]
            for row in rows:
                obj={"id":row.Prop_Det_Id,"descripcion":row.Prop_Det_Desc,"item":item,"nro":nro,"ot":ot}
                componentes.append(obj)
            return {"message": "ok", "data":componentes}
    except Exception as e:
        return {"message": "Ocurrio un error a la base de datos: "+str(e), "data":[]}

"""
nombre: saveComponenteSubItem
params: el id del sub_item, el id del componente, el id del usuario, un booleano y una conexion a la BD
return: un json el cual contiene un mensaje que indica el resultado de la operacion
"""
def saveComponenteSubItem(id_sub_item,id_componente,user,requerida,conn):
    try:
        cursor = conn.cursor()
        consulta = "INSERT INTO compte_sub_item (id_sub_item,Prop_Det_Id,crea_id,edit_id) VALUES (?,?,?,?)"
        existe = consultarCompteSubItem(id_sub_item,id_componente,conn)
        if(existe == True):
            return actualizarCompteSubItm(requerida,id_sub_item,id_componente,user,conn)
        else:
            cursor.execute(consulta,id_sub_item,id_componente,user,user)
            conn.commit()
        return {"message": "ok, registro realizado"}
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
