import psycopg2
import psycopg2.extras

class Model:

    def __init__(self, dbname, user, host, password):
        self.dbname = dbname
        self.user = user
        self.host = host
        self.password = password

    def busqueda_dni(self, dni):
        try:
            connect_str = "dbname=%s user=%s host=%s password=%s" %(self.dbname, self.user, self.host, self.password)
            conn = psycopg2.connect(connect_str)
            try:
                cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
                try:
                    cursor.execute("SELECT dni, u.id, lastname, name, c.stock from profile.users u left outer join assistance.justification_compensatory_stock c on (u.id = c.user_id) where dni = %s", (dni,))
                    persona = cursor.fetchone()
                finally:
                    cursor.close()
            finally:
                conn.close()
        except Exception as e:
            print("Falla de conexion., Nombre de Base de datos, usuario o contrasenia?")
            print(e)
            persona="error"
        return persona

    def actualizarCompensatorios(self, id, compensatorios):
        try:
            connect_str = "dbname=%s user=%s host=%s password=%s" %(self.dbname, self.user, self.host, self.password)
            conn = psycopg2.connect(connect_str)
            try:
                cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
                #cursor.execute("SELECT dni, u.id, lastname, name, c.stock from profile.users u left outer join assistance.justification_compensatory_stock c on (u.id = c.user_id) where user_id = %s", (id,))
                try:
                    cursor.execute("SELECT stock from assistance.justification_compensatory_stock where user_id = %s", (id,))
                    if cursor.fetchone() == None:
                        print("Creando entrada para usuario.")
                        cursor.execute("INSERT INTO assistance.justification_compensatory_stock (user_id, stock) VALUES (%s,%s)", (id, compensatorios))
                    else:
                        print("Actualizando Usuario")
                        cursor.execute("UPDATE assistance.justification_compensatory_stock SET stock = stock + %s WHERE user_id = %s", (compensatorios, id))
                    conn.commit()
                    print("Se actualizaron los compensatorios del usuario.")
                finally:
                    cursor.close()
            finally:
                conn.close()
        except Exception as e:
            print("Falla de conexion.")
            print(e)
            persona = "error"
        return None
        