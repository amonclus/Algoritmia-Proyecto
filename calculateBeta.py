import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Cargar los datos
df = pd.read_csv('N=1000.csv')

def power_law(x, a, beta):
    """Función de ley de potencias para el ajuste."""
    return a * (x ** beta)

def calculate_beta(df, pc=0.5, pc_max=0.57, points=20):
    """
    Calcula el exponente crítico Beta usando regresión en escala log-log
    con pc fijo en 0.5. También calcula el error en el ajuste.
    """
    print(f"Punto crítico (pc): {pc}")
    
    # Seleccionar datos por encima de pc para el ajuste
    mask = (df['q'] >= pc) & (df['q'] <= pc_max)
    data_fit = df[mask].copy()
    
    # Calcular |p - pc| y preparar datos para el ajuste
    data_fit['p_pc'] = data_fit['q'] - pc
    
    # Filtrar puntos con p > pc y convertir a arrays para el ajuste
    mask_nonzero = data_fit['p_pc'] > 0
    x_data = data_fit.loc[mask_nonzero, 'p_pc'].values
    y_data = (data_fit.loc[mask_nonzero, 'Tamaño Clúster Mayor']/1000000).values
    
    # Ajustar con curve_fit para obtener tanto el valor de beta como su error
    try:
        popt, pcov = curve_fit(power_law, x_data, y_data)
        a, beta = popt
        beta_err = np.sqrt(np.diag(pcov))[1]
        
        print(f"Exponente crítico Beta: {beta:.4f} ± {beta_err:.4f}")
    except RuntimeError:
        print("No se pudo encontrar el ajuste óptimo.")
        return None, None
    
    # Visualización
    plt.figure(figsize=(10, 6))
    
    # Datos originales
    plt.plot(df['q'], df['Tamaño Clúster Mayor']/1000000, 'b.', label='Datos originales')
    
    # Ajuste de ley de potencias
    x_fit = np.linspace(pc, pc_max, 100)
    y_fit = power_law(x_fit - pc, a, beta)
    plt.plot(x_fit, y_fit, 'r-', label=f'Ajuste: β = {beta:.4f}')
    
    plt.axvline(pc, color='g', linestyle='--', label=f'pc = {pc}')
    plt.xlabel('p')
    plt.ylabel('S_max/N')
    plt.legend()
    plt.title('Determinación del Exponente Crítico β')
    plt.grid(True)
    
    # Plot en escala log-log
    plt.figure(figsize=(10, 6))
    plt.plot(x_data, y_data, 'b.', label='Datos')
    plt.plot(x_fit - pc, power_law(x_fit - pc, a, beta), 'r-', 
             label=f'Ajuste: β = {beta:.4f}')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('|p - pc|')
    plt.ylabel('S_max/N')
    plt.legend()
    plt.title('Ajuste del Exponente Crítico β (escala log-log)')
    plt.grid(True)
    
    # Imprimir detalles del ajuste
    print("\nDetalles del ajuste:")
    print(f"Número de puntos usados: {len(x_data)}")
    print(f"Rango de ajuste: {min(x_data):.4f} ≤ |p-pc| ≤ {max(x_data):.4f}")
    print(f"Factor pre-exponencial (A): {a:.4f}")
    
    return beta, beta_err

# Calcular el exponente crítico
beta, beta_err = calculate_beta(df)
plt.show()