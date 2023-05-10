from .entities.User import User
import oracle


class ModelUser():

    @classmethod
    def login(self, user):
        try:
            db = oracle.connection('stock','stock')
            cursor = db.cursor()
            sql = """SELECT USUARIO_ORACLE, PASSWORD, NOMBRE FROM USUARIO 
                    WHERE USUARIO_ORACLE = '{}'""".format(user.username.upper())
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                user = User(row[0], User.check_password(row[1], user.password), row[2])
                return user
            else:
                return None
        except Exception as ex:
            raise Exception(ex)

    @classmethod
    def get_by_id(self, id):
        try:
            db = oracle.connection('stock', 'stock')
            cursor = db.cursor()
            sql = "SELECT  USUARIO_ORACLE, NOMBRE, APELLIDO1 FROM USUARIO WHERE USUARIO_ORACLE = '{}'".format(id)
            cursor.execute(sql)
            row = cursor.fetchone()
            if row != None:
                return User(row[0], None, row[2] + " " + row[1])
            else:
                return None
        except Exception as ex:
            raise Exception(ex)