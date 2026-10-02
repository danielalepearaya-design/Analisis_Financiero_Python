# -*- coding: utf-8 -*-

"""
PROYECTO FINAL - FINANZAS EN PYTHON
Profesor: Guillermo Yañez

Herramienta de análisis de rentabilidad y riesgo financiero

La aplicación nos permitira:
    - Seleccionar un activo financiero.
    - Definir un período de análisis.
    - Descargar precios históricos.
    - Calcular retornos diarios.
    - Calcular indicadores de rentabilidad.
    - Calcular indicadores de riesgo.
    - Calcular VaR histórico.
    - Calcular Drawdown máximo.
    - Clasificar el nivel de riesgo.
    - Visualizar gráficamente los resultados.

Autor: Daniela Lepe
"""
#%%
import site
import sys

# Agregamos la carpeta donde está instalado yfinance,
# para poder ocupar esa libreria

ruta = site.getusersitepackages()

if ruta not in sys.path:
    sys.path.append(ruta)
    
#%%
# =============================================================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# =============================================================================

import tkinter as tk
from tkinter import ttk, messagebox

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#%%

# =============================================================================
# 2. FUNCIONES DE ANÁLISIS FINANCIERO
# =============================================================================

def descargar_datos(ticker, fecha_inicio, fecha_fin):
    """
    Descarga los precios históricos de un activo financiero.
    ----------
    ticker : str
        Símbolo del activo financiero utilizado por Yahoo Finance.

    fecha_inicio : str
        Fecha inicial del período en formato AAAA-MM-DD. - universal

    fecha_fin : str
        Fecha final del período en formato AAAA-MM-DD.

    Returns
    -------
    pandas.DataFrame
        DataFrame con los precios históricos descargados.
    """

    datos = yf.download(
        ticker,
        start=fecha_inicio,
        end=fecha_fin,
        auto_adjust=False,
        progress=False
    )

    return datos
#%%

def preparar_precios(datos):
    """
    Extrae y limpia la serie de precios de cierre.
    
    ----------
    datos : pandas.DataFrame
        Datos históricos descargados desde Yahoo Finance.

    Returns
    -------
    pandas.Series
        Serie de precios de cierre sin valores nulos.
    """

    precios = datos["Close"]

    if isinstance(precios, pd.DataFrame):
        precios = precios.iloc[:, 0]

    precios = precios.dropna()

    return precios

#%%

def calcular_retornos(precios):
    """
    Calcula los retornos diarios del activo financiero.
    
    ----------
    precios : pandas.Series
        Serie histórica de precios de cierre.

    Returns
    -------
    pandas.Series
        Serie de retornos diarios.
    """

    retornos = precios.pct_change().dropna()

    return retornos

#%%

def calcular_indicadores(precios, retornos):
    """
    Calcula indicadores de rentabilidad y riesgo financiero.

    ----------
    precios : pandas.Series
        Serie histórica de precios.

    retornos : pandas.Series
        Serie de retornos diarios.

    Returns
    -------
    dict
        Diccionario con los principales indicadores financieros.

    TENER PRESENTE:
    Para el cálculo de la volatilidad anualizada se consideran
    aprox 252 días de negociación por año.
    """

    precio_inicial = float(precios.iloc[0])
    precio_final = float(precios.iloc[-1])

    # Rentabilidad acumulada durante todo el período.
    rentabilidad_acumulada = (precio_final / precio_inicial) - 1

    # Retorno promedio diario.
    retorno_promedio = float(retornos.mean())

    # Volatilidad diaria.
    volatilidad_diaria = float(retornos.std())

    # Volatilidad anualizada.
    volatilidad_anualizada = (
        volatilidad_diaria * np.sqrt(252)
    )

    # Retorno anualizado.
    retorno_anualizado = (
        (1 + retorno_promedio) ** 252) - 1

    # Mejor y peor retorno diario.
    mejor_dia = float(retornos.max())
    peor_dia = float(retornos.min())

    # VaR histórico al 95%.
    var_95 = float(retornos.quantile(0.05))

    indicadores = {
        "precio_inicial": precio_inicial,
        "precio_final": precio_final,
        "rentabilidad_acumulada": rentabilidad_acumulada,
        "retorno_promedio": retorno_promedio,
        "volatilidad_diaria": volatilidad_diaria,
        "volatilidad_anualizada": volatilidad_anualizada,
        "retorno_anualizado": retorno_anualizado,
        "mejor_dia": mejor_dia,
        "peor_dia": peor_dia,
        "var_95": var_95
    }

    return indicadores

#%%
def calcular_drawdown(retornos):
    """
    Calcula el Drawdown histórico del activo.

    ----------
    retornos : pandas.Series
        Serie de retornos diarios.

    Returns
    -------
    pandas.Series
        Serie histórica de Drawdown.

    -----
    El Drawdown representa la caída porcentual desde un máximo
    histórico alcanzado por la inversión acumulada.
    """

    riqueza_acumulada = (1 + retornos).cumprod()

    maximo_acumulado = riqueza_acumulada.cummax()

    drawdown = (
        riqueza_acumulada / maximo_acumulado) - 1

    return drawdown

#%%

def clasificar_riesgo(volatilidad_anualizada):
    """
    Clasificamos el nivel de riesgo del activo.
    
    ----------
    volatilidad_anualizada : float
        Volatilidad anualizada del activo.

    Returns
    -------
        Nivel de riesgo: Bajo, Medio o Alto.
        
    """

    if volatilidad_anualizada < 0.20:
        return "BAJO"

    elif volatilidad_anualizada < 0.35:
        return "MEDIO"

    else:
        return "ALTO"
    
#%%

# =============================================================================
# 3. AJUSTAMOS LOS RESULTADOS
# =============================================================================

def formato_porcentaje(valor, decimales=2):
    """
    Convertiremos un valor decimal a porcentaje para mostrarlo en pantalla.
    ----------
    valor : float
        Valor decimal que se desea convertir.

    decimales : int
        Número de decimales a mostrar.

    Returns
    -------
        Valor expresado como porcentaje.
        
    """

    return f"{valor * 100:.{decimales}f}%"

#%%

def actualizar_tabla(indicadores, drawdown_maximo, nivel_riesgo):
    """
    Actualizamos la tabla de resultados de la App.

    ----------
    indicadores : dict
        Diccionario con los indicadores financieros.

    drawdown_maximo : float
        Drawdown máximo registrado.

    nivel_riesgo : str
        Clasificación del nivel de riesgo.

    Returns
    una tabla actualizada
    ----------
    """
# Este codigo va a borrar todos los elementos vizuales de la tabla 
    for item in tabla.get_children():
        tabla.delete(item)

    resultados = [
        ("Precio inicial", f"${indicadores['precio_inicial']:,.2f}"),
        ("Precio final", f"${indicadores['precio_final']:,.2f}"),
        (
            "Rentabilidad acumulada",
            formato_porcentaje(
                indicadores["rentabilidad_acumulada"]
            )
        ),
        (
            "Retorno promedio diario",
            formato_porcentaje(
                indicadores["retorno_promedio"],
                4
            )
        ),
        (
            "Retorno anualizado",
            formato_porcentaje(
                indicadores["retorno_anualizado"]
            )
        ),
        (
            "Volatilidad diaria",
            formato_porcentaje(
                indicadores["volatilidad_diaria"],
                4
            )
        ),
        (
            "Volatilidad anualizada",
            formato_porcentaje(
                indicadores["volatilidad_anualizada"]
            )
        ),
        (
            "Mejor día",
            formato_porcentaje(
                indicadores["mejor_dia"]
            )
        ),
        (
            "Peor día",
            formato_porcentaje(
                indicadores["peor_dia"]
            )
        ),
        (
            "VaR histórico 95%",
            formato_porcentaje(
                indicadores["var_95"]
            )
        ),
        (
            "Drawdown máximo",
            formato_porcentaje(
                drawdown_maximo
            )
        ),
        ("Nivel de riesgo", nivel_riesgo)
    ]

    for indicador, resultado in resultados:
        tabla.insert(
            "",
            "end",
            values=(indicador, resultado)
        )

#%%

# =============================================================================
# 4. FUNCIÓN PARA GENERAR LOS GRÁFICOS
# =============================================================================

def mostrar_graficos(precios, retornos, drawdown, ticker):
    """
    Genera los gráficos financieros dentro de la ventana principal.

    ----------
    precios : pandas.Series
        Serie de precios de cierre.

    retornos : pandas.Series
        Serie de retornos diarios.

    drawdown : pandas.Series
        Serie de Drawdown.

    ticker : str
        Símbolo del activo analizado.

    Returns
    -------
    
    """

    # Eliminar gráficos anteriores.
    for widget in frame_graficos.winfo_children():
        widget.destroy()

    # Crear figura con cuatro gráficos.
    figura, ejes = plt.subplots(
        2,
        2,
        figsize=(11, 7)
    )

#%%
# -------------------------------------------------------------------------
# Gráfico 1: Precio de cierre
# -------------------------------------------------------------------------

    ejes[0, 0].plot(
        precios.index,
        precios.values
    )

    ejes[0, 0].set_title(
        f"Evolución del precio - {ticker}"
    )

    ejes[0, 0].set_xlabel("Fecha")
    ejes[0, 0].set_ylabel("Precio")
    ejes[0, 0].grid(True)

#%%
# -------------------------------------------------------------------------
# Gráfico 2: Retornos diarios
# -------------------------------------------------------------------------

    ejes[0, 1].plot(
        retornos.index,
        retornos.values
    )

    ejes[0, 1].axhline(
        y=0,
        linestyle="--"
    )

    ejes[0, 1].set_title(
        "Retornos diarios"
    )

    ejes[0, 1].set_xlabel("Fecha")
    ejes[0, 1].set_ylabel("Retorno")
    ejes[0, 1].grid(True)

#%%

# -------------------------------------------------------------------------
# Gráfico 3: Rentabilidad acumulada
# -------------------------------------------------------------------------

    rentabilidad_acumulada = (
        (1 + retornos).cumprod()
    ) - 1

    ejes[1, 0].plot(
        rentabilidad_acumulada.index,
        rentabilidad_acumulada.values
    )

    ejes[1, 0].axhline(
        y=0,
        linestyle="--"
    )

    ejes[1, 0].set_title(
        "Rentabilidad acumulada"
    )

    ejes[1, 0].set_xlabel("Fecha")
    ejes[1, 0].set_ylabel("Rentabilidad")
    ejes[1, 0].grid(True)


# -------------------------------------------------------------------------
# Gráfico 4: Drawdown
# -------------------------------------------------------------------------

    ejes[1, 1].plot(
        drawdown.index,
        drawdown.values
    )

    ejes[1, 1].axhline(
        y=0,
        linestyle="--"
    )

    ejes[1, 1].set_title(
        "Drawdown histórico"
    )

    ejes[1, 1].set_xlabel("Fecha")
    ejes[1, 1].set_ylabel("Drawdown")
    ejes[1, 1].grid(True)


    figura.tight_layout()

 # Insertar la figura de Matplotlib dentro de Tkinter.
    canvas = FigureCanvasTkAgg(
        figura,
        master=frame_graficos
    )

    canvas.draw()

    canvas.get_tk_widget().pack(
        fill=tk.BOTH,
        expand=True
    )

#%%
# =============================================================================
# 5. FUNCIÓN DE ANÁLISIS
# =============================================================================

def analizar_activo():
    """
    Ejecuta el análisis financiero completo del activo seleccionado.

    La función:
        1. Obtiene los parámetros ingresados.
        2. Descarga los datos históricos.
        3. Valida la información.
        4. Calcula retornos.
        5. Calcula indicadores financieros.
        6. Calcula Drawdown.
        7. Clasifica el nivel de riesgo.
        8. Actualiza la tabla.
        9. Genera los gráficos.

    Returns
    -------
        Actualizara la interfaz gráfica con los resultados.
    """

    ticker = entrada_ticker.get().strip().upper()
    fecha_inicio = entrada_inicio.get().strip()
    fecha_fin = entrada_fin.get().strip()

# -------------------------------------------------------------------------
# Validación de campos
# -------------------------------------------------------------------------

    if not ticker:
        messagebox.showwarning(
            "Dato faltante",
            "Ingrese el ticker del activo financiero."
        )
        return

    if not fecha_inicio or not fecha_fin:
        messagebox.showwarning(
            "Datos faltantes",
            "Ingrese ambas fechas."
        )
        return

# -------------------------------------------------------------------------
# Descarga de datos
# -------------------------------------------------------------------------

    try:

        datos = descargar_datos(
            ticker,
            fecha_inicio,
            fecha_fin
        )

    except Exception as error:

        messagebox.showerror(
            "Error",
            f"No fue posible descargar los datos.\n\n{error}"
        )

        return

# -------------------------------------------------------------------------
# Validación de datos descargados
# -------------------------------------------------------------------------

    if datos.empty:

        messagebox.showerror(
            "Sin datos",
            "No se encontraron datos para el activo "
            f"{ticker} en el período seleccionado."
        )

        return

#%%
# -------------------------------------------------------------------------
# Preparación de precios
# -------------------------------------------------------------------------

    precios = preparar_precios(datos)

    if len(precios) < 2:

        messagebox.showerror(
            "Datos insuficientes",
            "No existen suficientes datos para realizar "
            "el análisis financiero."
        )

        return
#%%

# -------------------------------------------------------------------------
# Cálculo de retornos
# -------------------------------------------------------------------------

    retornos = calcular_retornos(precios)

# -------------------------------------------------------------------------
# Cálculo de indicadores
# -------------------------------------------------------------------------

    indicadores = calcular_indicadores(precios, retornos)

# -------------------------------------------------------------------------
# Cálculo de Drawdown
# -------------------------------------------------------------------------

    drawdown = calcular_drawdown(retornos)

    drawdown_maximo = float(drawdown.min())
        

# -------------------------------------------------------------------------
# Clasificación de riesgo
# -------------------------------------------------------------------------

    nivel_riesgo = clasificar_riesgo(
        indicadores["volatilidad_anualizada"])

# -------------------------------------------------------------------------
# Actualización de la interfaz
# -------------------------------------------------------------------------

    actualizar_tabla(
        indicadores,
        drawdown_maximo,
        nivel_riesgo)

    mostrar_graficos(
        precios,
        retornos,
        drawdown,
        ticker)

# -------------------------------------------------------------------------
# Actualización del mensaje de estado
# -------------------------------------------------------------------------

    estado.set(
        f"Análisis completado correctamente: {ticker}"
        )
#%%

# =============================================================================
# 6. CONFIGURACIÓN DE LA VENTANA PRINCIPAL
# =============================================================================
""" 
Subo el Icono que cree para al APP
"""

ventana = tk.Tk()
ventana.iconbitmap(r"C:\Users\secre\.spyder-py3\Finanzas_phyton\INFORME FINAL - DANIELA LEPE\icon_DL.ico")

ventana.title(
    "Análisis Financiero - Daniela Lepe")
ventana.geometry("1250x850")
ventana.minsize(1000, 700)

#%%

# =============================================================================
# 7. TÍTULO DE LA APLICACIÓN
# =============================================================================

titulo = ttk.Label(
    ventana,
    text="Herramienta Análisis Financiero",
    font=("Arial", 20, "bold"))
titulo.pack(pady=15)


subtitulo = ttk.Label(
    ventana,
    text=(
        "Análisis de rentabilidad y riesgo "
        "de activos financieros"),
    font=("Arial", 11))
subtitulo.pack(pady=(0, 15))

#%%
# =============================================================================
# 8. PANEL DE PARÁMETROS
# =============================================================================

frame_parametros = ttk.LabelFrame(ventana,text="Parámetros del análisis",
    padding=10)

frame_parametros.pack(fill=tk.X,padx=20,pady=5)


# -------------------------------------------------------------------------
# Ticker
# -------------------------------------------------------------------------

ttk.Label(frame_parametros,text="Ticker:").grid(
    row=0,
    column=0,
    padx=5,
    pady=5
)

entrada_ticker = ttk.Entry(frame_parametros,width=18)

entrada_ticker.grid(
    row=0,
    column=1,
    padx=5,
    pady=5
)

entrada_ticker.insert(
    0,
    "COPEC.SN"
)


# -------------------------------------------------------------------------
# Fecha de inicio
# -------------------------------------------------------------------------

ttk.Label(
    frame_parametros,
    text="Fecha inicio:"
).grid(
    row=0,
    column=2,
    padx=5,
    pady=5
)

entrada_inicio = ttk.Entry(
    frame_parametros,
    width=15
)

entrada_inicio.grid(
    row=0,
    column=3,
    padx=5,
    pady=5
)

entrada_inicio.insert(
    0,
    "2020-01-01"
)


# -------------------------------------------------------------------------
# Fecha de término
# -------------------------------------------------------------------------

ttk.Label(frame_parametros,text="Fecha término:").grid(
    row=0,
    column=4,
    padx=5,
    pady=5
)

entrada_fin = ttk.Entry(
    frame_parametros,
    width=15
)

entrada_fin.grid(
    row=0,
    column=5,
    padx=5,
    pady=5
)

entrada_fin.insert(
    0,
    "2026-01-01"
)

#%%

# =============================================================================
# 9. BOTÓN DE ANÁLISIS
# =============================================================================

boton_analizar = ttk.Button(
    frame_parametros,
    text="ANALIZAR ACTIVO",
    command = analizar_activo)

boton_analizar.grid(
    row=0,
    column=6,
    padx=15,
    pady=5
)

#%%

# =============================================================================
# 10. PANEL DE RESULTADOS
# =============================================================================

frame_resultados = ttk.LabelFrame(
    ventana,
    text="Indicadores financieros",
    padding=10
)

frame_resultados.pack(
    fill=tk.X,
    padx=20,
    pady=10
)


# -------------------------------------------------------------------------
# Tabla de resultados
# -------------------------------------------------------------------------


tabla = ttk.Treeview(
    frame_resultados,
    columns=("Indicador", "Resultado"),
    show="headings",
    height=7
)

tabla.heading(
    "Indicador",
    text="Indicador"
)

tabla.heading(
    "Resultado",
    text="Resultado"
)

tabla.column(
    "Indicador",
    width=300
)

tabla.column(
    "Resultado",
    width=200
)

tabla.pack(
    fill=tk.X
)

#%%
# =============================================================================
# 11. PANEL DE GRÁFICOS
# =============================================================================

frame_graficos = ttk.LabelFrame(
    ventana,
    text="Visualización financiera",
    padding=5
)

frame_graficos.pack(
    fill=tk.BOTH,
    expand=True,
    padx=20,
    pady=5
)

#%%
# =============================================================================
# 12. BARRA DE ESTADO
# =============================================================================

estado = tk.StringVar()

estado.set(
    "Ingrese los parámetros y presione 'Analizar activo'."
)

barra_estado = ttk.Label(
    ventana,
    textvariable=estado,
    relief=tk.SUNKEN,
    anchor=tk.W
)

barra_estado.pack(
    fill=tk.X,
    side=tk.BOTTOM
)

#%%
# =============================================================================
# 13. EJECUCIÓN DE LA APLICACIÓN
# =============================================================================

ventana.mainloop()

