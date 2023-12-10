import sys
import time
import csv

# -------------------------------------------------------------- CLASE ESTADO --------------------------------------------------------------

class Estado():
    """ 
    Clase de los nodos para el algoritmo A* 
    """
    def __init__(self, padre, fila, columna, valor, cambio_energia, pacientes_recoger_n, pacientes_recoger_c,
                 asientos_n, asientos_c, heuristica, parking: list = None, centro_n: list = None, centro_c: list = None):
        
        self.padre = padre
        # posicion del vehiculo : (fila, columna)
        self.fila = fila
        self.columna = columna
        self.valor = valor
        self.energia = cambio_energia
        self.pacientes_recoger_n = pacientes_recoger_n
        self.pacientes_recoger_c = pacientes_recoger_c
        self.asientos_n = asientos_n
        self.asientos_c = asientos_c
        self.parking = padre.parking if parking is None else parking
        self.centro_n = padre.centro_n if centro_n is None else centro_n
        self.centro_c = padre.centro_c if centro_c is None else centro_c
        self.coste_gx = self.calculo_gx(padre)
        self.coste_hx = self.seleccionar_heuristica(heuristica)
        self.coste_fx = self.coste_gx + self.coste_hx
    
    def __str__(self):

            return f"({self.fila + 1},{self.columna + 1}):{self.valor}:{self.energia}"


    def __eq__(self, estado):
        return (self.fila, self.columna, self.energia, self.pacientes_recoger_n, self.pacientes_recoger_c, self.asientos_n, self.asientos_c) == (estado.fila, estado.columna, estado.energia, estado.pacientes_recoger_n, estado.pacientes_recoger_c, estado.asientos_n, estado.asientos_c)


    def calculo_gx(self, padre: object):
        """ Función que calcula el coste g """
        # Si el padre es None, es el nodo inicial
        if padre is None:
            return 0
        # Si el padre no es None, sumamos el coste del padre más el coste de la casilla
        # Si self.valor es int, ese es el coste de la casilla. En caso contrario, es 1.
        return padre.coste_gx + (self.valor if isinstance(self.valor, int) else 1)
    
    def seleccionar_heuristica(self, heuristica: int):
        """ Función que calcula el coste h """
        if heuristica == 1:
            return self.heuristica_1()
        elif heuristica == 2:
            return self.heuristica_2()
        elif heuristica == 3:
            return self.heuristica_3()
        raise ValueError("El número de la heurística no es válido, disponibles de la 1 a la 4")
        
    def heuristica_1(self) -> int:
        """ Función que implementa la heurística 1: Dijkstra """
        return 0

    def heuristica_2(self) -> int:
        """ Función que implementa la heurística 1, heuristica con valor 1 en caso de que no queden pacientes por recoger
        y con valor 1 en caso de que si"""
        if not self.pacientes_recoger_n and not self.pacientes_recoger_c:
            return 0
        return 1
    
    def heuristica_3(self) -> int:
        """ Función que implementa la heurística 2, heuristica con valor 0 en caso de que no queden pacientes por recoger
        y con valor 'numero_pacientes' en caso de quedar pacientes por recoger"""
        if not self.pacientes_recoger_n and not self.pacientes_recoger_c:
            return 0
        return len(self.pacientes_recoger_n) + len(self.pacientes_recoger_c)

#-----------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------- GENERAR SUCESORES -----------------------------------

def generar_sucesores(estado, mapa, heuristica, coste_predeterminado: int = 1):
    sucesores = []
    
    def agregar_sucesor(dx, dy):
        nonlocal sucesores
        nueva_fila, nueva_columna = estado.fila + dx, estado.columna + dy
        if 0 <= nueva_fila < len(mapa) and 0 <= nueva_columna < len(mapa[0]) and mapa[nueva_fila][nueva_columna] != 'X':
            valor_casilla = mapa[nueva_fila][nueva_columna]
            cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = None, None, None, None, None
            
            if valor_casilla == 'P':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = acciones_casilla_P(estado, coste_predeterminado=coste_predeterminado)
            elif valor_casilla == 'N':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, valor_casilla = acciones_casilla_N(estado, "izquierda" if dx == 0 and dy == -1 else "derecha" if dx == 0 and dy == 1 else "arriba" if dx == -1 and dy == 0 else "abajo", valor_casilla, coste_predeterminado)
            elif valor_casilla == 'C':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, valor_casilla = acciones_casilla_C(estado, "izquierda" if dx == 0 and dy == -1 else "derecha" if dx == 0 and dy == 1 else "arriba" if dx == -1 and dy == 0 else "abajo", valor_casilla, coste_predeterminado)
            elif valor_casilla == 'CC':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = acciones_casilla_CC(estado, coste_predeterminado)
            elif valor_casilla == 'CN':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = acciones_casilla_CN(estado, coste_predeterminado)
            elif isinstance(valor_casilla, int):
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = acciones_casilla_numerica(estado, valor_casilla)
            
            if cambio_energia is not None and cambio_energia >= 0:
                sucesor = Estado(estado, nueva_fila, nueva_columna, valor_casilla, cambio_energia, nuevo_paciente_n, nuevo_paciente_c, nuevo_asiento_n, nuevo_asiento_c, heuristica)
                sucesores.append(sucesor)

    agregar_sucesor(0, -1)  # Izquierda
    agregar_sucesor(0, 1)   # Derecha
    agregar_sucesor(-1, 0)  # Arriba
    agregar_sucesor(1, 0)   # Abajo

    sucesores.sort(key=lambda x: x.coste_fx)
    return sucesores

# --------------------------------------- ACCIONES DEL VEHICULO -----------------------------------


def recoger_tipo_n(estado, asientos_cte_n: int = 8, asientos_cte_c: int = 2):
    """ Un paciente no contagioso se recoge si hay plazas no contagiosas libres o si hay plazas contagiosas libres 
    y no hay ningún paciente contagioso en ellas """

    asiento_disp_n = len(estado.asientos_n) < asientos_cte_n
    asientos_disp_c = len(estado.asientos_c) < asientos_cte_c

    if asiento_disp_n:
        return True, False # Se puede recoger y se recoge en plazas no contagiosas
    elif asientos_disp_c and not any(estado.asientos_c):
        return True, True # Se puede recoger y se recoge en plazas contagiosas
    else:
        return False, False # No se puede recoger
    

def recoger_tipo_c(estado, asientos_cte_c: int = 2):
    """ Un paciente contagioso se recoge si hay plazas contagiosas libres y no hay ningún paciente no contagioso en ellas.
    También NO debe haber ningún paciente no contagioso restante por recoger """

    if estado.pacientes_recoger_n or len(estado.asientos_c) >= asientos_cte_c or any(estado.asientos_c):
        return False
    return True


def parada_cn(estado):
    pacientes_c_contagiosos = any(estado.asientos_c)  # True si hay pacientes contagiosos en plazas contagiosas
    pacientes_n_ocupados = any(estado.asientos_n)  # True si hay pacientes no contagiosos en plazas no contagiosas

    if pacientes_c_contagiosos:
        return False, False # No se puede descargar de ninguna plaza
    elif pacientes_n_ocupados:
        return True, True # Se puede descargar de plazas no contagiosas y de plazas contagiosas
    else:
        return True, False # Se puede descargar de plazas no contagiosas, pero no de plazas contagiosas


def acciones_casilla_P(estado, max_energia: int = 50, coste_predeterminado: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un parking en la casilla """

    cambio_energia, nuevo_paciente_n, nuevo_paciente_c, nuevo_asiento_n, nuevo_asiento_c = (
        max_energia,
        estado.pacientes_recoger_n.copy(),
        estado.pacientes_recoger_c.copy(),
        estado.asientos_n.copy(),
        estado.asientos_c.copy()
    )

    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n

def acciones_casilla_N(estado, direccion_movimiento, valor_direccion, coste_predeterminado: int = 1) :
    """ Función que se ejecuta cuando se genera un estado hijo con un paciente no contagioso en la casilla,
    dada una dirección de movimiento """

    desplazamiento_x, desplazamiento_y = 0, 0

    if direccion_movimiento == "arriba":
        desplazamiento_x = -1
    elif direccion_movimiento == "abajo":
        desplazamiento_x = 1
    elif direccion_movimiento == "izquierda":
        desplazamiento_y = -1
    elif direccion_movimiento == "derecha":
        desplazamiento_y = 1
    else:
        raise ValueError("La dirección de movimiento no es válida")

    cambio_energia = estado.energia - coste_predeterminado
    nuevo_paciente_c = estado.pacientes_recoger_c.copy()
    nuevo_paciente_n = estado.pacientes_recoger_n.copy()
    nuevo_asiento_c, nuevo_asiento_n = estado.asientos_c.copy(), estado.asientos_n.copy()

    if [estado.fila + desplazamiento_x, estado.columna + desplazamiento_y] in estado.pacientes_recoger_n:
        se_puede, en_plazas_c = recoger_tipo_n(estado)

        if se_puede:
            nuevo_paciente_n = estado.pacientes_recoger_n.copy()
            nuevo_paciente_n.remove([estado.fila + desplazamiento_x, estado.columna + desplazamiento_y])

            if en_plazas_c:
                nuevo_asiento_c.append(False)
            else:
                nuevo_asiento_n.append(False)
        else:
            valor_direccion = 1
    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, valor_direccion

def acciones_casilla_C(estado, direccion_movimiento, valor_direccion, coste_predeterminado: int = 1) :
    """ Función que se ejecuta cuando se genera un estado hijo con un paciente contagioso en la casilla,
    dada una dirección de movimiento """

    desplazamiento_x, desplazamiento_y = 0, 0

    if direccion_movimiento == "arriba":
        desplazamiento_x = -1
    elif direccion_movimiento == "abajo":
        desplazamiento_x = 1
    elif direccion_movimiento == "izquierda":
        desplazamiento_y = -1
    elif direccion_movimiento == "derecha":
        desplazamiento_y = 1
    else:
        raise ValueError("La dirección de movimiento no es válida")

    cambio_energia = estado.energia - coste_predeterminado
    nuevo_paciente_n = estado.pacientes_recoger_n.copy()
    nuevo_paciente_c = estado.pacientes_recoger_c.copy()
    nuevo_asiento_n, nuevo_asiento_c = estado.asientos_n.copy(), estado.asientos_c.copy()

    if [estado.fila + desplazamiento_x, estado.columna + desplazamiento_y] in estado.pacientes_recoger_c:
        se_puede = recoger_tipo_c(estado)

        if se_puede:
            nuevo_paciente_c = estado.pacientes_recoger_c.copy()
            nuevo_paciente_c.remove([estado.fila + desplazamiento_x, estado.columna + desplazamiento_y])
            nuevo_asiento_c.append(True)
        else:
            nuevo_paciente_c, nuevo_asiento_c = estado.pacientes_recoger_c.copy(), estado.asientos_c.copy()
            nuevo_asiento_n = estado.asientos_n.copy()

    else:
        nuevo_paciente_c, nuevo_asiento_n, nuevo_asiento_c = estado.pacientes_recoger_c.copy(), estado.asientos_n.copy(), estado.asientos_c.copy()
        valor_direccion = 1

    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, valor_direccion

def acciones_casilla_CC(estado, coste_predeterminado: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un centro de atención de pacientes
    contagiosos en la casilla """

    cambio_energia = estado.energia - coste_predeterminado
    nuevo_paciente_n, nuevo_paciente_c = estado.pacientes_recoger_n.copy(), estado.pacientes_recoger_c.copy()
    nuevo_asiento_n, nuevo_asiento_c = estado.asientos_n.copy(), []
    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n

def acciones_casilla_CN(estado, coste_predeterminado: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un centro de atención de pacientes
    no contagiosos en la casilla """

    cambio_energia = estado.energia - coste_predeterminado
    nuevo_paciente_n, nuevo_paciente_c = estado.pacientes_recoger_n.copy(), estado.pacientes_recoger_c.copy()
    nuevo_asiento_n, nuevo_asiento_c = estado.asientos_n.copy(), estado.asientos_c.copy()

    # Se eliminan los pacientes no contagiosos de las listas de plazas según la disponibilidad
    nuevo_asiento_n = [] if parada_cn(estado)[0] else nuevo_asiento_n
    nuevo_asiento_c = [] if parada_cn(estado)[1] else nuevo_asiento_c

    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n

def acciones_casilla_numerica(estado, coste: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un número en la casilla """

    cambio_energia = estado.energia - coste
    nuevo_paciente_n, nuevo_paciente_c = estado.pacientes_recoger_n.copy(), estado.pacientes_recoger_c.copy()
    nuevo_asiento_n, nuevo_asiento_c = estado.asientos_n.copy(), estado.asientos_c.copy()
    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n


# -----------------------------------------------------------------------------------------------
# --------------------------- FUNCION DE ORDENACIÓN DE LISTA EN LISTA ---------------------------

def merge_listas_ordenada(lista_a, lista_b):
    """
    Función que inserta una lista ordenada 'b' en otra lista ordenada 'a'
    de forma que la lista resultante siga ordenada
    """
    # Si alguna de las listas está vacía, devolvemos la otra lista
    if not lista_a:
        return lista_b
    elif not lista_b:
        return lista_a

    lista_ordenada = []
    index_a, index_b = 0, 0

    while index_a < len(lista_a) and index_b < len(lista_b):
        if lista_a[index_a].coste_fx <= lista_b[index_b].coste_fx:
            lista_ordenada.append(lista_a[index_a])
            index_a += 1
        else:
            lista_ordenada.append(lista_b[index_b])
            index_b += 1

    # Añadimos los elementos restantes de ambas listas (si los hay)
    lista_ordenada.extend(lista_a[index_a:])
    lista_ordenada.extend(lista_b[index_b:])

    return lista_ordenada

# -----------------------------------------------------------------------------------------------
# -------------------------------------- ALGORITMO A* --------------------------------------

def a_estrella(estado_inicial, mapa, heuristica):
    """ 
    Función que implementa el algoritmo A* // Con cronometro
    """
    start_time = time.time()
    abierta = [estado_inicial]  # Es una lista ordenada por coste_f de los estados a expandir
    cerrada = []    # Es una lista de estados ya expandidos
    meta = False    # Indica si se ha expandido un estado meta
    solucion = []   # Lista de estados que forman la solución
    while abierta and not meta:
        estado_actual = abierta.pop(0)
        while estado_actual in cerrada:     # Esto utiliza el método __eq__ de la clase Estado
            estado_actual = abierta.pop(0)
        if (estado_actual.valor == 'P' and not estado_actual.pacientes_recoger_n and not estado_actual.pacientes_recoger_c and 
            not estado_actual.asientos_n and not estado_actual.asientos_c):
            meta = True
        else:
            cerrada.append(estado_actual)
            sucesores = generar_sucesores(estado_actual, mapa, heuristica)
            # Insertamos los hijos (ya ordenados) en la lista abierta (ya ordenada) de forma que la lista abierta siga ordenada
            abierta = merge_listas_ordenada(abierta, sucesores)

    if meta:
        solucion.append(estado_actual)
        tiempo_total = time.time() - start_time
        while estado_actual.padre:
            solucion.append(estado_actual.padre)
            estado_actual = estado_actual.padre
        solucion.reverse() # Invertimos la lista solución
        pasos_solucion = "\n".join(str(estado) for estado in solucion)
        coste_total = solucion[-1].coste_gx # Guardamos el coste total de la solución
        longitud_solucion = len(solucion) # Guardamos la longitud de la solución
        nodos_expandidos = len(cerrada) + 1

    else:
        tiempo_total = time.time() - start_time
        pasos_solucion = "No hay solución"
        coste_total = 0
        longitud_solucion = 0 
        nodos_expandidos = len(cerrada)

    return pasos_solucion, tiempo_total, coste_total, longitud_solucion, nodos_expandidos


# -------------------------------------------- ARCHIVOS DE SALIDA -----------------------------------------------

def cargar_mapa_desde_csv(ruta_csv):
    mapa = []
    with open(ruta_csv, newline='') as archivo_csv:
        lector_csv = csv.reader(archivo_csv, delimiter=';')
        for fila in lector_csv:
            # Convierte cada elemento de la fila a su tipo correspondiente
            fila = [int(valor) if valor.isdigit() else valor.strip('\"') for valor in fila]
            mapa.append(fila)
    return mapa

def write_statistics(heuristica, tiempo_total, coste_total, longitud_solucion, nodos_expandidos, path):
    """Función que escribe las estadísticas en un archivo de texto."""
    with open(path[:-5] + f'-{heuristica}' + '.stat', 'w', encoding='UTF8') as file:
        # Escribimos los resultados
        print("\nESTADÍSTICAS DE LA EJECUCIÓN:")
        file.write(f'Tiempo total: {tiempo_total}\n')
        file.write(f'Coste total: {int(coste_total)}\n')
        file.write(f'Longitud del plan: {longitud_solucion}\n')
        file.write(f'Nodos expandidos: {nodos_expandidos}\n')

        print(f'Tiempo total: {tiempo_total}')
        print(f'Coste Total: {coste_total}')
        print(f'Longitud del plan: {longitud_solucion}')
        print(f'Nodos expandidos: {nodos_expandidos}')

def write_solution(heuristica, pasos_solucion, path):
    """Función que escribe los resultados en un archivo de texto."""
    # Abrimos el archivo de texto
    with open(path[:-5] + f'-{heuristica}' + '.output', 'w', encoding='UTF8') as file:
        # Escribimos los pasos de la solución
        print("\nPASOS DE LA SOLUCIÓN:")
        for paso in pasos_solucion:
            file.write(str(paso))
        print(pasos_solucion)

# ------------------------------------------------------------------------------------------
# -------------------------------- PROGRAMA PRINCIPAL --------------------------------------

def main():
    """ Función principal del programa """
    # Obtenemos el path del fichero y la heurística a utilizar desde la consola
    if len(sys.argv) != 3:
        print("Uso: python3 prueba2.py <ruta_csv> <otro_parametro>")
        sys.exit(1)

    ruta_csv = sys.argv[1]
    heuristica = int(sys.argv[2])

    mapa = cargar_mapa_desde_csv(ruta_csv)
    print(mapa)

    energia_inicial = 50
    p = None
    centro_c = []
    centro_n = []
    pacientes_recoger_n = []
    pacientes_recoger_c = []

    # Buscamos el estado inicial 'P' y las coordenadas de los centros y de los pacientes
    for i in range(len(mapa)):
        for j in range(len(mapa[0])):
            if mapa[i][j] == 'P':
                p = [i, j]
            elif mapa[i][j] == 'CN':
                centro_n.append([i, j])
            elif mapa[i][j] == 'CC':
                centro_c.append([i, j])
            elif mapa[i][j] == 'N':
                pacientes_recoger_n.append([i, j])
            elif mapa[i][j] == 'C':
                pacientes_recoger_c.append([i, j])
    if not p:
        raise ValueError("No se ha encontrado el estado inicial")

    estado_inicial = Estado(None, p[0], p[1], 'P', energia_inicial, pacientes_recoger_n, pacientes_recoger_c, [], [], heuristica, p, centro_n, centro_c)
    
    pasos_solucion, tiempo_total, coste_total, longitud_solucion, nodos_expandidos = a_estrella(estado_inicial, mapa, heuristica)
    
    write_statistics(heuristica, tiempo_total, coste_total, longitud_solucion, nodos_expandidos, ruta_csv)
    write_solution(heuristica, pasos_solucion, ruta_csv)

if __name__ == '__main__':
    # Llamamos a la función principal
    main()