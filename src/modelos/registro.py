from enum import Enum

# Clase Registro

class TipoRegistro(Enum):
    DONACION = "Donacion"
    SOLICITUD = "Solicitud"

class TipoSangre(Enum):
    AB_POS = "AB+"
    AB_NEG = "AB-"
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    O_POS = "O+"
    O_NEG = "O-"

class Registro:
    def __init__(self, id_registro: int, tipo_registro: TipoRegistro, tipo_sangre: TipoSangre, cantidad: int, 
                 razon: str, comentarios: str, prioridad: int, estado: str, fecha: str, usuario_documento: str, usuario_tipo_documento: str):
        self.id = id_registro
        self.tipo_registro = tipo_registro
        self.tipo_sangre = tipo_sangre
        self.cantidad = cantidad
        self.razon = razon
        self.comentarios = comentarios
        self.prioridad = prioridad  # está entre 1 y 5 como el TRIAGE
        self.estado = estado
        self.fecha = fecha
        self.usuario_documento = usuario_documento
        self.usuario_tipo_documento = usuario_tipo_documento