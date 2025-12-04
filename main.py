from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from config import get_db
from schemas import (
    CompromisoResponse,
    AccionResponse,
    AccionSeleccionRequest,
    AccionSeleccionResponse,
    AccionInnovacionRequest,
    AccionInnovacionResponse,
    UsuarioCompromisoAsignacionResponse,
    ValidacionPesosResponse
)

app = FastAPI(
    title="API Compromisos y Acciones",
    description="API para gestión de compromisos, acciones y evaluación de desempeño",
    version="0.1.0"
)

# ============================================
# ENDPOINTS - COMPROMISOS
# ============================================

@app.get("/api/v1/usuarios/{usuario_id}/compromisos", response_model=List[UsuarioCompromisoAsignacionResponse])
async def get_compromisos_usuario(usuario_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener todos los compromisos asignados a un usuario"""
    query = """
    SELECT 
        uca.id,
        uca.id_usuario,
        uca.id_rol,
        uca.id_regional,
        uca.id_centro,
        uca.id_compromiso,
        uca.estado,
        c.id, c.nombre, c.descripcion, c.peso_porcentual, c.estado
    FROM usuario_compromiso_asignacion uca
    JOIN compromisos c ON uca.id_compromiso = c.id
    WHERE uca.id_usuario = :usuario_id AND uca.estado = TRUE
    ORDER BY c.id
    """
    result = await db.execute(text(query), {"usuario_id": usuario_id})
    
    compromisos = []
    for row in result:
        compromiso = CompromisoResponse(
            id=row[7],
            nombre=row[8],
            descripcion=row[9],
            peso_porcentual=float(row[10]),
            estado=row[11]
        )
        asignacion = UsuarioCompromisoAsignacionResponse(
            id=row[0],
            id_usuario=row[1],
            id_rol=row[2],
            id_regional=row[3],
            id_centro=row[4],
            id_compromiso=row[5],
            estado=row[6],
            compromiso=compromiso
        )
        compromisos.append(asignacion)
    
    if not compromisos:
        raise HTTPException(status_code=404, detail="No se encontraron compromisos para este usuario")
    
    return compromisos

# ============================================
# ENDPOINTS - ACCIONES
# ============================================

@app.get("/api/v1/usuarios/{usuario_id}/roles/{id_rol}/compromisos/{compromiso_id}/acciones", response_model=List[AccionResponse])
async def get_acciones_disponibles(usuario_id: int, id_rol: int, compromiso_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener acciones disponibles para un usuario en un rol y compromiso específico"""
    # Verificar que el usuario tiene ese rol y ese compromiso
    query_verificar = """
    SELECT uca.id FROM usuario_compromiso_asignacion uca
    WHERE uca.id_usuario = :usuario_id 
      AND uca.id_rol = :id_rol 
      AND uca.id_compromiso = :compromiso_id
      AND uca.estado = TRUE
    """
    result = await db.execute(text(query_verificar), {
        "usuario_id": usuario_id,
        "id_rol": id_rol,
        "compromiso_id": compromiso_id
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="El usuario no tiene asignado este rol y compromiso")
    
    # Obtener acciones específicas del rol y compromiso
    query = """
    SELECT 
        a.id,
        a.nombre,
        a.descripcion,
        a.obligatorio,
        a.peso_fijo,
        a.estado
    FROM acciones a
    WHERE a.id_rol = :id_rol 
      AND a.id_compromiso = :compromiso_id
      AND a.estado = TRUE
    ORDER BY a.obligatorio DESC, a.id
    """
    result = await db.execute(text(query), {"id_rol": id_rol, "compromiso_id": compromiso_id})
    
    acciones = []
    for row in result:
        accion = AccionResponse(
            id=row[0],
            nombre=row[1],
            descripcion=row[2],
            obligatorio=row[3],
            peso_fijo=float(row[4]) if row[4] else None,
            estado=row[5]
        )
        acciones.append(accion)
    
    if not acciones:
        raise HTTPException(status_code=404, detail="No se encontraron acciones disponibles")
    
    return acciones

@app.get("/api/v1/usuarios/{usuario_id}/roles/{id_rol}/compromisos/{compromiso_id}/acciones-seleccionadas", response_model=List[AccionSeleccionResponse])
async def get_acciones_seleccionadas(usuario_id: int, id_rol: int, compromiso_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener acciones ya seleccionadas por el usuario en un rol y compromiso específico"""
    query = """
    SELECT 
        ucas.id,
        ucas.id_accion,
        ucas.peso_porcentual_usuario,
        a.id, a.nombre, a.descripcion, a.obligatorio, a.peso_fijo, a.estado,
        ucas.estado
    FROM usuario_compromiso_accion_seleccion ucas
    JOIN usuario_compromiso_asignacion uca ON ucas.id_usuario_compromiso_asignacion = uca.id
    JOIN acciones a ON ucas.id_accion = a.id
    WHERE uca.id_usuario = :usuario_id 
      AND uca.id_rol = :id_rol
      AND uca.id_compromiso = :compromiso_id
      AND uca.estado = TRUE
    ORDER BY a.obligatorio DESC, a.id
    """
    result = await db.execute(text(query), {
        "usuario_id": usuario_id,
        "id_rol": id_rol,
        "compromiso_id": compromiso_id
    })
    
    acciones = []
    for row in result:
        accion = AccionResponse(
            id=row[3],
            nombre=row[4],
            descripcion=row[5],
            obligatorio=row[6],
            peso_fijo=float(row[7]) if row[7] else None,
            estado=row[8]
        )
        accion_seleccionada = AccionSeleccionResponse(
            id=row[0],
            id_accion=row[1],
            peso_porcentual_usuario=float(row[2]),
            accion=accion,
            estado=row[9]
        )
        acciones.append(accion_seleccionada)
    
    return acciones

# ============================================
# ENDPOINTS - SELECCIONAR ACCIONES
# ============================================

@app.post("/api/v1/usuarios/{usuario_id}/roles/{id_rol}/compromisos/{compromiso_id}/acciones/seleccionar")
async def seleccionar_accion(
    usuario_id: int,
    id_rol: int,
    compromiso_id: int,
    accion_data: AccionSeleccionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Seleccionar una acción y asignarle peso"""
    
    # Obtener la asignación
    query_asignacion = """
    SELECT id FROM usuario_compromiso_asignacion
    WHERE id_usuario = :usuario_id 
      AND id_rol = :id_rol
      AND id_compromiso = :compromiso_id 
      AND estado = TRUE
    LIMIT 1
    """
    result = await db.execute(text(query_asignacion), {
        "usuario_id": usuario_id,
        "id_rol": id_rol,
        "compromiso_id": compromiso_id
    })
    asignacion = result.first()
    
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    id_asignacion = asignacion[0]
    
    # Verificar que la acción existe y pertenece al rol y compromiso
    query_accion = """
    SELECT id FROM acciones 
    WHERE id = :id_accion 
      AND id_compromiso = :compromiso_id 
      AND id_rol = :id_rol
      AND estado = TRUE
    """
    result = await db.execute(text(query_accion), {
        "id_accion": accion_data.id_accion,
        "compromiso_id": compromiso_id,
        "id_rol": id_rol
    })
    if not result.first():
        raise HTTPException(status_code=404, detail="Acción no encontrada para este rol y compromiso")
    
    # Insertar o actualizar la selección
    query_insert = """
    INSERT INTO usuario_compromiso_accion_seleccion 
    (id_usuario_compromiso_asignacion, id_accion, peso_porcentual_usuario, estado, fecha_seleccion)
    VALUES (:id_asignacion, :id_accion, :peso, TRUE, CURRENT_TIMESTAMP)
    ON CONFLICT (id_usuario_compromiso_asignacion, id_accion) 
    DO UPDATE SET peso_porcentual_usuario = :peso
    RETURNING id
    """
    result = await db.execute(text(query_insert), {
        "id_asignacion": id_asignacion,
        "id_accion": accion_data.id_accion,
        "peso": accion_data.peso_porcentual_usuario
    })
    await db.commit()
    
    return {"mensaje": "Acción seleccionada correctamente", "id": result.scalar()}

# ============================================
# ENDPOINTS - ACCIONES DE INNOVACIÓN
# ============================================

@app.post("/api/v1/usuarios/{usuario_id}/roles/{id_rol}/innovaciones", response_model=AccionInnovacionResponse)
async def crear_accion_innovacion(
    usuario_id: int,
    id_rol: int,
    accion_data: AccionInnovacionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Crear una acción de innovación customizada"""
    
    # Obtener la asignación de innovación (compromiso id=3)
    query_asignacion = """
    SELECT id FROM usuario_compromiso_asignacion
    WHERE id_usuario = :usuario_id 
      AND id_rol = :id_rol
      AND id_compromiso = 3 
      AND estado = TRUE
    LIMIT 1
    """
    result = await db.execute(text(query_asignacion), {
        "usuario_id": usuario_id,
        "id_rol": id_rol
    })
    asignacion = result.first()
    
    if not asignacion:
        raise HTTPException(status_code=404, detail="Asignación de innovación no encontrada")
    
    # Contar acciones de innovación existentes
    query_count = """
    SELECT COUNT(*) FROM usuario_accion_innovacion
    WHERE id_usuario_compromiso_asignacion = :id_asignacion AND estado = TRUE
    """
    result = await db.execute(text(query_count), {"id_asignacion": asignacion[0]})
    count = result.scalar()
    
    if count >= 5:
        raise HTTPException(status_code=400, detail="Máximo 5 acciones de innovación permitidas")
    
    if count < 3:
        raise HTTPException(status_code=400, detail="Mínimo 3 acciones de innovación requeridas")
    
    # Insertar acción de innovación
    query_insert = """
    INSERT INTO usuario_accion_innovacion 
    (id_usuario_compromiso_asignacion, nombre, descripcion, peso_porcentual_usuario, evidencias, estado, fecha_creacion)
    VALUES (:id_asignacion, :nombre, :descripcion, :peso, :evidencias, TRUE, CURRENT_TIMESTAMP)
    RETURNING id, nombre, descripcion, peso_porcentual_usuario, evidencias, estado, fecha_creacion
    """
    result = await db.execute(text(query_insert), {
        "id_asignacion": asignacion[0],
        "nombre": accion_data.nombre,
        "descripcion": accion_data.descripcion,
        "peso": accion_data.peso_porcentual_usuario,
        "evidencias": accion_data.evidencias
    })
    await db.commit()
    row = result.first()
    
    return AccionInnovacionResponse(
        id=row[0],
        nombre=row[1],
        descripcion=row[2],
        peso_porcentual_usuario=float(row[3]),
        evidencias=row[4],
        estado=row[5],
        fecha_creacion=row[6]
    )

@app.get("/api/v1/usuarios/{usuario_id}/roles/{id_rol}/innovaciones", response_model=List[AccionInnovacionResponse])
async def get_acciones_innovacion(usuario_id: int, id_rol: int, db: AsyncSession = Depends(get_db)):
    """Obtener todas las acciones de innovación del usuario para un rol específico"""
    query = """
    SELECT 
        uai.id,
        uai.nombre,
        uai.descripcion,
        uai.peso_porcentual_usuario,
        uai.evidencias,
        uai.estado,
        uai.fecha_creacion
    FROM usuario_accion_innovacion uai
    JOIN usuario_compromiso_asignacion uca ON uai.id_usuario_compromiso_asignacion = uca.id
    WHERE uca.id_usuario = :usuario_id 
      AND uca.id_rol = :id_rol
      AND uca.id_compromiso = 3 
      AND uca.estado = TRUE
    ORDER BY uai.fecha_creacion DESC
    """
    result = await db.execute(text(query), {"usuario_id": usuario_id, "id_rol": id_rol})
    
    innovaciones = []
    for row in result:
        innovacion = AccionInnovacionResponse(
            id=row[0],
            nombre=row[1],
            descripcion=row[2],
            peso_porcentual_usuario=float(row[3]),
            evidencias=row[4],
            estado=row[5],
            fecha_creacion=row[6]
        )
        innovaciones.append(innovacion)
    
    return innovaciones

# ============================================
# ENDPOINTS - VALIDACIÓN
# ============================================

@app.get("/api/v1/usuarios/{usuario_id}/roles/{id_rol}/validar-pesos", response_model=List[ValidacionPesosResponse])
async def validar_pesos_usuario(usuario_id: int, id_rol: int, db: AsyncSession = Depends(get_db)):
    """Validar que los pesos de acciones sumen 100% para cada compromiso de un rol específico"""
    query = """
    SELECT 
        c.id,
        c.nombre,
        c.peso_porcentual,
        COUNT(CASE WHEN ucas.id IS NOT NULL OR uai.id IS NOT NULL THEN 1 END) as total_acciones,
        COALESCE(SUM(ucas.peso_porcentual_usuario), 0) + COALESCE(SUM(uai.peso_porcentual_usuario), 0) as suma_pesos
    FROM usuario_compromiso_asignacion uca
    JOIN compromisos c ON uca.id_compromiso = c.id
    LEFT JOIN usuario_compromiso_accion_seleccion ucas ON uca.id = ucas.id_usuario_compromiso_asignacion
    LEFT JOIN usuario_accion_innovacion uai ON uca.id = uai.id_usuario_compromiso_asignacion
    WHERE uca.id_usuario = :usuario_id 
      AND uca.id_rol = :id_rol
      AND uca.estado = TRUE
    GROUP BY c.id, c.nombre, c.peso_porcentual
    ORDER BY c.id
    """
    result = await db.execute(text(query), {"usuario_id": usuario_id, "id_rol": id_rol})
    
    validaciones = []
    for row in result:
        suma_pesos = float(row[4]) if row[4] else 0
        peso_real = (suma_pesos * float(row[2])) / 100
        es_valido = suma_pesos == 100
        
        validacion = ValidacionPesosResponse(
            compromiso_id=row[0],
            compromiso_nombre=row[1],
            total_acciones=int(row[3]),
            suma_pesos=suma_pesos,
            peso_real_en_total=peso_real,
            es_valido=es_valido,
            mensaje="✓ Válido" if es_valido else f"✗ Las acciones deben sumar 100% (actual: {suma_pesos}%)"
        )
        validaciones.append(validacion)
    
    return validaciones

# ============================================
# HEALTH CHECK
# ============================================

@app.get("/health")
async def health_check():
    """Verificar que la API está activa"""
    return {"status": "ok", "message": "API funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)