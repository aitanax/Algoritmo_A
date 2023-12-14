
# -------------------------------------------------------------- IMPORTS --------------------------------------------------------------
import sys
import time
import csv
# -------------------------------------------------------------------------------------------------------------------------------------
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
    with open(path[:-6] + f'-{heuristica}' + '.stat', 'w', encoding='UTF8') as file:

        #print("\nESTADÍSTICAS DE LA EJECUCIÓN:")
        file.write(f'Tiempo total: {tiempo_total}\n')
        file.write(f'Coste total: {int(coste_total)}\n')
        file.write(f'Longitud del plan: {longitud_solucion}\n')
        file.write(f'Nodos expandidos: {nodos_expandidos}\n')

        #print(f'Tiempo total: {tiempo_total}')
        #print(f'Coste Total: {coste_total}')
        #print(f'Longitud del plan: {longitud_solucion}')
        #print(f'Nodos expandidos: {nodos_expandidos}')

def write_solution(heuristica, pasos_solucion, path):
    """Función que escribe los resultados en un archivo de texto, de tipo '.output' """
    # Abrimos el archivo de texto
    with open(path[:-6] + f'-{heuristica}' + '.output', 'w', encoding='UTF8') as file:
        # Escribimos los pasos de la solución
        #print("\nPASOS DE LA SOLUCIÓN:")
        for paso in pasos_solucion:
            file.write(str(paso))
        #print(pasos_solucion)
# -------------------------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ FUNCION DE ORDENACIÓN DE LISTA EN LISTA --------------------------------------------

def ordenar_bucket(lista_a, lista_b):
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
            return f"({self.fila + 1},{self.columna + 1}):{self.tipo}:{self.energia}"

    def __eq__(self, estado):
        return self.fila == estado.fila and self.columna == estado.columna and self.energia == estado.energia and self.pacientes_recoger_n == estado.pacientes_recoger_n and self.pacientes_recoger_c == estado.pacientes_recoger_c and self.asientos_n == estado.asientos_n and self.asientos_c == estado.asientos_c

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
        raise ValueError("El número de la heurística no es válido, disponibles de la 1 a la 3")
        
    def heuristica_1(self) :
        """ Función que implementa la heurística 1: Dijkstra """
        return 0
   
    def heuristica_2(self):
        """ Función que implementa la heurística 2, heuristica con valor 0 en caso de que no queden pacientes por recoger
        y con valor 'numero_pacientes' en caso de quedar pacientes por recoger"""
        if not self.pacientes_recoger_n and not self.pacientes_recoger_c:
            return 0
        return len(self.pacientes_recoger_n) + len(self.pacientes_recoger_c)
    

    def heuristica_3(self):
        # Si no quedan pacientes por recoger, la heurística es la distancia de Manhattan entre la ambulancia y el parking
        if not self.pacientes_recoger_n and not self.pacientes_recoger_c:
            return self.calcular_distancia((self.fila, self.columna), self.parking)
        distancia_total = 0
        # Si quedan pacientes no contagiosos por recoger
        if self.pacientes_recoger_n:
            pacientes_n_visitados = []
            paciente_n_mas_cercano = (self.fila, self.columna)           
            # Se repite el proceso hasta que no queden pacientes no contagiosos por visitar
            for _ in range(len(self.pacientes_recoger_n)):
                distancia_minima_n = float('inf')                
                # Se elige el paciente no contagioso más cercano a la ambulancia
                for paciente_n in self.pacientes_recoger_n:
                    distancia = self.calcular_distancia((self.fila, self.columna), paciente_n)
                    if distancia < distancia_minima_n:
                        distancia_minima_n = distancia
                        paciente_n_mas_cercano = paciente_n 
                # Se añade a la lista de pacientes no contagiosos visitados
                pacientes_n_visitados.append(paciente_n_mas_cercano)
                distancia_total += distancia_minima_n
            # Se calcula la distancia de Manhattan entre el último y el paciente contagioso más cercano
            distancia_minima_c = float('inf')
            paciente_c_mas_cercano = paciente_n_mas_cercano
            # Se repite el proceso hasta que no queden pacientes contagiosos por visitar
            for _ in range(len(self.pacientes_recoger_c)):
                # Se elige el paciente contagioso más cercano al último paciente no contagioso visitado
                for paciente_c in self.pacientes_recoger_c:
                    distancia = self.calcular_distancia(paciente_n_mas_cercano, paciente_c)
                    if distancia < distancia_minima_c:
                        distancia_minima_c = distancia
                        paciente_c_mas_cercano = paciente_c
                # Se añade a la lista de pacientes contagiosos visitados
                distancia_total += distancia_minima_c
            # Se calcula la distancia de Manhattan entre el último paciente contagioso y el parking
            distancia_total += self.calcular_distancia(paciente_c_mas_cercano, self.parking)
        # Si no quedan pacientes no contagiosos por recoger
        else:
            paciente_c_mas_cercano = (self.fila, self.columna)
            # Se repite el proceso hasta que no queden pacientes contagiosos por visitar
            for _ in range(len(self.pacientes_recoger_c)):
                distancia_minima_c = float('inf')
                # Se elige el paciente contagioso más cercano a la ambulancia
                for paciente_c in self.pacientes_recoger_c:
                    distancia = self.calcular_distancia((self.fila, self.columna), paciente_c)
                    if distancia < distancia_minima_c:
                        distancia_minima_c = distancia
                        paciente_c_mas_cercano = paciente_c
                # Se añade a la lista de pacientes contagiosos visitados
                distancia_total += distancia_minima_c
            # Se calcula la distancia de Manhattan entre el último paciente contagioso y el parking
            distancia_total += self.calcular_distancia(paciente_c_mas_cercano, self.parking)

        return distancia_total - len(self.pacientes_recoger_c) * 0.5

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

    if estado.pacientes_recoger_n or estado.asientos_c.count(False) > asientos_cte_c:
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

def sucesores_P(estado, max_energia: int = 50, coste: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un parking en la casilla """

    cambio_energia, nuevo_paciente_n, nuevo_paciente_c, nuevo_asiento_n, nuevo_asiento_c = (
        max_energia,
        estado.pacientes_recoger_n.copy(),
        estado.pacientes_recoger_c.copy(),
        estado.asientos_n.copy(),
        estado.asientos_c.copy()
    )

    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n

def sucesores_N(estado, operador, valor_direccion, coste: int = 1) :
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
            valor_direccion = 1
    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, valor_direccion

def sucesores_C(estado, operador, valor_direccion, coste: int = 1) :
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
        valor_direccion = 1

    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n, valor_direccion

def sucesores_CC(estado, coste: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un centro de atención de pacientes
    contagiosos en la casilla """

    cambio_energia = estado.energia - coste
    nuevo_paciente_n, nuevo_paciente_c, nuevo_asiento_n = estado.pacientes_recoger_n.copy(), estado.pacientes_recoger_c.copy(), estado.asientos_n.copy()
    nuevo_asiento_c =  []
    return cambio_energia, nuevo_paciente_c, nuevo_paciente_n, nuevo_asiento_c, nuevo_asiento_n

def sucesores_CN(estado, coste: int = 1):
    """ Función que se ejecuta cuando se genera un estado hijo con un centro de atención de pacientes
    no contagiosos en la casilla """

    cambio_energia = estado.energia - coste
    nuevo_paciente_n, nuevo_paciente_c = estado.pacientes_recoger_n.copy(), estado.pacientes_recoger_c.copy()
    nuevo_asiento_n, nuevo_asiento_c = estado.asientos_n.copy(), estado.asientos_c.copy()

    # Se eliminan los pacientes no contagiosos de las listas de plazas según la disponibilidad
    nuevo_asiento_n = [] if parada_cn(estado)[0] else nuevo_asiento_n
    nuevo_asiento_c = [] if parada_cn(estado)[1] else nuevo_asiento_c

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
    closed_list = []    # Es una lista de estados ya expandidos
    is_goal = False    # Indica si se ha expandido un estado is_goal
    solucion = []   # Lista de estados que forman la solución
    while open_list and not is_goal:
        estado_actual = open_list.pop(0)
        while estado_actual in closed_list:
            estado_actual = open_list.pop(0)

        if (estado_actual.tipo == 'P' and not estado_actual.pacientes_recoger_c and not estado_actual.pacientes_recoger_n and 
            not estado_actual.asientos_c and not estado_actual.asientos_n):
            is_goal = True
        
        else:
            closed_list.append(estado_actual)
            sucesores = generar_sucesores(estado_actual, mapa, heuristica)
            open_list = ordenar_bucket(open_list, sucesores)

    if is_goal:
        solucion.append(estado_actual)
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