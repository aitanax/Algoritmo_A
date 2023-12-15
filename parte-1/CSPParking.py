from constraint import Problem, AllDifferentConstraint, InSetConstraint
import csv
import random
import time

# ------------------------------ FUNCIÓN PARA PROCESAR EL ARCHIVO DE ENTRADA ---------------------------------

def procesar_archivo(path):
    """ Función implementada para procesar un fichero de entrada.
    """
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
    """ Funcion para la restricción 4. Controla la colocacion de los TNU y TSU respecto de un TSU.
        Un TSU no puede tener aparcado por delante, en su misma fila, a ningún otro vehículo excepto si es también de tipo TSU
    """
    return v_tsu[0] != v_tnu[0] or v_tsu[1] >= v_tnu[1]

# ------------------------------ FUNCIÓN PARA RESTRICCIÓN 5: MANIOBRABILIDAD ---------------------------------

def restriccion_maniobrabilidad(v1, v2, v3 ):
    """ Funcion para la restricción 5. Controla la maniobrabilidad de los coches, asegurando libertad de plaza
    a izquierdas o derechas de un coche para su libre movimiento.

        -   Tenemos en cuenta que fila 1 y última fila son casos especiales dado que uno solo tiene fila debajo y
            otro solo encima, respectivamente.
    """
    # Condicion para la primera fila
    if v1[0] == 1 and ((v1[0] + 1 == v2[0] and v1[1] == v2[1]) or (v1[0] + 1 == v3[0] and v1[1] == v3[1])):
        return False 

    # Condicion para la última fila
    if v1[0] == filas and ((v1[0] - 1 == v2[0] and v1[1] == v2[1]) or (v1[0] - 1 == v3[0] and v1[1] == v3[1])):
        return False  

    # Condicioón para el resto de filas
    if v1[0] != 1 and v1[0] != filas and ((v1[0] + 1 == v2[0] and v1[1] == v2[1]) and (v1[0] - 1 == v3[0] and v1[1] == v3[1])):
        return False  

    return True

# -------------------------------- FUNCIÓN RESOLUCIÓN ---------------------------------

def resolver_problema(filas, columnas, plazas_conexion, vehiculos):
    problem = Problem()
    
    parking = [(i, j) for i in range(1, filas + 1) for j in range(1, columnas + 1)]

    for vehiculo in vehiculos:
        problem.addVariable(vehiculo[0], parking)
    problem.addConstraint(AllDifferentConstraint())
    for vehiculo in vehiculos:
        id, tipo, congelar = vehiculo[0], vehiculo[1], vehiculo[2]

        if congelar:
            problem.addConstraint(InSetConstraint(plazas_conexion), [id])

        for vehiculo2 in vehiculos:
            vehiculo2_id, tipo2, _ = vehiculo2
            if tipo == 'TSU'  and  tipo2 == 'TNU':
                problem.addConstraint(restriccion_aparcado_por_delante, (id, vehiculo2_id))

            for vehiculo3 in vehiculos:
                vehiculo3_id = vehiculo3[0]
            
                problem.addConstraint(restriccion_maniobrabilidad, (id, vehiculo2_id, vehiculo3_id))
                
    problem.addConstraint(AllDifferentConstraint())

    # Obtener las soluciones
    soluciones = problem.getSolutions()

    return soluciones

# ------------------------------ FUNCIÓN PARA VOLCAR EN EL ARCHIVO DE SALIDA ---------------------------------

def imprimir_archivo(soluciones, path_salida, filas, columnas):
    with open(path_salida, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        writer.writerow(["N. Sol:", len(soluciones)])

        if len(soluciones) > 2:
            soluciones = random.sample(soluciones, 3)
        
        for index, solucion in enumerate(soluciones):

            writer.writerow([f"Solución aleatoria {index + 1}:"])

            parking = [['-'] * columnas for i in range(filas)]

            for vehiculo, plaza in solucion.items():
                info_vehiculo = next((v for v in vehiculos if v[0] == vehiculo), None)
                if info_vehiculo:
                    tipo_vehiculo = "C" if info_vehiculo[2] else "X"
                    parking[plaza[0]-1][plaza[1]-1] = f"{vehiculo}-{info_vehiculo[1]}-{tipo_vehiculo}"

            for fila in parking:
             writer.writerow(fila)
       
            if index < len(soluciones) - 1:
                writer.writerow([ ])

if __name__ == "__main__":
    import sys
    tiempo_inicio = time.time()
    def command_prompt():
        """ Obtenemos el argumento (path) pasado por consola """
        if len(sys.argv) < 2 or len(sys.argv) > 2:
            print("Error: Se necesita un argumento (el path al test)")
            sys.exit(1)
        return f"{sys.argv[1]}"

    filas, columnas, plazas_conexion, vehiculos = procesar_archivo(command_prompt())
    
    print(f"Filas: {filas}")
    print(f"Columnas: {columnas}")
    print(f"Plazas de Conexión: {plazas_conexion}")
    print(f"Vehículos: {vehiculos}")

    soluciones = resolver_problema(filas, columnas, plazas_conexion, vehiculos)

    if soluciones:
        random.shuffle(soluciones)
        path_salida = str(command_prompt()) + '.csv'
        imprimir_archivo(soluciones, path_salida, filas, columnas)
        print(f"Soluciones guardadas en {path_salida}")
        
    else:
        print("No se encontraron soluciones.")

    tiempo_total = time.time()-tiempo_inicio
    print(tiempo_total)
