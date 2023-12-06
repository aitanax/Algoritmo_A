
import sys
import time


def comprobar_parametros():
    """ Funcion Comprobar Parametros.
        1. Levantamos error en caso de no ser lo esperado.
        2. Devolvemos los argumentos """
    if len(sys.argv) < 3 or len(sys.argv) > 3:
        print("Error: Se necesita un <path> y un tipo de heurística válida (1 o 2)")
        sys.exit(1)
    return sys.argv[1], sys.argv[2]


def parse_map(map_str):
    with open(map_str, 'r') as archivo:
        lines = archivo.readlines()
    rows = len(lines)
    cols = len(lines[0].split(';'))

    map_data = []
    for line in lines:
        cells = line.strip().split(';')
        map_data.append(cells)

    patient_locations = []
    contagious_locations = []
    treatment_centers = {'CC': set(), 'CN': set()}
    parking_location = None
    obstacles = set()

    for i, line in enumerate(lines):
        cells = line.strip().split(';')
        for j, cell in enumerate(cells):
            if cell == 'N':
                patient_locations.append((i, j))
            elif cell == 'C':
                patient_locations.append((i, j))
                contagious_locations.append((i, j))
            elif cell == 'CC':
                treatment_centers['CC'].add((i, j))
            elif cell == 'CN':
                treatment_centers['CN'].add((i, j))
            elif cell == 'P':
                parking_location = (i, j)
            elif cell == 'X':
                obstacles.add((i, j))

    return {

        'Filas': rows,
        'Columnas': cols,
        'Mapa': map_data,
        'N': patient_locations,
        'C': contagious_locations,
        'Centros tratamiento': treatment_centers,
        'P': parking_location,
        'X': obstacles,
        'Localizacion inicio': parking_location
    }

# ----------------- DEFINIMOS CLASE ESTADO ----------------------
class Estado():
        
    def __init__(self, padre: object, cola_bus: list, cola_total: list, heuristica: int):
        """ Constructor de la clase nod """
        self.padre = padre
        self.cola_bus = cola_bus # necesitamos diferenciar contagiosos de no contagisos
        print(f'\nPacientes: {self.cola_bus}')
        self.cola_restante = restantes(self.cola_bus, cola_total)
        print("Pacientes restantes:", self.cola_restante)
        self.energia = energia
        self.posicion_actual = posicion
        # Calulamos los costes
        self.coste_g = coste(self.cola_bus)
        self.coste_h = select_heuristic(heuristica, self.cola_restante)
        self.coste_f = self.coste_g + self.coste_h  # f(n) = g(n) + h(n)
        print(f"Costes del estado hijo: coste g(n): {self.coste_g}, coste h(n): {self.coste_h}, coste f(n): {self.coste_f}")


















def main():
    """ Funcion main. En esta:
        1. Obtenemos fichero y heurística.
        2. Obtenemos la cola, o sea lo que leemos del fichero.
        3. Creamos el estado inicial.
        4. Llamamos a A* """
    # 1
    path_translados = str(comprobar_parametros()[0])
    heuristica = int(comprobar_parametros()[1])
    # 2
    queue = parse_map(path_translados)
    print('\n········································')
    print('\nSE ESTÁ CREANDO EL ESTADO INICIAL...')
    print(f'La cola es: {queue}')
    print(f'La heurística elegída: {heuristica}')
    estado_incial = Estado(None, [], queue, heuristica)
    astar(estado_incial, queue, heuristica)


if __name__ == '__main__':
    # Llamamos a la función principal
    main()