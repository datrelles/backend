from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from src import oracle

import datetime
import requests
from requests.auth import HTTPBasicAuth
from os import getenv
class User(UserMixin):

    def __init__(self, username, password, fullname="") -> None:
        self.id = username
        self.username = username
        self.password = password
        self.fullname = fullname

    @classmethod
    def check_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)


print(generate_password_hash('*******'))

# ########################################################################################################
# inicio = datetime.date(2023, 1, 1)
# fin = datetime.date(2024, 1, 9)
#
# # Definir la duración de una semana
# duracion_semana = datetime.timedelta(days=6)
#
# # Bucle para recorrer las semanas
# fecha_actual = inicio
# while fecha_actual <= fin:
#     primer_dia_semana = fecha_actual.strftime("%Y-%m-%d")
#     ultimo_dia_semana = fecha_actual + duracion_semana
#     ultimo_dia_semana = ultimo_dia_semana.strftime("%Y-%m-%d")
#     response = requests.get(
#         "https://api.jelou.ai/v1/company/405/reports/147/rows?startAt="+primer_dia_semana+"T00:00:01.007-05:00&endAt="+ultimo_dia_semana+"T23:59:59.007-05:00&limit=500&page=1",
#         auth=HTTPBasicAuth("pGaKaVkHVe7Xc1oOP7tXARxdECsknSbt", "gJjzyBGGpdHKQLOoFg9pcVlUoq9fO0xhEN7EpYUylqBC1DSMlyK59DI6Q6O6HuCQ"))
#     data = response.json()
#     rows = data['rows']
#     c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
#     cursor = c.cursor()
#
#     for row in rows:
#         cod_produc = row["codProduc"]
#         cod_motor = row["codMotor"]
#         cod_chasis = row["codChasis"]
#         cpn = row["cpn"]
#         year = row["year"]
#         color = row["color"]
#         cylindrage = row["cylindrage"]
#         tonnage = row["tonnage"]
#         passangers = row["passangers"]
#         model = row["model"]
#         clase = row["class"]
#         subclass = row["subclass"]
#         plate = row["plate"]
#         name = row["name"]
#         legal_id = row["legalId"]
#         vehicle_use = row["vehicleUse"]
#         warranty = row["warranty"]
#         fecha_crea = row["createdAt"]
#         fecha_mod = row["updatedAt"]
#         restriction = row["restriction"]
#         telefono = row.get("telefono", None)
#         empresa = '20'
#
#         query = "INSERT INTO STOCK.ST_WS_GARANTIAS (cod_produc, cod_motor, cod_chasis, cpn, year, color, cylindrage, tonnage, passangers, model, class, subclass, plate, name, legal_id, vehicle_use, warranty, fecha_crea, fecha_mod, restriction, telefono, empresa) VALUES (:cod_produc, :cod_motor, :cod_chasis, :cpn, :year, :color, :cylindrage, :tonnage, :passangers, :model, :class, :subclass, :plate, :name, :legal_id, :vehicle_use, :warranty, TO_DATE(:fecha_crea, 'DD/MM/YYYY HH24:MI'), TO_DATE(:fecha_mod, 'DD/MM/YYYY HH24:MI'), :restriction, :telefono, :empresa)"
#         try:
#             cursor.execute(query, {
#                 "cod_produc": cod_produc.upper(),
#                 "cod_motor": cod_motor.upper(),
#                 "cod_chasis": cod_chasis.upper(),
#                 "cpn": cpn.upper(),
#                 "year": year,
#                 "color": color.upper(),
#                 "cylindrage": cylindrage.upper(),
#                 "tonnage": tonnage,
#                 "passangers": passangers,
#                 "model": model.upper(),
#                 "class": clase.upper(),
#                 "subclass": subclass.upper(),
#                 "plate": plate.upper(),
#                 "name": name.upper(),
#                 "legal_id": legal_id.upper(),
#                 "vehicle_use": vehicle_use.upper(),
#                 "warranty": warranty.upper(),
#                 "fecha_crea": fecha_crea,
#                 "fecha_mod": fecha_mod,
#                 "restriction": restriction.upper(),
#                 "telefono": telefono,
#                 "empresa": empresa
#             })
#             c.commit()
#
#         except c.Error as error:
#             print("Error inserting row ", name, " ", fecha_crea, " :", error)
#     c.close()
#
#     # Actualizar la fecha actual para la próxima iteración
#     fecha_actual += datetime.timedelta(days=7)
#
# ########################################################################################################################################################
#
# inicio = datetime.date(2023, 1, 1)
# fin = datetime.date(2024, 1, 9)
#
# # Definir la duración de una semana
# duracion_semana = datetime.timedelta(days=6)
#
# # Bucle para recorrer las semanas
# fecha_actual = inicio
# while fecha_actual <= fin:
#     primer_dia_semana = fecha_actual.strftime("%Y-%m-%d")
#     ultimo_dia_semana = fecha_actual + duracion_semana
#     ultimo_dia_semana = ultimo_dia_semana.strftime("%Y-%m-%d")
#     response = requests.get(
#         "https://api.jelou.ai/v1/company/405/reports/137/rows?startAt="+primer_dia_semana+"T00:00:01.007-05:00&endAt="+ultimo_dia_semana+"T23:59:59.007-05:00&limit=500&page=1",
#         auth=HTTPBasicAuth("pGaKaVkHVe7Xc1oOP7tXARxdECsknSbt", "gJjzyBGGpdHKQLOoFg9pcVlUoq9fO0xhEN7EpYUylqBC1DSMlyK59DI6Q6O6HuCQ"))
#     data = response.json()
#     rows = data['rows']
#     c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
#     cursor = c.cursor()
#
#     for row in rows:
#         user_id = int(row["userId"])
#         full_name = row["fullName"]
#         city = row["city"]
#         phone = row.get("phone", "")
#         trademark = row.get("trademark", " ")
#         model = row.get("model", None)
#         color = row.get("color", None)
#         detail = row.get("detail", None)
#         status = row.get("status", " ")
#         observation = row.get("observation", " ")
#         fecha_crea = row["createdAt"]
#         fecha_mod = row["updatedAt"]
#         empresa = '20'
#
#         query = "INSERT INTO ST_WS_REPUESTOS (user_id, full_name, city, phone, trademark, model, color, detail, status, observation, fecha_crea, fecha_mod, empresa ) VALUES (:user_id, :full_name, :city, :phone, :trademark, :model, :color, :detail, :status, :observation, TO_DATE(:fecha_crea, 'DD/MM/YYYY HH24:MI'), TO_DATE(:fecha_mod, 'DD/MM/YYYY HH24:MI'), :empresa)"
#
#         try:
#             cursor.execute(query, {
#                 "user_id": user_id,
#                 "full_name": full_name.upper(),
#                 "city": city.upper(),
#                 "phone": phone,
#                 "trademark": trademark.upper(),
#                 "model": model.upper(),
#                 "color": color.upper(),
#                 "detail": detail.upper(),
#                 "status": status.upper(),
#                 "observation": observation.upper(),
#                 "fecha_crea": fecha_crea,
#                 "fecha_mod": fecha_mod,
#                 "empresa": empresa,
#             })
#             c.commit()
#
#         except c.Error as error:
#             print("Error inserting row ", user_id, " ", fecha_crea, " :", error)
#     c.close()
#
#     # Actualizar la fecha actual para la próxima iteración
#     fecha_actual += datetime.timedelta(days=7)

########################################################################################################################################################
#
# inicio = datetime.date(2023, 1, 1)
# fin = datetime.date(2024, 1, 9)
#
# # Definir la duración de una semana
# duracion_semana = datetime.timedelta(days=6)
#
# # Bucle para recorrer las semanas
# fecha_actual = inicio
# while fecha_actual <= fin:
#     primer_dia_semana = fecha_actual.strftime("%Y-%m-%d")
#     ultimo_dia_semana = fecha_actual + duracion_semana
#     ultimo_dia_semana = ultimo_dia_semana.strftime("%Y-%m-%d")
#     response = requests.get(
#         "https://api.jelou.ai/v1/company/405/reports/145/rows?startAt="+primer_dia_semana+"T00:00:01.007-05:00&endAt="+ultimo_dia_semana+"T23:59:59.007-05:00&limit=500&page=1",
#         auth=HTTPBasicAuth("pGaKaVkHVe7Xc1oOP7tXARxdECsknSbt", "gJjzyBGGpdHKQLOoFg9pcVlUoq9fO0xhEN7EpYUylqBC1DSMlyK59DI6Q6O6HuCQ"))
#     data = response.json()
#     rows = data['rows']
#     c = oracle.connection(getenv("USERORA"), getenv("PASSWORD"))
#     cursor = c.cursor()
#
#     for row in rows:
#         codigo_taller = int(row["codigoTaller"])
#         mantenimiento_prox = int(row["mantenimientoProx"])
#         nombre_mantenimiento = row["nombreMantenimiento"]
#         nombre_garantia = row["nombreGarantia"]
#         nombre_taller = row.get("nombreTaller", " ")
#         telefono_garantia = row.get("telefonoGarantia", None)
#         chasis = row["chasis"]
#         mantenimiento_actual = int(row["mantenimientoActual"])
#         placa = row["placa"]
#         legal_id = row["legalId"]
#         created_at = row["createdAt"]
#         updated_at = row["updatedAt"]
#         empresa = '20'
#
#         query = "INSERT INTO ST_WS_MANTENIMIENTOS (codigo_taller, mantenimiento_prox, nombre_mantenimiento, nombre_garantia, chasis, mantenimiento_actual, placa, legal_id, fecha_crea, fecha_mod, empresa, nombre_taller, telefono_garantia) VALUES (:codigo_taller, :mantenimiento_prox, :nombre_mantenimiento, :nombre_garantia, :chasis, :mantenimiento_actual, :placa, :legal_id, TO_DATE(:created_at, 'DD/MM/YYYY HH24:MI'), TO_DATE(:updated_at, 'DD/MM/YYYY HH24:MI'), :empresa, :nombre_taller, :telefono_garantia)"
#
#         try:
#             cursor.execute(query, {
#             "codigo_taller": codigo_taller,
#             "mantenimiento_prox": mantenimiento_prox,
#             "nombre_mantenimiento": nombre_mantenimiento.upper(),
#             "nombre_garantia": nombre_garantia.upper(),
#             "chasis": chasis.upper(),
#             "mantenimiento_actual": mantenimiento_actual,
#             "placa": placa.upper(),
#             "legal_id": legal_id.upper(),
#             "created_at": created_at,
#             "updated_at": updated_at,
#             "empresa": empresa,
#             "nombre_taller": nombre_taller.upper(),
#             "telefono_garantia": telefono_garantia
#         })
#             c.commit()
#
#         except c.Error as error:
#             print("Error inserting row ", codigo_taller, " ", created_at, " :",error)
#     c.close()
#
#     # Actualizar la fecha actual para la próxima iteración
#     fecha_actual += datetime.timedelta(days=7)
