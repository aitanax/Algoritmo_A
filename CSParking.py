from constraint import Problem, AllDifferentConstraint, InSetConstraint
import csv
import random

# ------------------------------ FUNCIÓN PARA PROCESAR EL ARCHIVO DE ENTRADA ---------------------------------

def procesar_archivo(path):

    with open(path, 'r') as f:
        lines = f.readlines()
    size = lines[0].strip().split('x')
    filas = int(size[0])
    columnas = int(size[1])
    plazas_conexion_lineas = lines[1].strip()[4:-1].split(')(')
    plazas_conexion = [(int(plaza.split(',')[0]), int(plaza.split(',')[1])) for plaza in plazas_conexion_lineas]
    vehiculos = []
    for line in lines[2:]:
        vehiculo = line.strip().split('-')
        id = int(vehiculo[0])
        tipo = vehiculo[1]
        congelador = vehiculo[2] == 'C'
        vehiculos.append((id, tipo, congelador))

    return filas, columnas, plazas_conexion, vehiculos

# ------------------------------ FUNCIÓN PARA RESTRICCIÓN 4: TSU>TNU ---------------------------------

def restriccion_aparcado_por_delante(v_tsu, v_tnu):
    # Un TSU no puede tener aparcado por delante, en su misma fila, a ningún otro vehículo excepto si es también de tipo TSU
    return v_tsu[0] != v_tnu[0] or v_tsu[1] >= v_tnu[1]  # Se cambia >= por <=

# ------------------------------ FUNCIÓN PARA RESTRICCIÓN 5: MANIOBRABILIDAD ---------------------------------
def restriccion_maniobrabilidad(v1, v2, v3):
        
        # Condicion tres vehiculos seguidos:
        if abs(v1[0] - v2[0]) == 1 and abs(v1[0] - v3[0]) == 1 and v1[1] == v2[1] == v3[1]:
                return False
        # Condicion fila 1:
        if v1[0] == 1:  
                # Derecha
                if (v1[0] + 1 == v2[0] and v1[1]==v2[1]) or (v1[0] + 1 == v3[0] and v1[1]==v3[1]):
                    return False
        # Condicion ultima fila:
        if v1[0] == filas: 
                # Izquierda
                if (v1[0] - 1 == v2[0] and v1[1]==v2[1]) or (v1[0] - 1 == v3[0] and v1[1]==v3[1]):
                    return False

        return True