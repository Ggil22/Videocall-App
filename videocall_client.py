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

OK = 1
ERROR = -1

"""
********
* FUNCIÓN: class VideoCallClient(object)
* ARGS_IN: object object - Resolucion
* DESCRIPCIÓN: Clase con la que se creara el cliente de la llamada.
********
"""
class VideoCallClient(object):
    """
    ********
    * FUNCIÓN: def __init__(self, window_size)
    * ARGS_IN: self self - gui de la aplicacion
    * ARGS_IN: gui gui - gui de la aplicacion principal
    * ARGS_IN: usuario_destino usuario_destino - usuario destino de la llamada
    * DESCRIPCIÓN: Funcion que inicializa las variables de la ventana de la llamada.
    ********
    """
    def __init__(self, gui, usuario_destino):
        self.userDest = usuario_destino
        self.app = gui.app
        self.app.conexion = True
        try:
            # Iniciamos la llamada
            self.app.startSubWindow("Llamada")
            self.app.setSize("640x600")
            # Preparación del interfaz
            self.app.addLabel("title llamada", "Llamada con " + self.userDest[0])
            self.app.setLabelBg("title llamada", "black")
            self.app.getLabelWidget("title llamada").config(font=("Sans Serif", "20", "bold"))
            self.app.setBg("black")
            self.app.setFg("white")

            #Sección del emisor
            self.app.addLabel("ORIGEN", "You are: " + self.app.sesionUser[0])
            self.app.addImage("videoCall", "imgs/user.gif")
            self.app.setLabelFg("ORIGEN", "white")
            self.app.setLabelBg("ORIGEN", "black")
            #Seccion del receptor.
            self.app.addLabel("DESTINO", "You are calling: " + self.userDest[0])
            self.app.setLabelFg("DESTINO", "white")
            self.app.setLabelBg("DESTINO", "black")
            self.app.addImage("videoRecive", "imgs/user.gif")
            #ajustamos Tamaños
            self.app.setImageSize("videoCall", 400,260)
            self.app.setImageSize("videoRecive", 400,260)

            # Obtenemos los datos de la camara web.
            try:
                self.frame = cv2.VideoCapture(0)
            except:
                self.errorBox("CAMARA", "No se encuentra la camara.")
            # Para cambiar la frecuencia, http://appjar.info/pythonLoopsAndSleeps/
            self.app.setPollTime(20)
            # Añadir los botones
            self.app.addButtons(["Colgar", "Pausar", "Continuar", "Camara"], self.buttonsCallback)
            self.app.hideButton("Continuar")
            self.app.hideButton("Camara")
            self.app.stopSubWindow()
        except:
            try:
                self.frame = cv2.VideoCapture(0)
            except:
                self.app.errorBox("ERROR", "No camara")

            self.app.setLabel("ORIGEN", "You are: " + self.app.sesionUser[0])
            self.app.setLabel("title llamada", "Llamada con " + self.userDest[0])
            self.app.setLabel("DESTINO", "You are calling: " + self.userDest[0])

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
        if button == "Colgar":
            self.colgar()
        elif button == "Pausar":
            self.pausa()
        elif button == "Continuar":
            self.continuar()
        elif button == "Camara":
            self.camara()

###############################################################################################################
################################################FUNCIONALIDAD##################################################
###############################################################################################################
    """
    ********
    * FUNCIÓN: def start(self, usuario_destino)
    * ARGS_IN: self self - gui de la aplicacion
    * ARGS_IN: usuario usuario_destino - usuario destino al que se le quiere llamar.
    * DESCRIPCIÓN: Funcion que inicia la videollamada y crea los hilos del emisor y receptor.
    ********
    """
    def start(self, usuario_destino):
        self.app.showSubWindow("Llamada")
        # Obtenemos la direccion del socket tcp
        self.userDest = usuario_destino
        self.urlTCP = (usuario_destino[1], int(usuario_destino[2]))
        # Para futuras llamadas dejamos en oculto el boton de camara
        try:
            self.frame = cv2.VideoCapture(0)
            self.app.hideButton("Camara")
        except:
            try:
                self.app.hideButton("Camara")
            except:
                time.sleep(0.001)
        # Hilo creado para la emision
        threadOut = threading.Thread(target = self.sendUDP, args=(), daemon = False)
        threadOut.start()
        # Hilo creado para la recepcion
        threadIn = threading.Thread(target = self.reciveUDP, args=(), daemon = False)
        threadIn.start()
    
    def colgar(self):
        print("Finalizando videollamada.")
        # Antes de finalizar la videollamada, hay que enviar al usuario destino que se termina la llamada.
        '''self.socketTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketTCP.connect(self.urlTCP)
        message = "CALL_END " + self.app.sesionUser[0]
        # Realizamos una conexion con el usuario destino
        try:
            self.socketTCP.sendall(message.encode())
        except:
            print("Err: Fallo al enviar el mensaje.")
        # Para futuras llamadas se oculta el boton de camara y la camara como predeterminada.
        try:
            self.frame = cv2.VideoCapture(0)
            self.app.hideButton("Camara")
        except:
            try:
                self.app.hideButton("Camara")
            except:
                time.sleep(0.001)'''
        # Cerramos el cliente de la videollamada.
        self.app.hideSubWindow("Llamada")
        self.app.connection = False
        self.socketTCP.close()
        self.app.infoBox("Llamada", "Finalizando videollamada.")
        print("Ok")
    
    def pausa(self):
        return OK

    def continuar(self):
        return OK

    def camara(self):
        return OK