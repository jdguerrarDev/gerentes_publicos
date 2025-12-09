from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ============================================
# COMPROMISOS
# ============================================
class CompromisoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    peso_porcentual: float
    estado: bool

    class Config:
        from_attributes = True


# ============================================
# ACCIONES
# ============================================
class AccionResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    obligatorio: bool
    peso_fijo: Optional[float]
    estado: bool

    class Config:
        from_attributes = True


class AccionSeleccionRequest(BaseModel):
    id_accion: int
    peso_porcentual_usuario: float


class AccionSeleccionResponse(BaseModel):
    id: int
    id_accion: int
    peso_porcentual_usuario: float
    accion: AccionResponse
    estado: bool

    class Config:
        from_attributes = True


# ============================================
# ACCIONES DE INNOVACIÓN
# ============================================
class AccionInnovacionRequest(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    peso_porcentual_usuario: float
    evidencias: Optional[str] = None


class AccionInnovacionResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    peso_porcentual_usuario: float
    evidencias: Optional[str]
    estado: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ============================================
# USUARIO COMPROMISO ASIGNACIÓN
# ============================================
class UsuarioCompromisoAsignacionResponse(BaseModel):
    id: int
    id_usuario: int
    id_rol: int
    id_regional: Optional[int]
    id_centro: Optional[int]
    id_compromiso: int
    estado: bool
    compromiso: CompromisoResponse

    class Config:
        from_attributes = True


# ============================================
# VALIDACIÓN DE PESOS
# ============================================
class ValidacionPesosResponse(BaseModel):
    compromiso_id: int
    compromiso_nombre: str
    total_acciones: int
    suma_pesos: float
    peso_real_en_total: float
    es_valido: bool
    mensaje: str

    class Config:
        from_attributes = True


# ============================================
# ESTADÍSTICAS
# ============================================
class EstadisticasRolesResponse(BaseModel):
    subdirectores_centro: int
    directores_regional: int
    total: int


# ============================================
# AUTENTICACIÓN
# ============================================
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    usuario_id: int
    email: str
    roles: List[str]


# ============================================
# RESUMEN DE USUARIO
# ============================================
class AccionResumenResponse(BaseModel):
    id: int
    nombre: str
    peso_porcentual_usuario: float

    class Config:
        from_attributes = True


class CompromisoResumenResponse(BaseModel):
    id: int
    nombre: str
    peso_porcentual: float
    acciones_seleccionadas: List[AccionResumenResponse]
    suma_pesos: float
    estado_completo: bool

    class Config:
        from_attributes = True


class UsuarioResumenResponse(BaseModel):
    id: int
    nombre: str  # Usa email del usuario
    email: str
    rol: str
    regional: Optional[str]
    centro: Optional[str]
    compromisos: List[CompromisoResumenResponse]

    class Config:
        from_attributes = True
