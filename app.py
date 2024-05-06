from flask import Flask, render_template
import math
import random

app = Flask(__name__)

def distancia(coord1, coord2):
    lat1 = coord1[0]
    lon1 = coord1[1]
    lat2 = coord2[0]
    lon2 = coord2[1]
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

def evalua_ruta(ruta, coord):
    total = 0
    for i in range(len(ruta) - 1):
        ciudad1 = ruta[i]
        ciudad2 = ruta[i + 1]
        total += distancia(coord[ciudad1], coord[ciudad2])
    total += distancia(coord[ruta[-1]], coord[ruta[0]])  # Volver al punto de inicio
    return total

def busqueda_tabu(ruta, coord):
    mejor_ruta = ruta[:]
    memoria_tabu = {}
    persistencia = 5
    iteraciones = 100

    while iteraciones > 0:
        iteraciones -= 1
        dist_actual = evalua_ruta(ruta, coord)
        mejora = False

        # Evaluar vecinos
        for i in range(len(ruta)):
            if mejora:
                break
            for j in range(len(ruta)):
                if i != j:
                    ruta_tmp = ruta[:]
                    ciudad_tmp = ruta_tmp[i]
                    ruta_tmp[i] = ruta_tmp[j]
                    ruta_tmp[j] = ciudad_tmp
                    dist = evalua_ruta(ruta_tmp, coord)

                    # Comprobar si el movimiento es tabú
                    tabu = False
                    movimiento = f"{ruta_tmp[i]}_{ruta_tmp[j]}"
                    if movimiento in memoria_tabu and memoria_tabu[movimiento] > 0:
                        tabu = True
                    elif f"{ruta_tmp[j]}_{ruta_tmp[i]}" in memoria_tabu and memoria_tabu[f"{ruta_tmp[j]}_{ruta_tmp[i]}"] > 0:
                        tabu = True

                    if dist < dist_actual and not tabu:
                        # Encontrado vecino que mejora el resultado
                        ruta = ruta_tmp[:]
                        if evalua_ruta(ruta, coord) < evalua_ruta(mejor_ruta, coord):
                            mejor_ruta = ruta[:]
                            # Se almacena en memoria Tabú
                            memoria_tabu[movimiento] = persistencia
                            mejora = True
                            break
                    elif dist < dist_actual and tabu:
                        # Comprobar el criterio de aspiración aunque sea movimiento tabú
                        if evalua_ruta(ruta_tmp, coord) < evalua_ruta(mejor_ruta, coord):
                            mejor_ruta = ruta_tmp[:]
                            # Almacenar en Memoria Tabú
                            memoria_tabu[movimiento] = persistencia
                            mejora = True
                            break

        # Reducir la persistencia de los movimientos tabú
        if len(memoria_tabu) > 0:
            for k in list(memoria_tabu.keys()):
                memoria_tabu[k] -= 1
                if memoria_tabu[k] == 0:
                    del memoria_tabu[k]

    return mejor_ruta

@app.route('/')
def index():
    coord = {
        'Jilotepec': (19.984146, -99.519127),
        'Toluca': (19.283389, -99.651294),
        'Atlacomulco': (19.797032, -99.875878),
        'Guadalajara': (20.666006, -103.343649),
        'Monterrey': (25.687299, -100.315655),
        'Cancun': (21.080865, -86.773482),
        'Morelia': (19.706167, -101.191413),
        'Aguascalientes': (21.861534, -102.321629),
        'Queretaro': (20.5856142, -100.392965),
        'Cdmx': (19.432361, -99.133111)
    }

    ruta = list(coord.keys())
    random.shuffle(ruta)

    mejor_ruta = busqueda_tabu(ruta, coord)
    distancia_total = evalua_ruta(mejor_ruta, coord)

    return render_template('index.html', mejor_ruta=mejor_ruta, distancia_total=distancia_total)

if __name__ == '__main__':
    app.run(debug=True)
