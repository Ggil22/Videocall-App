import socket
import practica3_client
import sys
from videocall_client import VideoCallClient

OK = 1
ERROR = -1
NO_CONECTADO = -2
TAM = 2048

"""
    ********
    * FUNCIÓN: def llamar(gui, usuario)
    * ARGS_IN: gui gui - gui de la aplicacion
    * ARGS_IN: usuario usuario - usuario destino al que se le quiere llamar.
    * DESCRIPCIÓN: Funcion que crea la videollamada y hace de union entre el cliente 
    * principal y el cliente de videollamada.
    ********
    """
def llamar(gui, usuario):
    # Inicia el cliente de la videollamada
    print("Estabbleciendo llamada.")
    call = VideoCallClient(gui, usuario)
    call.start(usuario)
    print("Ok")
    return OK