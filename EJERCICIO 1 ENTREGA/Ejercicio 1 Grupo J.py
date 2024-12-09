from gurobipy import Model, GRB  

# Función para importar y procesar los datos desde un archivo de texto
def importar(nombre):

    # Lee el archivo especificado y guarda las líneas no vacías en una lista
    with open(nombre, 'r') as f:
        lineas = f.readlines()
    lineas = [linea.strip() for linea in lineas if linea.strip()]
    
    # La primera línea contiene el número de registros (no usado en este caso)
    n = int(lineas[0])
    
    # La segunda línea contiene los parámetros generales (recursos máximos disponibles)
    parametros = list(map(int, lineas[1].split()))
    
    # Las siguientes líneas contienen los datos específicos para cada taller
    datos = []
    for line in lineas[2:]:
        valores = line.split()
        
        # Convierte "SI"/"NO" en valores booleanos (1 para "SI" y 0 para "NO")
        valores[2] = 1 if valores[2] == 'SI' else 0
        valores[3] = 1 if valores[3] == 'SI' else 0
        
        # Convierte los datos a enteros o flotantes según sea necesario y los almacena en una lista
        fila = [
            int(valores[0]),  # Costo de la modificación
            int(valores[1]),  # Número de mecánicos necesarios
            int(valores[2]),  # Si necesita elevador (1 o 0)
            int(valores[3]),  # Si necesita máquina de extracción de humo (1 o 0)
            int(valores[4]),  # Ganancia por la modificación
            float(valores[5]) # Consumo eléctrico
        ]
        datos.append(fila)  # Agrega la lista 'fila' a la lista de 'datos'
    return parametros, datos  # Devuelve los parámetros y datos procesados

# Función principal que configura y resuelve el modelo de optimización
def main(archivo):
    # Llama a la función 'importar' para obtener los parámetros y datos del archivo
    parametros, datos = importar(archivo)
    
    # Crea el modelo de Gurobi y define su nombre
    modelo = Model(name="Talleres")
    
    # Define las variables de decisión (modificaciones en cada tipo de componente)
    X1 = modelo.addVar(name="Escape", lb=0)
    X2 = modelo.addVar(name="ECU", lb=0)
    X3 = modelo.addVar(name="Motor", lb=0)
    X4 = modelo.addVar(name="Suspension", lb=0)
    X5 = modelo.addVar(name="Frenado", lb=0)
    X6 = modelo.addVar(name="Pintura", lb=0)
    X7 = modelo.addVar(name="Ruedas", lb=0)
    
    # Define la función objetivo: Maximizar las ganancias
    modelo.setObjective((datos[0][4]*X1+datos[1][4]*X2+datos[2][4]*X3+datos[3][4]*X4+datos[4][4]*X5+datos[5][4]*X6+datos[6][4]*X7)-
    (datos[0][0]*X1+datos[1][0]*X2+datos[2][0]*X3+datos[3][0]*X4+datos[4][0]*X5+datos[5][0]*X6+datos[6][0]*X7), GRB.MAXIMIZE)
    
    # Restricciones de recursos:
    # 1. Restricción de número de elevadores
    modelo.addConstr(datos[0][2]*X1+datos[1][2]*X2+datos[2][2]*X3+datos[3][2]*X4+datos[4][2]*X5+datos[5][2]*X6+datos[6][2]*X7<=parametros[0],name="Numero de Elevadores")
    
    # 2. Restricción de número de mecánicos
    modelo.addConstr(datos[0][1]*X1+datos[1][1]*X2+datos[2][1]*X3+datos[3][1]*X4+datos[4][1]*X5+datos[5][1]*X6+datos[6][1]*X7<=parametros[1],name="Numero de Mecanicos")
    
    # 3. Restricción de número de máquinas de extracción de humo
    modelo.addConstr(datos[0][3]*X1+datos[1][3]*X2+datos[2][3]*X3+datos[3][3]*X4+datos[4][3]*X5+datos[5][3]*X6+datos[6][3]*X7<=parametros[2],name="Maquinas de Extraccion de humo")
    
    # 4. Restricción de consumo eléctrico
    modelo.addConstr(datos[0][5]*X1+datos[1][5]*X2+datos[2][5]*X3+datos[3][5]*X4+datos[4][5]*X5+datos[5][5]*X6+datos[6][5]*X7<=parametros[3],name="Consumo electrico")
    
    # Optimiza el modelo
    modelo.optimize()
    
    # Muestra resultados de optimización
    print('---------------------------------------------')
    print("\nValores sombra de las restricciones:")
    for constr in modelo.getConstrs():
        print(f"{constr.ConstrName}: {constr.Pi:.4f}")  # Imprime el valor sombra de cada restricción
    
    # Imprime los costes reducidos de las variables
    print("\nCostes reducidos de las variables:")
    for var in modelo.getVars():
        print(f"{var.VarName}: {var.RC:.4f}")  # Imprime el coste reducido de cada variable
    
    # Imprime las holguras de las restricciones
    print("\nHolguras de las restricciones:")
    for constr in modelo.getConstrs():
        print(f"{constr.ConstrName}: {constr.Slack:.4f}")  # Imprime la holgura de cada restricción
    
    # Si se encontró una solución óptima, muestra la ganancia y las decisiones óptimas
    if modelo.status == GRB.OPTIMAL:
        print('------------------------------------------------------')
        print(f'Ganancias del taller en un día: {modelo.objVal:.2f}€')
        print(f'Modificaciones de {X1.VarName}: {int(X1.X)}')
        print(f'Modificaciones de {X2.VarName}: {int(X2.X)}')
        print(f'Modificaciones de {X3.VarName}: {int(X3.X)}')
        print(f'Modificaciones de {X4.VarName}: {int(X4.X)}')
        print(f'Modificaciones de {X5.VarName}: {int(X5.X)}')
        print(f'Modificaciones de {X6.VarName}: {int(X6.X)}')
        print(f'Modificaciones de {X7.VarName}: {int(X7.X)}')
    else:
        print('No se ha encontrado una solución óptima')

# Si el script se ejecuta como principal, llama a la función 'main' con el archivo de datos 'Inst1.txt'
if __name__ == "__main__":
    archivo = 'Inst1.txt'  # Nombre del archivo con datos de entrada
    main(archivo)
