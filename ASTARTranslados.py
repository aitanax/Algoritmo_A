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
        'Localización pacientes': patient_locations,
        'Localización pacientes contagiosos': contagious_locations,
        'Centros tratamiento': treatment_centers,
        'Parking': parking_location,
        'Obstaculos': obstacles,
        'Localizacion inicio': parking_location
    }

# Ejemplo de uso
map_str = './ASTAR-tests/mapa.csv'

map_info = parse_map(map_str)
print(map_info)