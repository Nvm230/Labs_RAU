import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

datos = [1.078223348, 1.06437695, 1.06437695, 1.06689477, 1.06689477, 1.064172983, 1.064172983, 1.072478294, 1.072478294, 1.063647151, 1.063647151, 1.083568573, 1.083568573, 1.077025175, 1.077025175, 1.077238083, 1.077238083, 1.073259234, 1.073259234, 1.078526378 ]

media, sigma = np.mean(datos), np.std(datos, ddof=1)
x = np.linspace(media - 4*sigma, media + 4*sigma, 1000)
y_campana = norm.pdf(x, media, sigma)

plt.figure(figsize=(10, 6))
plt.plot(x, y_campana, 'b-', lw=2)

plt.axvspan(media - sigma, media + sigma, alpha=0.2, color='red')

datos_ordenados = np.sort(datos)
y_puntos = norm.pdf(datos_ordenados, media, sigma)
plt.scatter(datos_ordenados, y_puntos, color='green', s=50, zorder=5)

plt.xlabel('Valor')
plt.ylabel('Densidad')
plt.title(f'Campana: μ={media:.3f}, σ²={1e3 * sigma**2:.3f} * 1e-3')
plt.grid(True, alpha=0.3)
plt.show()