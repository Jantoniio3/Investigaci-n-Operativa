from gurobipy import Model, GRB, quicksum

def importar(nombre):
    with open(nombre, 'r') as f:
        lineas = f.readlines()
    lineas = [linea.strip() for linea in lineas if linea.strip()]
    n = int(lineas[0])
    mapa = [[None for _ in range(n)] for _ in range(n)]
    prioridades = list(map(int, lineas[2].split()))  # Convertir la línea de prioridades a una lista de enteros
    parametros = list(map(int, lineas[1].split()))

    for i in range(n):
        valores = list(map(int, lineas[3 + i].split()))
        for j in range(n):
            if i == j:
                mapa[i][j] = 0
            else:
                mapa[i][j] = valores[j]
    return n, parametros, mapa, prioridades

def main(nombre):
    n, parametros, mapa, prioridades = importar(nombre)
    e = mapa
    d = parametros[0]
    umbral_prioridad = parametros[1]  # Definido como la prioridad mínima que debe alcanzarse
    pr = parametros[2]
    pr1 = parametros[3]
    pr3 = parametros[4]
    pr4 = parametros[5]
    bateria = parametros[6]
    P = prioridades
    estanterias = range(1, n + 1)

    modelo = Model('Problema del viajero en Amazon')
    s = modelo.addVars(estanterias, estanterias, vtype=GRB.BINARY, name='x')
    l = modelo.addVars(estanterias, vtype=GRB.CONTINUOUS, lb=1, ub=n, name='y')
    Z = modelo.addVar(vtype=GRB.CONTINUOUS, name="Z")
    modelo.setObjective(quicksum(e[i-1][j-1] * s[i, j] for i in estanterias for j in estanterias if i != j))
    print(Z)

    # 1. Restricción base: Entrada y salida.
    for i in estanterias:  # Sale de una estantería
        modelo.addConstr(quicksum(s[i, j] for j in estanterias if j != i) == 1, name=f"Salida{i}")

    for j in estanterias:  # Entra una vez a cada estantería
        modelo.addConstr(quicksum(s[i, j] for i in estanterias if i != j) == 1, name=f"Entrada{j}")

    #Restriccion de eliminacion de subtours
    for a in estanterias:
        if a != 1:
            modelo.addConstr(l[a] >= 2, name=f"l_min{a}")
            modelo.addConstr(l[a] <= n, name=f"l_max{a}")

    for i in estanterias:
        for j in estanterias:
            if i != j and i != 1 and j!=1:
                modelo.addConstr(l[i] - l[j] + n * s[i, j] <= n - 1, name=f'MTZ {i} {j}')

    # 2. Restricción de Implicación: la salida desde la estantería `pr` solo puede ocurrir si también hay salida desde `pr1`.
    # Esto asegura una dependencia entre las dos estanterías `pr` y `pr1` en cuanto a su inclusión en la ruta.
    modelo.addConstr(
        quicksum(s[pr, k] for k in estanterias if k != pr) <= quicksum(s[pr1, k] for k in estanterias if k != pr1),
        name="Implicacion_de_i_a_j"
    )

    # 3. Restricción de Distancia Mínima: el valor total de la distancia recorrida (Z) debe ser al menos `d`.
    # Esto fuerza al modelo a cumplir con un límite mínimo de distancia, útil para evitar recorridos triviales o demasiado cortos.
    modelo.addConstr(
        Z >= d,
        name="Distancia_Minima"
    )

    # Definición de Z como el costo total del recorrido: `Z` se establece como la suma ponderada de las distancias
    # entre estanterías, multiplicada por las variables de decisión s[i,j] que indican si se recorre la ruta entre `i` y `j`.
    modelo.addConstr(
        Z == quicksum(e[i - 1][j - 1] * s[i, j] for i in estanterias for j in estanterias if i != j),
        name="Definicion_de_Z"
    )

    # 4. Restricción de Prioridad Mínima: la suma de las prioridades ponderadas por las decisiones `s[i,j]` debe ser al menos `umbral_prioridad`.
    # Esto asegura que el recorrido elegido incluya estanterías con una prioridad acumulada mínima, incentivando rutas con mayor valor.
    modelo.addConstr(
        quicksum(P[i - 1] * s[i, j] for i in estanterias for j in estanterias if i != j) >= umbral_prioridad,
        name="Prioridad_Minima"
    )

    # 5. Restricción que prohíbe el camino de la estantería pr3 a la estantería pr4
    modelo.addConstr(s[pr3, pr4] == 0, name="Prohibir_camino_pr3_pr4")

    # 6. Restricción de Coste Fijos: la cantidad de metros recorridos no puede superar el máximo de batería del robot.
    modelo.addConstr(
        quicksum(e[i - 1][j - 1] * s[i, j] for i in estanterias for j in estanterias if i != j) <= bateria,
        name="Restriccion_Bateria"
    )


    modelo.optimize()
    print('---------------------')
    if modelo.status == GRB.OPTIMAL:
        print(f"\nCosto minimo del recorrido: {modelo.ObjVal}")
        ruta = []
        actual = 1
        while True:
            ruta.append(actual)
            for i in estanterias:
                if i != actual and s[actual, i].X > 0.5:
                    siguiente = i
                    break
            if siguiente == 1:
                ruta.append(1)
                break
            else:
                actual = siguiente
        print("Ruta optima-->")
        print(' '.join(map(str, ruta)))
    else:
        print('Sin solucion optima')

if __name__ == "__main__":
    archivo = 'Inst1.txt'  # Añadir el .txt
    main(archivo)
