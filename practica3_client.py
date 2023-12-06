# import the library
from appJar import gui
from PIL import Image, ImageTk
import numpy as np
import cv2
import socket
import sys
from requests import get
import requests
import threading
import conexion

OK = 1
ERROR = -1
TAM = 2048
URL = ("vega.ii.uam.es", 8000)
VERSION = "V1#V2"
NO_CONECTADO = -2

"""
********
* FUNCIÓN: def __init__(self, window_size)
* ARGS_IN: object object - Resolucion
* DESCRIPCIÓN: Clase con la que se creara el cliente.
********
"""
class VideoClient(object):
    """
    ********
    * FUNCIÓN: def __init__(self, window_size)
    * ARGS_IN: self self - gui de la aplicacion
    * ARGS_IN: window_size window_size - Tamaño de la ventana
    * DESCRIPCIÓN: Funcion que inicializa las variables de la ventana.
    ********
    """
    def __init__(self, window_size):

        # Creamos una variable que contenga el GUI principal
        self.app = gui("Redes2 - P2P", window_size)
        self.app.setGuiPadding(10,10)
        self.sesionUser = []
        # Para el cambio de colores hemos buscado infromacion en:
        # http://appjar.info/pythonWidgetOptions/
        # http://appjar.info/pythonGuiOptions/
        # http://appjar.info/outputWidgets/
        # http://appjar.info/pythonBasics/#colour-map
        self.app.setBg("black")
        self.app.setFg("white")
        # Icono de la aplicacion obtenido de:
        # https://www.flaticon.es/icono-gratis/hangouts-se-encuentran_2965309
        self.app.setIcon("imgs/portada.gif")
        # Screen de registro
        self.app.startSubWindow("Login", modal=True)
        self.app.setFg("black")
        self.app.addLabelEntry("Nombre:")
        self.app.addLabelEntry("Puerto TCP:")
        self.app.addLabelEntry("Puerto UDP:")
        self.app.addLabelSecretEntry("Contraseña:")
        self.app.addButtons(["Aceptar", "Cancelar"], self.login)
        self.app.stopSubWindow()
        # Preparación del interfaz
        self.app.addLabel("title", "Cliente Multimedia P2P - Redes2 ")
        self.app.getLabelWidget("title").config(font=("Sans Serif", "20", "bold"))
        # Imagen de la aplicacion
        # El gif lo hemos obtenido a traves de esta pagina:
        # https://www.pinterest.es/pin/173740498113461700/
        self.app.addImage("video", "imgs/portada.gif")
        self.app.setImageSize("video", 500, 350)
        # Añadir los botones
        self.app.addButtons(["Iniciar Sesion", "Cerrar sesion"], self.buttonsCallback, 2)
        self.app.hideButton("Cerrar sesion")
        self.app.addButtons(["Conectar", "Listar Usuarios", "Info usuario", "Salir"], self.buttonsCallback)
        self.app.hideButton("Conectar")
        # Barra de estado
        # Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
        self.app.addStatusbar(fields=2)

    """
    ********
    * FUNCIÓN: def start(self)
    * ARGS_IN: self self - gui de la aplicacion
    * DESCRIPCIÓN: Funcion que la aplicacion.
    ********
    """
    def start(self):
        self.app.go()

###############################################################################################################
###################################################BOTONES#####################################################
###############################################################################################################
    """
    ********
    * FUNCIÓN: def buttonsCallback(self, button) 
    * ARGS_IN: self self - gui de la aplicacion
    * ARGS_IN: string button - boton que se selecciona en las ventanas.
    * DESCRIPCIÓN: Funcion que da funcionalidad a los botones.
    ********
    """
    def buttonsCallback(self, button):
        #INFO: Boton que sale de la aplicacion.
        if button == "Salir":
            # Salimos de la aplicación
            control_quit = quit()
            if control_quit is ERROR:
                print("Err: Fallo en el quit.")
            else:
                print("Salida correcta.")
            self.app.stop()
        #INFO: Boton que inicia sesion.
        elif button == "Iniciar Sesion":
            self.app.showSubWindow("Login")
        #INFO: Boton que cierra sesion.
        elif button == "Cerrar sesion":
            # Cerramos el hilo de escucha
            self.logout()
        #INFO: Boton que lista usuarios.
        elif button == "Listar Usuarios":
            # Procedemos a realizar la lista de los usuarios de la aplicacion
            self.lists()
        #INFO: Boton que da informacion del usuario.
        elif button == "Info usuario":
            self.info_users()
        #INFO: Boton que realiza la llamada.
        elif button == "Conectar":
            self.conectar()

###############################################################################################################
############################################FUNCIONALIDAD_BOTONES##############################################
###############################################################################################################
    """
    ********
    * FUNCIÓN: def login (self, button)
    * ARGS_IN: self self - gui de la aplicacion
    * ARGS_IN: string button - boton que se selecciona en las ventanas.
    * DESCRIPCIÓN: Funcion que da inicia sesion en el servidor o registra.
    ********
    """
    def login (self, button):
        if button != "Aceptar":
            self.app.hideSubWindow("Login")
        else:
            # Recogemos el nombre de usuario
            nombre = self.app.getEntry("Nombre:")
            # Recogemos los puertos que se quieren utilizar
            tcp = self.app.getEntry("Puerto TCP:")
            udp = self.app.getEntry("Puerto UDP:")
            # Recogemos contrasena
            contrasena = self.app.getEntry("Contraseña:")
            # Control de errores de login
            if nombre is None or contrasena is None or tcp is None or udp is None:
                self.app.warningBox("ERROR", "Rellene todos los campos.", parent="None")
            elif udp == tcp:
                self.app.warningBox("ERROR", "Puertos TCP y UDP identicos.", parent="Login")
            # Registramos
            else:
                control_registro = register(nombre, tcp, contrasena, VERSION)
                # Control de errores para registrarse.
                # Creamos hilo socket para recibir peticiones a traves de IP
                if control_registro is OK:
                    # EN caso de que el registro se haya realizado correctamente, 
                    # realizamos la consulta y añadimos al objeto del usuario el 
                    # puerto UDP.
                    user = query(nombre)
                    user.append(udp)
                    # Añadimos a la aplicacion el usuario
                    self.app.sesionUser = user
                    # Para recibir peticiones, creamos un hilo
                    # TODO: Descomentar cuando esten implementadas las llamadas
                    '''self.listenThread = threading.Thread(target = conexion.connect, args=(self,), daemon = None)
                    self.listenThread.start()'''
                    self.app.infoBox("Inicio sesion", "Se ha iniciado sesion correctamente.")
                    # Funcion de la interfaz
                    self.app.hideButton("Iniciar Sesion")
                    self.app.showButton("Cerrar sesion")
                    self.app.showButton("Conectar")
                    self.app.hideSubWindow("Login")
                else:
                    self.app.warningBox("ERROR", "Error en el registro del usuario.", parent="Login")

    """
    ********
    * FUNCIÓN: def logout ()
    * DESCRIPCIÓN: Funcion que cierra sesion, cerrando las conexiones con el socket.
    ********
    """
    def logout(self):
        self.app.hideButton("Cerrar sesion")
        self.app.hideButton("Conectar")
        self.app.showButton("Iniciar Sesion")
        # TODO: quitar comentarios cuando se pueda hacer conexiones
        '''urlUser = (self.app.sesionUser[1], int(self.app.sesionUser[2]))
        kill = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        kill.connect(urlUser)
        msg = "KILL_THREAD"
        kill.sendall(msg.encode())
        self.sesionUser = []'''
        control_quit = quit()
        if control_quit is ERROR:
            self.app.warningBox("ERROR", "No se ha podido cerrar sesion.", parent="None")
            print("Err: Fallo en el quit.")
        else:
            self.app.infoBox("Cerrar sesion", "Se ha cerrado sesion correctamente.", parent="None")
            print("Salida correcta.")

    """
    ********
    * FUNCIÓN: def lists()
    * DESCRIPCIÓN: Funcion que lista usuarios.
    ********
    """
    def lists(self):
        # Llamamos a la funcion para pedir informacion al servidor
        u = list_users()
        # Creamos un apartado de pestaña donde te enseña el listado de usuarios
        if u is not None:
            try:
                self.app.removeLabel("Info")
                try:
                    self.app.addOptionBox("Lista de usuarios", u)
                    self.app.setLabelBg("Lista de usuarios", "white")
                    
                except:
                    self.app.changeOptionBox("Lista de usuarios", u)
            except:
                try:
                    self.app.addOptionBox("Lista de usuarios", u)
                    self.app.setLabelBg("Lista de usuarios", "white")
                except:
                    self.app.changeOptionBox("Lista de usuarios", u)
        else:
            self.app.errorBox("ERROR", "Todava no hay usuarios registrados.")

    """
    ********
    * FUNCIÓN: def lists()
    * DESCRIPCIÓN: Funcion que da informacion del usuario a buscar.
    ********
    """
    def info_users(self):
        # Creamos una ventana auxiliar para que se introduzaca el nombre
            nombre = self.app.textBox("Info usuario", "Nombre del usuario")
            if nombre is not None:
                consulta = query(nombre)
                if consulta == ERROR:
                    self.app.errorBox("ERROR", "Usuario no encontrado.")
                else:
                    # SUprimimos la lista de usuarios para que no se sobrecargue la aplicaicon.
                    try:
                        try:
                            self.app.addLabel("Info", "Nombre:" + consulta[0] + "/IP:" + consulta[1] + "/Puerto:" + consulta[2])
                        except:
                            self.app.setLabel("Info", "Nombre:" + consulta[0] + "/IP:" + consulta[1] + "/Puerto:" + consulta[2])
                    except:
                        try:
                            self.app.addLabel("Info", "Nombre:" + consulta[0] + "/IP:" + consulta[1] + "/Puerto:" + consulta[2])
                        except:
                            self.app.setLabel("Info", "Nombre:" + consulta[0] + "/IP:" + consulta[1] + "/Puerto:" + consulta[2])
    """
    ********
    * FUNCIÓN: def conectar(self)
    * DESCRIPCIÓN: Funcion que conecta con la llamada.
    ********
    """
    def conectar(self):
            nombre = self.app.textBox("Info usuario", "Nombre del usuario")
            if nombre is not None:
                consulta = query(nombre)
                if consulta == ERROR:
                    self.app.errorBox("ERROR", "Usuario no encontrado.")
                else:
                    print("Llamada realizado con: " + consulta[0] + "...")
                    call = conexion.llamar(self, consulta)
                    if call is OK:
                        print("Ok")
                    elif call is NO_CONECTADO:
                        self.app.errorBox("Usuario conectado", "Usuario no conectado.")
                        print("Err: usuario no conectado")
                    else:
                        print("Err: Error al llamar")

###############################################################################################################
###############################################GESTION_USUARIO#################################################
###############################################################################################################
"""
********
* FUNCIÓN: def register(nombre, puerto, contrasena, version)
* ARGS_IN: string nombre - Nombre del usuario a registrar
* ARGS_IN: string puerto - puerto del usuario tcp
* ARGS_IN: string contrasena - Contrasena del usuario secreta
* ARGS_IN: string version - Version en la que se encuentra el usuario
* ARGS_OUT: ERROR cuando se produce un error y OK cuando se realiza correctamente.
* DESCRIPCIÓN: Funcion que registra al usuario en el servidor.
*****
"""
def register(nombre, puerto, contrasena, version):
    print("Procediendo al registro de usuario.")
    # Comprobacion de argumentos
    if puerto is None or len(puerto) != 4:
        print("Err: Error al pasar el puerto")
        return ERROR
    if nombre is None:
        print("Err: Error al pasar el nombre")
        return ERROR
    if contrasena is None:
        print("Err: Error al pasar la contrasena")
        return ERROR
    # Mensaje de la peticion al servidor
    msg = 'REGISTER ' + nombre + ' ' + getPublicIP() + ' ' + puerto + ' ' + contrasena + ' ' + version
    # COnectamos con el servidor y enviamos la consulta
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(URL)
    server.sendall(msg.encode())
    # Respuesta del servidor
    respuesta = server.recv(TAM)
    if respuesta.decode() == "NOK WRONG_PASS":
        print("Err: El nick es válido, pero la contraseña proporcionada es errónea")
        return ERROR
    else:
        print("Ok")
        return OK

"""
********
* FUNCIÓN: def query(nombre)
* ARGS_IN: string nombre - Nombre del usuario a consultar
* ARGS_OUT: ERROR cuando se produce un error y consulta cuando se realiza correctamente.
* DESCRIPCIÓN: Funcion que consulta un usuario en el servidor.
*****
"""
def query(nombre):
    print("Informacion del usuario " + nombre + '.')
    # Comprobamos los argumentos
    if nombre is None:
        print("Err: Error al pasar el nombre")
        return ERROR
    # Mensaje de la peticion al servidor
    msg = 'QUERY ' + nombre
    # COnectamos con el servidor y enviamos la consulta
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(URL)
    server.sendall(msg.encode())
    # Respuesta del servidor
    respuesta = server.recv(TAM)
    if respuesta.decode() == "NOK USER_UNKNOWN":
        print("Err: Usuario desconocido.")
        return ERROR
    else:
        user = respuesta.decode().split(' ')[2]
        ip = respuesta.decode().split(' ')[3]
        puerto = respuesta.decode().split(' ')[4]
        version = respuesta.decode().split(' ')[5]
        # Crea la lista de usuarios
        consulta = []
        consulta.append(user)
        consulta.append(ip)
        consulta.append(puerto)
        print("Ok")
        return consulta

"""
********
* FUNCIÓN: def list_users()
* ARGS_OUT: ERROR cuando se produce un error y users_aux lista de usuarios cuando se realiza correctamente.
* DESCRIPCIÓN: Funcion que devuelve una lista de usuarios.
*****
"""
def list_users():
    print("Listas de usuarios.")
    # Mensaje de la peticion al servidor
    msg = 'LIST_USERS'
    # COnectamos con el servidor y enviamos la consulta
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(URL)
    server.sendall(msg.encode())
    # Respuesta del servidor
    respuesta = server.recv(TAM)
    if respuesta.decode() == "NOK USER_UNKNOWN":
        print("Err: Usuario desconocido.")
        return ERROR
    else:
        num = len(respuesta.decode().split(' ')[2])
        users = respuesta.decode()[15+num:]
        users_aux = []
        for u in users.split('#'):
            users_aux.append(u.split(' ')[0])
        print("Ok")
        return users_aux

"""
********
* FUNCIÓN: def quit()
* ARGS_OUT: ERROR cuando se produce un error y OK cuando se realiza correctamente.
* DESCRIPCIÓN: Funcion que se desconecta del servidor.
*****
"""
def quit():
    print("Desconectandose.")
    # Mensaje de la peticion al servidor
    msg = 'QUIT'
    # COnectamos con el servidor y enviamos la consulta
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect(URL)
    server.sendall(msg.encode())
    # Respuesta del servidor
    respuesta = server.recv(TAM)
    if respuesta.decode() == "BYE":
        print("Ok")
        return OK
    else:
        print("Err: Fallo en la desconexion")
        return ERROR

"""
********
* FUNCIÓN: def getPublicIP()
* ARGS_OUT: ip.text - ip del ordenador
* DESCRIPCIÓN: Funcion que devuelve la ip del ordenador donde se encuentra.
*****
"""
def getPublicIP():
    ip = requests.get('https://ifconfig.me/')
    print("IP publica: " + ip.text)
    return ip.text

if __name__ == '__main__':
    vc = VideoClient("640x520")
    vc.start()