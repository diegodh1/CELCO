def userLogin(user,password,conn):
    try:
        with conn.cursor() as cursor:
            consulta = "SELECT Usu_Id FROM usuarios WHERE Usu_Login = ? AND Usu_Password=? AND Usu_Activo=1"
            cursor.execute(consulta, user,password)
            rows = cursor.fetchall()
            userId=""
            for row in rows:
                userId=row.Usu_Id
            return userId
    except Exception as e:
        print("Ocurrio un error a la base de datos: ", e)
