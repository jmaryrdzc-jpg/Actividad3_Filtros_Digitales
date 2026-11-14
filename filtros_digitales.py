"""Actividad formativa 3 — Señales y Sistemas, Universidad Ciudadana de Nuevo León.

Simula una señal compuesta (5, 40 y 120 Hz) con ruido blanco y compara
filtros digitales pasa bajos, pasa altos y pasa bandas, tanto FIR como IIR.

Ejecutar:
    python filtros_digitales.py

Produce figuras PNG y tablas CSV en carpetas figuras/ y datos/.
Se utiliza filtrado de fase cero para comparación FUERA DE LÍNEA (no tiempo real).
"""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

FS = 500                           # muestras/segundo (Hz)
DURACION = 4.0                    # segundos
FRECUENCIAS = (5.0, 40.0, 120.0)  # tonos de la señal
AMPLITUDES = (0.90, 0.65, 0.45)
DESV_RUIDO = 0.35
SEMILLA = 2026                    # permite reproducir el ejemplo
ORDEN_IIR = 4                     # Butterworth, orden base (en banda se duplica)
COEF_FIR = 101                    # coeficientes de FIR con ventana Hamming
CORTES = {'Pasa bajos': 15.0, 'Pasa altos': 80.0, 'Pasa bandas': (30.0, 60.0)}
TIPOS = {'Pasa bajos': 'lowpass', 'Pasa altos': 'highpass', 'Pasa bandas': 'bandpass'}
FREQUENCIA_OBJETIVO = {'Pasa bajos': 5.0, 'Pasa altos': 120.0, 'Pasa bandas': 40.0}
COLOR = {'entrada': '#8795a7', 'IIR': '#087f8c', 'FIR': '#ec7b17'}
BASE = Path(__file__).resolve().parent
FIG = BASE / 'figuras'
DAT = BASE / 'datos'
FIG.mkdir(parents=True, exist_ok=True)
DAT.mkdir(parents=True, exist_ok=True)


def db(magnitud: np.ndarray | float) -> np.ndarray | float:
    """Convierte una ganancia lineal a dB, con protección del log(0)."""
    return 20 * np.log10(np.maximum(np.abs(magnitud), 1e-12))


def senal_compuesta() -> tuple[np.ndarray, np.ndarray, dict[float, np.ndarray]]:
    """Produce la misma señal de prueba en todas las corridas."""
    tiempo = np.arange(round(FS * DURACION)) / FS
    componentes = {f: a * np.sin(2 * np.pi * f * tiempo)
                   for f, a in zip(FRECUENCIAS, AMPLITUDES)}
    limpia = sum(componentes.values())
    ruido = np.random.default_rng(SEMILLA).normal(0, DESV_RUIDO, tiempo.size)
    return tiempo, limpia + ruido, componentes


def disenar_filtros() -> dict[tuple[str, str], dict]:
    """Diseña tres familias por tipo: IIR (Butterworth) y FIR (Hamming)."""
    filtros = {}
    for nombre, cortes in CORTES.items():
        # SOS evita problemas de precisión al usar filtros IIR.
        sos = signal.butter(ORDEN_IIR, cortes, btype=TIPOS[nombre], fs=FS,
                            output='sos')
        filtros[(nombre, 'IIR')] = {'sos': sos}
        # numtaps impar permite pasa altos sin restricciones de Nyquist.
        taps = signal.firwin(COEF_FIR, cortes, pass_zero=TIPOS[nombre],
                             window='hamming', fs=FS)
        filtros[(nombre, 'FIR')] = {'taps': taps}
    return filtros


def aplicar(filtros: dict, entrada: np.ndarray) -> dict[tuple[str, str], np.ndarray]:
    """Aplica filtros en adelante/atrás: fase cero y sin latencia aparente.

    Nota: esta técnica requiere datos futuros; no sirve sin ajustes para
    sistemas en tiempo real y su respuesta efectiva cambia el módulo.
    """
    salidas = {}
    for clave, coef in filtros.items():
        if clave[1] == 'IIR':
            salidas[clave] = signal.sosfiltfilt(coef['sos'], entrada)
        else:
            salidas[clave] = signal.filtfilt(coef['taps'], [1.0], entrada)
    return salidas


def respuesta_frecuencia(coef: dict, familia: str) -> tuple[np.ndarray, np.ndarray]:
    if familia == 'IIR':
        return signal.sosfreqz(coef['sos'], worN=4096, fs=FS)
    return signal.freqz(coef['taps'], [1.0], worN=4096, fs=FS)


def relacion_senal_ruido(senal: np.ndarray, referencia: np.ndarray,
                         margen: int = 125) -> float:
    """SNR de salida contra el componente de interés conocido (es simulación).

    La diferencia incluye las interferencias restantes, ruido residual y
    posible distorsión del componente deseado. Se omiten bordes de 0.25 s.
    """
    ref = referencia[margen:-margen]
    pred = senal[margen:-margen]
    return float(10 * np.log10(np.mean(ref**2) /
                               max(np.mean((pred-ref)**2), 1e-15)))


def amplitud_tono(senal: np.ndarray, t: np.ndarray, f: float) -> float:
    """Amplitud de tono estimada por proyecciones seno/coseno en 4 s."""
    sinv = np.sin(2 * np.pi * f * t)
    cosv = np.cos(2 * np.pi * f * t)
    return float(np.hypot(2 / len(t) * np.dot(senal, sinv),
                          2 / len(t) * np.dot(senal, cosv)))


def preparar_graficas() -> None:
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'axes.titlesize': 11, 'axes.labelsize': 10,
                         'figure.dpi': 120, 'savefig.dpi': 180,
                         'axes.spines.top': False, 'axes.spines.right': False})


def guardar_grafica(nombre: str) -> None:
    plt.savefig(FIG / nombre, bbox_inches='tight', facecolor='white')
    plt.close()


def graficas(t: np.ndarray, x: np.ndarray, comp: dict,
             filtros: dict, salidas: dict) -> None:
    preparar_graficas()
    # 1. Señal de entrada, antes de filtrar
    fig, axes = plt.subplots(2, 1, figsize=(10.5, 6.5), layout='constrained')
    m = t <= 0.60
    limpia = sum(comp.values())
    axes[0].plot(t[m], x[m], color=COLOR['entrada'], linewidth=1,
                 label='Entrada con ruido')
    axes[0].plot(t[m], limpia[m], color=COLOR['IIR'], linewidth=1.35,
                 alpha=.9, label='Señal compuesta sin ruido')
    axes[0].set(title='Señal simulada: 5 + 40 + 120 Hz con ruido blanco',
                xlabel='Tiempo (s)', ylabel='Amplitud relativa')
    axes[0].legend(loc='upper right', fontsize=9)
    f, p = signal.welch(x, fs=FS, nperseg=1024)
    axes[1].plot(f, 10 * np.log10(p+1e-12), color=COLOR['entrada'], linewidth=1.6)
    for tone in FRECUENCIAS:
        axes[1].axvline(tone, color='#e27f22', linestyle='--', alpha=.75)
        axes[1].text(tone+2, -13, f'{int(tone)} Hz', fontsize=9, rotation=90,
                     va='top', color='#955613')
    axes[1].set(title='Densidad espectral de potencia de la entrada (método de Welch)',
                xlabel='Frecuencia (Hz)', ylabel='Potencia/Hz (dB)', xlim=(0,160),
                ylim=(-68,-10))
    for a in axes: a.grid(alpha=.25)
    guardar_grafica('01_senal_entrada.png')

    # 2. Respuesta en frecuencia de todos los filtros
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.5), sharey=True,
                             layout='constrained')
    for ax, nombre in zip(axes, CORTES):
        for familia in ('IIR','FIR'):
            f, h = respuesta_frecuencia(filtros[(nombre, familia)], familia)
            ax.plot(f, db(np.abs(h)**2), label=familia, linewidth=2,
                    color=COLOR[familia])
        fc=CORTES[nombre]
        if isinstance(fc, tuple):
            ax.axvspan(fc[0], fc[1], color='#cff0e6', alpha=.45)
        else: ax.axvline(fc, color='#777', alpha=.7, ls='--', lw=1)
        ax.set(title=nombre, xlabel='Frecuencia (Hz)', xlim=(0,160),ylim=(-90,5))
        ax.grid(alpha=.2)
    axes[0].set_ylabel('Ganancia efectiva, doble pasada (dB)')
    axes[2].legend(loc='upper right')
    fig.suptitle('Comparación de filtros FIR (Hamming) e IIR (Butterworth)', fontsize=13, fontweight='bold')
    guardar_grafica('02_respuestas_frecuencia.png')

    # 3. Comparación temporal entre entrada, FIR e IIR
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 9), layout='constrained')
    m=t<0.5
    for ax,nombre in zip(axes,CORTES):
        ax.plot(t[m],x[m],label='Entrada',color=COLOR['entrada'],alpha=.55,lw=.8)
        for familia in ('IIR','FIR'):
            ax.plot(t[m],salidas[(nombre,familia)][m],
                    color=COLOR[familia], lw=1.6, label=familia)
        ax.set(title=f'{nombre} — señal temporal filtrada',
               ylabel='Amplitud relativa', xlabel='Tiempo (s)')
        ax.grid(alpha=.2); ax.legend(ncol=3,loc='upper right',fontsize=9)
    guardar_grafica('03_comparacion_tiempo.png')

    # 4. Comparación espectral
    fig, axes = plt.subplots(3, 1, figsize=(10.5, 9), layout='constrained')
    for ax,nombre in zip(axes,CORTES):
        f,p=signal.welch(x, fs=FS, nperseg=1024)
        ax.plot(f,10*np.log10(p+1e-12),label='Entrada',color=COLOR['entrada'],alpha=.60,lw=1)
        for familia in ('IIR','FIR'):
            f,p=signal.welch(salidas[(nombre,familia)], fs=FS, nperseg=1024)
            ax.plot(f,10*np.log10(p+1e-12),label=familia,
                    color=COLOR[familia],lw=1.45)
        for tone in FRECUENCIAS:
            ax.axvline(tone,ls=':',color='#999',lw=.8)
        ax.set(title=f'{nombre} — espectro antes/después',
               ylabel='Potencia/Hz (dB)',xlabel='Frecuencia (Hz)',
               xlim=(0,160),ylim=(-130,-10))
        ax.grid(alpha=.2); ax.legend(ncol=3,loc='upper right',fontsize=9)
    guardar_grafica('04_comparacion_frecuencia.png')


def resultados(t: np.ndarray, x: np.ndarray, comp: dict,
               filtros: dict, salidas: dict) -> list[dict]:
    filas=[]
    for nombre in CORTES:
        f_obj=FREQUENCIA_OBJETIVO[nombre]
        referencia=comp[f_obj]
        snr_entrada=relacion_senal_ruido(x,referencia)
        amp_entrada=amplitud_tono(x,t,f_obj)
        for familia in ('IIR','FIR'):
            y=salidas[(nombre,familia)]
            snr_salida=relacion_senal_ruido(y,referencia)
            res={'filtro':nombre, 'familia':familia,
                 'frecuencia_objetivo_hz':f_obj,
                 'snr_entrada_db':round(snr_entrada,2),
                 'snr_salida_db':round(snr_salida,2),
                 'mejora_snr_db':round(snr_salida-snr_entrada,2),
                 'amplitud_tono_entrada':round(amp_entrada,3),
                 'amplitud_tono_salida':round(amplitud_tono(y,t,f_obj),3)}
            filas.append(res)
    with (DAT/'metricas_snr.csv').open('w',newline='',encoding='utf-8-sig') as fh:
        writer=csv.DictWriter(fh,fieldnames=list(filas[0]))
        writer.writeheader(); writer.writerows(filas)
    with (DAT/'senal_entrada.csv').open('w',newline='',encoding='utf-8-sig') as fh:
        writer=csv.writer(fh); writer.writerow(['tiempo_s','amplitud'])
        writer.writerows(zip(t,x))
    print('RESUMEN DE LAS SIMULACIONES')
    for r in filas:
        print(f"{r['filtro']:>12s}  {r['familia']}: SNR entrada {r['snr_entrada_db']:6.2f} dB, "
              f"SNR salida {r['snr_salida_db']:6.2f} dB, "
              f"mejora {r['mejora_snr_db']:+6.2f} dB")
    return filas


def main() -> None:
    t,x,comp=senal_compuesta()
    filtros=disenar_filtros()
    salidas=aplicar(filtros,x)
    graficas(t,x,comp,filtros,salidas)
    resultados(t,x,comp,filtros,salidas)
    print('Figuras y CSV guardados en', BASE)

if __name__=='__main__': main()
