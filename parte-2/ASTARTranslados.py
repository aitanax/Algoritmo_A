
# -------------------------------------------------------------- IMPORTS --------------------------------------------------------------
import sys
import time
import csv
import math
# -------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------ FUNCIÓN COMPROBACION DE LA HEURISTICA ----------------------------------------

def comprobar_estado(estado):
    """ Función que comprueba la validez de una heurística """
    coste_ruta_f, coste_ruta_g, coste_ruta_h = [], [], []

    i = True
    while i:
        coste_ruta_g.append(estado.coste_gx)
        coste_ruta_h.append(estado.coste_hx)
        coste_ruta_f.append(estado.coste_fx)
        # print(estado.coste_g, estado.coste_h, estado.coste_f)
        if estado.padre is None:
            i = False
        estado = estado.padre

    # Si f(n) != g(n) + h(n) no es admisible
    if round(sum(coste_ruta_f), 2) != round((sum(coste_ruta_g) + sum(coste_ruta_h)), 2):
        return f"ERROR: suma de costes no es correcta\nRuta G: {coste_ruta_g}\nRuta H: {coste_ruta_h}"

    # Si h(n) > h(n') no es admisible
    for i in range(len(coste_ruta_h)-1):
        if coste_ruta_h[i] > coste_ruta_h[i+1]:
            return f"ERROR: heurística no es admisible\nRuta H: {coste_ruta_h}"
    # Si h(n) > g(n), no es admisible, en caso de estar en el estado meta
    
    return "Heurística y costes admisibles"

# ---------------------------------------------------------- LECTURA DE MAPA ----------------------------------------------------------
def cargar_mapa_desde_csv(ruta_csv):
    """Función para procesar el mapa, me vuelve los valores '1', '2', etc. a enteros para poder trabajar con ellos."""
    mapa = []
    with open(ruta_csv, newline='') as archivo_csv:
        lector_csv = csv.reader(archivo_csv, delimiter=';')
        for fila in lector_csv:
            # Convierte cada elemento de la fila a su tipo correspondiente
            fila = [int(valor) if valor.isdigit() else valor.strip('\"') for valor in fila]
            mapa.append(fila)
    return mapa
# -------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- VOLCADO DE RESULTADOS -------------------------------------------------------

def write_statistics(heuristica, tiempo_total, coste_total, longitud_solucion, nodos_expandidos, path):
    """Función que escribe las estadísticas en un archivo de texto, de tipo '.stat' """
    with open(path[:-4] + f'-{heuristica}' + '.stat', 'w', encoding='UTF8') as file:

        #print("\nESTADÍSTICAS DE LA EJECUCIÓN:")
        file.write(f'Tiempo total: {tiempo_total}\n')
        file.write(f'Coste total: {int(coste_total)}\n')
        file.write(f'Longitud del plan: {longitud_solucion}\n')
        file.write(f'Nodos expandidos: {nodos_expandidos}\n')

        print(f'Tiempo total: {tiempo_total}')
        print(f'Coste Total: {coste_total}')
        print(f'Longitud del plan: {longitud_solucion}')
        print(f'Nodos expandidos: {nodos_expandidos}')

def write_solution(heuristica, pasos_solucion, path):
    """Función que escribe los resultados en un archivo de texto, de tipo '.output' """
    # Abrimos el archivo de texto
    with open(path[:-4] + f'-{heuristica}' + '.output', 'w', encoding='UTF8') as file:
        # Escribimos los pasos de la solución
        #print("\nPASOS DE LA SOLUCIÓN:")
        for paso in pasos_solucion:
            file.write(str(paso))
        print(pasos_solucion)
# -------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ FUNCION DE ORDENACIÓN DE LISTA EN LISTA --------------------------------------------

def ordenar_lista(lista_a, lista_b):
    """
    Función que inserta una lista ordenada 'b' en otra lista ordenada 'a' de forma que la lista resultante siga ordenada
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

# -------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------------ CLASE ESTADO -----------------------------------------------------------

class Estado():
    """ Clase de los nodos para el algoritmo A*  """
    def __init__(self, padre, fila, columna, tipo, cambio_energia, pacientes_recoger_n, pacientes_recoger_c,
                 asientos_n, asientos_c, heuristica, parking: list = None, centro_n: list = None, centro_c: list = None):
        
        self.padre = padre
        # posicion del vehiculo : (fila, columna) // Lo hicimos de esta forma para que a la hora de imprimir los pasos nos fuese más sencillo
        self.fila = fila
        self.columna = columna
        self.tipo = tipo
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
            return f"({self.fila + 1},{self.columna + 1}):{self.tipo}:{self.energia}: coste h: {self.coste_hx} : coste g{self.coste_gx}: coste f {self.coste_fx}"

    def __eq__(self, estado):
        if not isinstance(estado, Estado):
            return False
        return self.fila == estado.fila and self.columna == estado.columna and self.energia == estado.energia and self.pacientes_recoger_n == estado.pacientes_recoger_n and self.pacientes_recoger_c == estado.pacientes_recoger_c and self.asientos_n == estado.asientos_n and self.asientos_c == estado.asientos_c

    def __hash__(self):
        lista_pos_pacientes = []
        for paciente in self.pacientes_recoger_c + self.pacientes_recoger_n:
            lista_pos_pacientes.append(paciente[0])
            lista_pos_pacientes.append(paciente[1])

        lista_hash = [elemento for elemento in lista_pos_pacientes + self.asientos_c + self.asientos_n]
        lista_hash.append(self.fila)
        lista_hash.append(self.columna)
        lista_hash.append(self.energia)
        lista_hash = tuple(lista_hash)
        return hash(lista_hash)

    def calculo_gx(self, padre: object):
        """ Función que calcula el coste G"""
        if padre is None:
            return 0
        # Aumentamos coste en función del tipo, siempre que no sea un entero será 1
        return padre.coste_gx + (self.tipo if isinstance(self.tipo, int) else 1)
    
    def seleccionar_heuristica(self, heuristica: int):
        """ Función que calcula el coste h """
        if heuristica == 1:
            return self.heuristica_1()
        elif heuristica == 2:
            return self.heuristica_2()
        elif heuristica == 3:
            return self.heuristica_3()
        elif heuristica == 4:
            return self.heuristica_4()
        raise ValueError("El número de la heurística no es válido, disponibles de la 1 a la 4")
        
    def heuristica_1(self) :
        """ Función que implementa la heurística 1: Dijkstra """
        return 0
   
    def heuristica_2(self):
        if not self.pacientes_recoger_n and not self.pacientes_recoger_c:
            # No quedan pacientes por recoger, valor 0
            return 0
        else:
            # Quedan pacientes por recoger, valor igual al número de pacientes
            return len(self.pacientes_recoger_n) + len(self.pacientes_recoger_c)

    def heuristica_3(self):
        pacientes_totales = self.pacientes_recoger_n + self.pacientes_recoger_c
        distancia_total = 0

        while pacientes_totales:
            paciente_actual = pacientes_totales.pop(0)
            dist_min_otro_paciente = math.inf

            for otro_paciente in pacientes_totales:
                distancia = self.calcular_distancia(paciente_actual, otro_paciente)
                if distancia < dist_min_otro_paciente:
                    dist_min_otro_paciente = distancia

            distancia_total += dist_min_otro_paciente if dist_min_otro_paciente != math.inf else 0

        distancia_total += len(self.pacientes_recoger_n + self.pacientes_recoger_c)  # Vuelta al parking
        return distancia_total

    def heuristica_4(self):
        """Heurística personalizada basada en la distancia mínima a todos los pacientes"""
        dist_min_paciente = math.inf
        distancia_total = 0
        paciente_min_ubi = [self.fila, self.columna]
        pacientes_totales = self.pacientes_recoger_n + self.pacientes_recoger_c

        while pacientes_totales:
            dist_min_paciente = math.inf
            for paciente in pacientes_totales:
                distancia = self.calcular_distancia(paciente_min_ubi, paciente)
                if distancia < dist_min_paciente:
                    dist_min_paciente = distancia
                    paciente_min_ubi = paciente
            pacientes_totales.remove(paciente_min_ubi)
            distancia_total += distancia

        distancia_total += 1 # Vuelta al parking
        return distancia_total

    def calcular_distancia(self, punto_a, punto_b):
        return abs(punto_a[0] - punto_b[0]) + abs(punto_a[1] - punto_b[1])


# -------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- GENERAR SUCESORES -----------------------------------------------------------

def generar_sucesores(estado, mapa, heuristica, coste: int = 1):
    sucesores = []
    
    def agregar_sucesor(dx, dy):
        nonlocal sucesores
        nueva_fila, nueva_columna = estado.fila + dx, estado.columna + dy
        if 0 <= nueva_fila < len(mapa) and 0 <= nueva_columna < len(mapa[0]) and mapa[nueva_fila][nueva_columna] != 'X':
            tipo = mapa[nueva_fila][nueva_columna]
            cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = None, None, None, None, None
            
            if tipo == 'P':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = sucesores_P(estado, coste=coste)
            elif tipo == 'N':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, tipo = sucesores_N(estado, "izquierda" if dx == 0 and dy == -1 else "derecha" if dx == 0 and dy == 1 else "arriba" if dx == -1 and dy == 0 else "abajo", tipo, coste)
            elif tipo == 'C':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, tipo = sucesores_C(estado, "izquierda" if dx == 0 and dy == -1 else "derecha" if dx == 0 and dy == 1 else "arriba" if dx == -1 and dy == 0 else "abajo", tipo, coste)
            elif tipo == 'CC':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = sucesores_CC(estado, coste)
            elif tipo == 'CN':
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = sucesores_CN(estado, coste)
            elif isinstance(tipo, int):
                cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n = sucesores_enteros(estado, tipo)
            
            if cambio_energia is not None and cambio_energia >= 0:
                sucesor = Estado(estado, nueva_fila, nueva_columna, tipo, cambio_energia, nuevo_paciente_n, nuevo_paciente_c, nuevo_asiento_n, nuevo_asiento_c, heuristica)
                sucesores.append(sucesor)

    agregar_sucesor(0, -1)  # Izquierda
    agregar_sucesor(0, 1)   # Derecha
    agregar_sucesor(-1, 0)  # Arriba
    agregar_sucesor(1, 0)   # Abajo

    sucesores.sort(key=lambda x: x.coste_fx)
    return sucesores

# -------------------------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------------- ACCIONES DEL VEHICULO ------------------------------------------------------


def recoger_tipo_n(estado, asientos_cte_n: int = 8, asientos_cte_c: int = 2):
    """ Un paciente no contagioso se recoge si hay plazas no contagiosas libres o si hay plazas contagiosas libres 
    y no hay ningún paciente contagioso en ellas """
    if len(estado.asientos_n) < asientos_cte_n:
        return True, False # Se puede recoger y se recoge en plazas no contagiosas: acc/asiento_c
    if len(estado.asientos_c) < asientos_cte_c:
        if True in estado.asientos_c:
            return False, False #No se puede recoger
    # Si no hay ningún paciente contagioso en las plazas contagiosas, se puede recoger
    return True, True

def recoger_tipo_c(estado, asientos_cte_c: int = 2):
    """ Un paciente contagioso se recoge si hay plazas contagiosas libres y no hay ningún paciente no contagioso en ellas.
    También NO debe haber ningún paciente no contagioso restante por recoger """
    # Comprobamos si quedan pacientes no contagiosos por recoger
    if estado.pacientes_recoger_n:
        return False
    # Comprobamos si hay plazas contagiosas libres
    if len(estado.asientos_c) < asientos_cte_c:
        # Comprobamos si hay algún paciente no contagioso en las plazas contagiosas
        if False in estado.asientos_c:    # Los pacientes no contagiosos tienen un valor False
            return False
    # Si no hay ningún paciente no contagioso en las plazas contagiosas, se puede recoger
        return True
    return False

def parada_cn(estado):
     # Comprobamos si hay algún paciente contagioso en las plazas de pacientes contagiosos
    if True in estado.asientos_c:     # Los pacientes contagiosos tienen un valor True
        return False, False
    # Comprobamos si hay pacientes no contagiosos en las plazas de pacientes no contagiosos
    elif False in estado.asientos_n:
        # Comprobamos si hay pacientes no contagiosos en las plazas de pacientes contagiosos
        if False in estado.asientos_c:
            return True, True
        else:
            return True, False
    else:
        return False, False     # No hay pacientes no contagiosos en ninguna plaza

def sucesores_P(estado, max_energia: int = 50, coste: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un parking en la casilla """
    cambio_energia, nuevo_paciente_n, nuevo_paciente_c, nuevo_asiento_n, nuevo_asiento_c = (
        max_energia,
        estado.pacientes_recoger_n.copy(),
        estado.pacientes_recoger_c.copy(),
        estado.asientos_n.copy(),
        estado.asientos_c.copy())

    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n

def sucesores_N(estado, operador, cambio_tipo, coste: int = 1) :
    """ Función que se ejecuta cuando se genera un estado hijo con un paciente no contagioso en la casilla,
    dada una dirección de movimiento """
    dx, dy = 0, 0
    if operador == "arriba":
        dx = -1
    elif operador == "abajo":
        dx = 1
    elif operador == "izquierda":
        dy = -1
    elif operador == "derecha":
        dy = 1
    else:
        raise ValueError("Operador no válido")
    cambio_energia = estado.energia - coste
    nuevo_paciente_c, nuevo_paciente_n = estado.pacientes_recoger_c.copy(), estado.pacientes_recoger_n.copy()
    nuevo_asiento_c, nuevo_asiento_n = estado.asientos_c.copy(), estado.asientos_n.copy()

    if [estado.fila + dx, estado.columna + dy] in estado.pacientes_recoger_n:
        accesible, en_plazas_c = recoger_tipo_n(estado)
        if accesible:
            nuevo_paciente_n = estado.pacientes_recoger_n.copy()
            nuevo_paciente_n.remove([estado.fila + dx, estado.columna + dy])

            if en_plazas_c:
                nuevo_asiento_c.append(False)
            else:
                nuevo_asiento_n.append(False)
        else:
            cambio_tipo = 1
    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, cambio_tipo

def sucesores_C(estado, operador, cambio_tipo, coste: int = 1) :
    """ Función que se ejecuta cuando se genera un estado hijo con un paciente contagioso en la casilla,
    dada una dirección de movimiento """
    dx, dy = 0, 0

    if operador == "arriba":
        dx = -1
    elif operador == "abajo":
        dx = 1
    elif operador == "izquierda":
        dy = -1
    elif operador == "derecha":
        dy = 1
    else:
        raise ValueError("Operador no válido")

    cambio_energia = estado.energia - coste
    nuevo_paciente_n, nuevo_paciente_c = estado.pacientes_recoger_n.copy(), estado.pacientes_recoger_c.copy()
    nuevo_asiento_n, nuevo_asiento_c = estado.asientos_n.copy(), estado.asientos_c.copy()

    if [estado.fila + dx, estado.columna + dy] in estado.pacientes_recoger_c:
        accesible = recoger_tipo_c(estado)
        if accesible:
            nuevo_paciente_c = estado.pacientes_recoger_c.copy()
            nuevo_paciente_c.remove([estado.fila + dx, estado.columna + dy])
            nuevo_asiento_c.append(True)
        else:
            nuevo_paciente_c, nuevo_asiento_c = estado.pacientes_recoger_c.copy(), estado.asientos_c.copy()
            nuevo_asiento_n = estado.asientos_n.copy()

    else:
        nuevo_paciente_c, nuevo_asiento_n, nuevo_asiento_c = estado.pacientes_recoger_c.copy(), estado.asientos_n.copy(), estado.asientos_c.copy()
        cambio_tipo = 1

    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, cambio_tipo

def sucesores_CC(estado, coste: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un centro de atención de pacientes
    contagiosos en la casilla """

    cambio_energia = estado.energia - coste
    nuevo_paciente_n, nuevo_paciente_c, nuevo_asiento_n, nuevo_asiento_c = estado.pacientes_recoger_n.copy(), estado.pacientes_recoger_c.copy(), estado.asientos_n.copy(), estado.asientos_c.copy()
    if not False in nuevo_asiento_c:
        nuevo_asiento_c=  []
    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n

def sucesores_CN(estado, coste: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un centro de atención de pacientes
    no contagiosos en la casilla """

    cambio_energia = estado.energia - coste
    nuevo_paciente_n, nuevo_paciente_c = estado.pacientes_recoger_n.copy(), estado.pacientes_recoger_c.copy()
    nuevo_asiento_n, nuevo_asiento_c = estado.asientos_n.copy(), estado.asientos_c.copy()

    # Se eliminan los pacientes no contagiosos de las listas de plazas según la disponibilidad
    if parada_cn(estado)[0]:
        nuevo_asiento_n = []

    if parada_cn(estado)[1]:
        nuevo_asiento_c = []

    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n

def sucesores_enteros(estado, coste: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un número en la casilla """
    cambio_energia = estado.energia - coste
    nuevo_paciente_n, nuevo_paciente_c = estado.pacientes_recoger_n.copy(), estado.pacientes_recoger_c.copy()
    nuevo_asiento_n, nuevo_asiento_c = estado.asientos_n.copy(), estado.asientos_c.copy()
    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n

# -------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------- ALGORITMO A* --------------------------------------------------------------

def a_estrella(estado_inicial, mapa, heuristica):
    """ 
    Función que implementa el algoritmo A* // Con cronometro
    """
    iniciar_tiempo = time.time()
    open_list = [estado_inicial]  # Es una lista ordenada por coste_f de los estados a expandir
    closed_list = set()    # Es una lista de estados ya expandidos
    is_goal = False    # Indica si se ha expandido un estado is_goal
    solucion = []   # Lista de estados que forman la solución
    early_stop = False
    while open_list and not is_goal:
        estado_actual = open_list.pop(0)
        while estado_actual in closed_list:
            try :
                estado_actual = open_list.pop(0)
            except IndexError:
                # La lista abierta está vacía
                estado_actual = None
                early_stop = True
        # Si el estado actual es meta, terminamos
        if (not early_stop and estado_actual.tipo == 'P' and not estado_actual.pacientes_recoger_n and
            not estado_actual.pacientes_recoger_c and not estado_actual.asientos_n and not estado_actual.asientos_c):
            is_goal = True
        elif not early_stop:
            closed_list.add(estado_actual)
            sucesores = generar_sucesores(estado_actual, mapa, heuristica)
            open_list = ordenar_lista(open_list, sucesores)

    if is_goal:
        solucion.append(estado_actual)
        print(comprobar_estado(estado_actual))

        tiempo_total = time.time() - iniciar_tiempo
        while estado_actual.padre:
            solucion.append(estado_actual.padre)
            estado_actual = estado_actual.padre
        solucion.reverse() # Invertimos la lista solución
        pasos_solucion = "\n".join(str(estado) for estado in solucion)
        coste_total = solucion[-1].coste_gx # Guardamos el coste total de la solución
        longitud_solucion = len(solucion) # Guardamos la longitud de la solución
        nodos_expandidos = len(closed_list) + 1

    else:
        tiempo_total = time.time() - iniciar_tiempo
        pasos_solucion = "NO EXISTE SOLUCIÓN"
        coste_total = 0
        longitud_solucion = 0 
        nodos_expandidos = len(closed_list)

    return pasos_solucion, tiempo_total, coste_total, longitud_solucion, nodos_expandidos

# -------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------------- PROGRAMA PRINCIPAL ----------------------------------------------------------

def main():
    """ Función principal del programa """
    # Obtenemos el path del fichero y la heurística a utilizar desde la consola
    if len(sys.argv) != 3:
        print("Uso: python3 prueba2.py <ruta_csv> <otro_parametro>")
        sys.exit(1)

    ruta_csv = sys.argv[1]
    heuristica = int(sys.argv[2])

    mapa = cargar_mapa_desde_csv(ruta_csv)

    energia_inicial = 50
    p = None
    pacientes_recoger_n, pacientes_recoger_c = [], []
    centro_c, centro_n = [], []

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
        raise ValueError("No se encontró el parking.")

    estado_inicial = Estado(None, p[0], p[1], 'P', energia_inicial, pacientes_recoger_n, pacientes_recoger_c, [], [], heuristica, p, centro_n, centro_c)
    pasos_solucion, tiempo_total, coste_total, longitud_solucion, nodos_expandidos = a_estrella(estado_inicial, mapa, heuristica)
    
    write_statistics(heuristica, tiempo_total, coste_total, longitud_solucion, nodos_expandidos, ruta_csv)
    write_solution(heuristica, pasos_solucion, ruta_csv)

if __name__ == '__main__':
    # Llamamos a la función principal
    main()