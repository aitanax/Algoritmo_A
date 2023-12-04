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

# ------------------------------ FUNCIÓN PARA RESTRICCIÓN 5: MANIOBRABILIDAD ---------------------------------
