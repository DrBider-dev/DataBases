from dataclasses import dataclass
from typing import Optional

@dataclass
class Persona:
    id_persona: int
    primer_nombre: str
    primer_apellido: str
    email: str
    segundo_nombre: Optional[str] = None
    segundo_apellido: Optional[str] = None
    calle: Optional[str] = None
    carrera: Optional[str] = None
    numero: Optional[str] = None

@dataclass
class Telefono:
    id_telefono: Optional[int]
    id_persona: int
    telefono: str

@dataclass
class Cliente:
    id_persona: int

@dataclass
class Empleado:
    id_persona: int
    cargo: str
    area: str

@dataclass
class Habitacion:
    numero_h: int
    tipo: str
    estado: str
    precio_noche: float

@dataclass
class Reserva:
    id_reserva: Optional[int]
    id_cliente: int
    numero_h: int
    fecha_llegada: str
    fecha_salida: str
    valor_reserva: float
    tiempo_maxc: int

@dataclass
class Servicio:
    id_servicio: Optional[int]
    nombre: str
    descripcion: str
    costo: float
    estado: str

@dataclass
class Consumo:
    id_consumo: Optional[int]
    id_reserva: int
    id_servicio: int
    fecha_hora: str