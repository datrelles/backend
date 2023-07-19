# Inicializando la app 
 El proyecto esta desarrollado al 100% en Python en su version 3.10. Se requiere crear un ambiente de python luego de clonar
 el repositorio e instalar las librerias necesarias para la correcta ejecucion del proyecto.

## Configuracion inicial
 Se requiere editar o crear el archivo .env ubicado en la raiz del proyecto, dentro de este archivo se encuentran todas las variables 
 de entorno (Conexiones a DB, Integracion con Terceros, Claves de Seguridad, etc) dichas variables dependen del equipo en el 
 cual se vaya a ejecutar la app.

## Activacion del ambiente de python
 Para el despliegue de la app se requeire previamente la activacion del ambiente en el cual vaya a ejecutarse el proyecto. Este comando 
 dependera del SO del equipo. Para linux es el siguiente:

### source /<ubicacion_del_repo>/src/<nombre_ambiente>/bin/activate

## Ejecucion de la app

Para poner en marcha el proyecto, situandose en la ubicacion del repositorio, se ejecuta el comando, en este caso se ejecuta en background
para mantener siempre activa la app.

### nohup flask run -h 0.0.0.0 &

La app se ejecutara por defecto en el localhost en el puerto 5000

Para verificar logs y estados del servicio se puede leer el archivo nohup.out que se encuentra en el repositorio.
