import numpy as np
import matplotlib.pyplot as plt
from collections import deque

def importar(nombre):
    with open(nombre, 'r') as f:
        lineas = f.readlines()

    # Elimina líneas vacías y espacios extra
    lineas = [linea.strip() for linea in lineas if linea.strip()]

    # Convertir las tres primeras líneas a enteros
    lmrate = int(lineas[0])
    murate = int(lineas[1])
    numcustom = int(lineas[2])
    priority= int(lineas[3])
    k=int(lineas[4])

    return lmrate, murate, numcustom, priority,k

##Cola para el analisis del coche

def mm1_prioridad(tasa_llegadas, tasa_reparacion, num_vehiculos, niveles_prioridad):
    # Generar tiempos entre llegadas, tiempos de reparación y prioridades
    tiempos_entre_llegadas = np.random.exponential(1 / tasa_llegadas, num_vehiculos)
    tiempos_reparacion = np.random.exponential(1 / tasa_reparacion, num_vehiculos)
    prioridades = np.random.choice(range(niveles_prioridad), size=num_vehiculos)  # Ejemplo de distribución

    # Calcular tiempos de llegada acumulativos
    tiempos_llegada = np.cumsum(tiempos_entre_llegadas)

    # Inicializar matrices para tiempos de servicio
    inicio_reparacion = np.zeros(num_vehiculos)
    fin_reparacion = np.zeros(num_vehiculos)
    tiempos_espera = np.zeros(num_vehiculos)

    # Inicializar colas para cada nivel de prioridad
    colas_prioridad = [deque() for _ in range(niveles_prioridad)]

    # Inicializar tiempo de disponibilidad del taller
    tiempo_libre_taller = 0

    # Inicializar índice de llegada
    i = 0

    while i < num_vehiculos or any(colas_prioridad[nivel] for nivel in range(niveles_prioridad)):
        if i < num_vehiculos and tiempos_llegada[i] <= tiempo_libre_taller:
            # Añadir vehículo a la cola correspondiente
            colas_prioridad[prioridades[i]].append(i)
            i += 1
        else:
            if any(colas_prioridad[nivel] for nivel in range(niveles_prioridad)):
                # Encontrar la cola con la prioridad más alta disponible
                for nivel in range(niveles_prioridad):
                    if colas_prioridad[nivel]:
                        siguiente_vehiculo = colas_prioridad[nivel].popleft()
                        break

                # Asignar tiempos de reparación
                inicio_reparacion[siguiente_vehiculo] = max(tiempos_llegada[siguiente_vehiculo], tiempo_libre_taller)
                tiempos_espera[siguiente_vehiculo] = inicio_reparacion[siguiente_vehiculo] - tiempos_llegada[siguiente_vehiculo]
                fin_reparacion[siguiente_vehiculo] = inicio_reparacion[siguiente_vehiculo] + tiempos_reparacion[siguiente_vehiculo]

                # Actualizar tiempo libre del taller
                tiempo_libre_taller = fin_reparacion[siguiente_vehiculo]
            else:
                if i < num_vehiculos:
                    # Avanzar el tiempo al siguiente evento de llegada
                    tiempo_libre_taller = tiempos_llegada[i]
                else:
                    break

    # Calcular tiempos en el sistema
    tiempos_en_taller = fin_reparacion - tiempos_llegada

    # Calcular utilización del taller
    uso_taller = np.sum(tiempos_reparacion) / fin_reparacion[-1] if fin_reparacion[-1] > 0 else 0

    return  tiempos_en_taller,tiempos_espera,prioridades, uso_taller, fin_reparacion,prioridades


# Cola para la reparación del vehículo con capacidad limitada
def mm1k(inicio_reparacion, tasa_reparacion, capacidad_taller):
    num_vehiculos = len(inicio_reparacion)
    tiempos_reparacion = np.random.exponential(1 / tasa_reparacion, num_vehiculos)

    # Inicializar matrices para tiempos de servicio
    inicio_reparacion_real = np.zeros(num_vehiculos)
    fin_reparacion = np.zeros(num_vehiculos)
    tiempos_espera = np.zeros(num_vehiculos)

    # Inicializar cola del taller
    cola_taller = deque()
    tiempo_libre_taller = 0
    vehiculos_rechazados = 0

    for i in range(num_vehiculos):
        # Verificar si el vehículo puede ingresar al sistema
        if len(cola_taller) < capacidad_taller:
            cola_taller.append(i)  # Añadir a la cola
        else:
            # Vehículo rechazado por falta de espacio
            vehiculos_rechazados += 1
            continue

        # Procesar vehículo si el taller está libre
        if tiempo_libre_taller <= inicio_reparacion[i]:
            vehiculo_actual = cola_taller.popleft()

            # Asignar tiempos de reparación
            inicio_reparacion_real[vehiculo_actual] = max(inicio_reparacion[vehiculo_actual], tiempo_libre_taller)
            tiempos_espera[vehiculo_actual] = inicio_reparacion_real[vehiculo_actual] - inicio_reparacion[vehiculo_actual]
            fin_reparacion[vehiculo_actual] = inicio_reparacion_real[vehiculo_actual] + tiempos_reparacion[vehiculo_actual]

            # Actualizar tiempo libre del taller
            tiempo_libre_taller = fin_reparacion[vehiculo_actual]

    # Calcular métricas
    tiempos_en_taller = inicio_reparacion+tiempos_reparacion
    uso_taller = np.sum(tiempos_reparacion) / num_vehiculos
    return tiempos_espera, tiempos_en_taller, vehiculos_rechazados, uso_taller


if __name__ == "__main__":
    instancia='Inst1.txt'
    #instancia = 'Inst2.txt'
    lambda_rate, mu_rate, num_customers, priority, k = importar(instancia)


print("-----------------MM1/COLA DE ANALISIS DE VEHICULOS-----------------\n")
tiempos_en_taller,tiempos_espera,prioridades, uso_taller, fin_analisis,prioridades=mm1_prioridad(lambda_rate, mu_rate, num_customers,priority)
print(f"Tiempo de espera promedio en cola de analisis: {np.mean(tiempos_espera):.2f} horas")
print(f"Tiempo promedio en el sistema de analisis: {np.mean(tiempos_en_taller):.2f} horas")
print(f"Utilización del taller de analisis: {uso_taller:.2%}\n")

high_priority_indices = np.where(prioridades == 0)[0]
low_priority_indices = np.where(prioridades == 1)[0]
#Metricas para la creacion de grafico
wait_times_high = tiempos_espera[high_priority_indices]
system_times_high = tiempos_en_taller[high_priority_indices]
wait_times_low = tiempos_espera[low_priority_indices]
system_times_low = tiempos_en_taller[low_priority_indices]
#Distribucion de tiempos de espera de reparacion
plt.figure(figsize=(12, 8))
plt.hist(wait_times_high, bins=50, density=True, edgecolor='black', alpha=0.7, label='Prioridad Alta')
plt.hist(wait_times_low, bins=50, density=True, edgecolor='black', alpha=0.5, label='Prioridad Baja')
plt.title('Distribución de tiempos de espera en cola por prioridad de Analisis')
plt.xlabel('Tiempo de espera en el taller (horas)')
plt.ylabel('Densidad de probabilidad')
plt.legend()
plt.grid(True)
plt.show()

# Tiempos en el sistema de analisis
plt.figure(figsize=(12, 8))
plt.hist(system_times_high, bins=50, density=True, edgecolor='black', alpha=0.7, label='Prioridad Alta')
plt.hist(system_times_low, bins=50, density=True, edgecolor='black', alpha=0.5, label='Prioridad Baja')
plt.title('Distribución de tiempos en el sistema por prioridad en cola de analisis')
plt.xlabel('Tiempo en el sistema (horas)')
plt.ylabel('Densidad de probabilidad')
plt.legend()
plt.grid(True)
plt.show()


print("-----------------MM1K/COLA DE REPARACION DE VEHICULOS-----------------\n")
tiempos_espera_mm1k, tiempos_en_taller_mm1k, vehiculos_rechazados, uso_taller_mm1k=mm1k(fin_analisis, mu_rate, k)
print(f"Tiempo de espera promedio en cola de Reparacion: {np.mean(tiempos_espera_mm1k):.2f} horas")
print(f"Tiempo promedio en el sistema de Reparacion: {np.mean(tiempos_en_taller_mm1k):.2f} horas")
print(f"Utilización del taller de reparaciones: {uso_taller_mm1k:.2%}")
print(f'Numero de clientes rechazados para reparacion: {vehiculos_rechazados} vehiculos')

high_priority_indices = np.where(prioridades == 0)[0]
low_priority_indices = np.where(prioridades == 1)[0]

wait_times_high = tiempos_espera_mm1k[high_priority_indices]
system_times_high = tiempos_en_taller_mm1k[high_priority_indices]

wait_times_low = tiempos_espera_mm1k[low_priority_indices]
system_times_low = tiempos_en_taller_mm1k[low_priority_indices]
#Distribucion de tiempos de espera de reparacion
plt.figure(figsize=(12, 8))
plt.hist(wait_times_high, bins=50, density=True, edgecolor='black', alpha=0.7, label='Prioridad Alta')
plt.hist(wait_times_low, bins=50, density=True, edgecolor='black', alpha=0.5, label='Prioridad Baja')
plt.title('Distribución de tiempos de espera en cola por prioridad de Reparacion')
plt.xlabel('Tiempo de espera en el taller (horas)')
plt.ylabel('Densidad de probabilidad')
plt.legend()
plt.grid(True)
plt.show()

# Tiempos en el sistema de reparacion
plt.figure(figsize=(12, 8))
plt.hist(system_times_high, bins=50, density=True, edgecolor='black', alpha=0.7, label='Prioridad Alta')
plt.hist(system_times_low, bins=50, density=True, edgecolor='black', alpha=0.5, label='Prioridad Baja')
plt.title('Distribución de tiempos en el sistema por prioridad en cola de Reparacion')
plt.xlabel('Tiempo en el sistema (horas)')
plt.ylabel('Densidad de probabilidad')
plt.legend()
plt.grid(True)
plt.show()

