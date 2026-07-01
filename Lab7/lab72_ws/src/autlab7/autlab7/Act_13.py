import numpy as np
import matplotlib.pyplot as plt

def kalman_1d(datos, Q=0.001, R=0.01, x0=None, P0=1.0, graficar=True):
    """
    Filtro de Kalman 1D para suavizar medidas de un sensor.
    
    Parámetros:
    -----------
    datos : list o array
        Vector de medidas del sensor.
    Q : float, opcional
        Varianza del ruido de proceso (incertidumbre del modelo).
    R : float, opcional
        Varianza del ruido de medición (incertidumbre del sensor).
    x0 : float, opcional
        Estimación inicial del estado. Si es None, se usa el primer dato.
    P0 : float, opcional
        Covarianza inicial del error.
    graficar : bool, opcional
        Si es True, muestra la gráfica con medidas y filtro.
    
    Retorna:
    --------
    x_filt : numpy.ndarray
        Vector con las estimaciones filtradas.
    P_filt : numpy.ndarray
        Vector con las covarianzas del error posteriores.
    """
    datos = np.asarray(datos, dtype=float)
    N = len(datos)
    
    # Inicialización
    if x0 is None:
        x0 = datos[0]
    x_est = x0          # estado posterior inicial
    P_est = P0          # covarianza posterior inicial
    
    # Arreglos para guardar historial
    x_filt = np.zeros(N)
    P_filt = np.zeros(N)
    
    for k, z in enumerate(datos):
        # --- Predicción ---
        x_pri = x_est          # x_k|k-1 = x_{k-1|k-1} (modelo de posición constante)
        P_pri = P_est + Q      # P_k|k-1 = P_{k-1|k-1} + Q
        
        # --- Actualización ---
        K = P_pri / (P_pri + R)        # Ganancia de Kalman
        x_est = x_pri + K * (z - x_pri) # Estado corregido
        P_est = (1 - K) * P_pri        # Covarianza corregida
        
        # Guardar
        x_filt[k] = x_est
        P_filt[k] = P_est
    
    # Gráfica
    if graficar:
        plt.figure(figsize=(10, 6))
        plt.plot(datos, 'ro', markersize=6, label='Medidas del sensor', alpha=0.7)
        plt.plot(x_filt, 'b-', linewidth=2, label='Filtro de Kalman')
        # Banda de incertidumbre (±1 desviación)
        sigma = np.sqrt(P_filt)
        plt.fill_between(range(N), x_filt - sigma, x_filt + sigma, 
                         color='blue', alpha=0.2, label='Incertidumbre ±1σ')
        plt.xlabel('Muestra')
        plt.ylabel('Distancia (m)')
        plt.title('Filtro de Kalman 1D para sensor infrarrojo')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    return x_filt, P_filt



if __name__ == "__main__":
    datos = [1.078223348, 1.06437695, 1.06437695, 1.06689477, 1.06689477,
             1.064172983, 1.064172983, 1.072478294, 1.072478294, 1.063647151,
             1.063647151, 1.083568573, 1.083568573, 1.077025175, 1.077025175,
             1.077238083, 1.077238083, 1.073259234, 1.073259234, 1.078526378]
    
    # Q grande -> el filtro confía menos en el modelo (sigue más a las medidas)
    # R grande -> el filtro confía menos en las medidas (suaviza más)
    x_filt, P_filt = kalman_1d(datos, Q=0.0005, R=0.005)