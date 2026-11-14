# Implementación y evaluación de filtros digitales

**Universidad Ciudadana de Nuevo León · Ingeniería en Desarrollo de Software**  
**Materia:** Señales y Sistemas  
**Actividad:** Actividad formativa 3  
**Alumna:** Juana María Rodríguez Camarillo  
**Tutor:** Ing. Luis Osvaldo Moreno Gaytán

## Propósito

Evaluar tres tipos de filtros digitales (pasa bajos, pasa altos y pasa bandas), construidos con dos métodos: **IIR Butterworth** y **FIR con ventana de Hamming**. El experimento permite observar cómo se modifica una señal en los dominios del tiempo y la frecuencia al eliminar componentes no deseadas.

## Software

- Python 3.10 o posterior
- NumPy, SciPy y Matplotlib (`requirements.txt`)
- No requiere licencia de MATLAB ni cuenta para ejecutar el código.

## Cómo ejecutarlo

1. Abre una terminal dentro de la carpeta del proyecto.
2. Opcionalmente, crea un entorno virtual: `python -m venv .venv` y actívalo.
3. Instala las dependencias: `python -m pip install -r requirements.txt`
4. Ejecuta: `python filtros_digitales.py`

El programa crea las siguientes gráficas en `figuras/`:

- `01_senal_entrada.png`: señal original con ruido y su espectro.
- `02_respuestas_frecuencia.png`: respuestas efectivas de los seis filtros.
- `03_comparacion_tiempo.png`: entrada e imágenes de las señales filtradas (dominio temporal).
- `04_comparacion_frecuencia.png`: espectros antes y después (método de Welch).

También genera los CSV `datos/metricas_snr.csv` y `datos/senal_entrada.csv`.

## Parámetros del experimento

| Parámetro | Valor |
|---|---|
| Muestreo | 500 muestras/s (500 Hz) |
| Duración | 4 s |
| Tonos combinados | 5, 40 y 120 Hz |
| Amplitudes respectivas | 0.90, 0.65 y 0.45 |
| Ruido blanco | Normal, desviación estándar 0.35 |
| Semilla aleatoria | 2026 (reproducibilidad) |
| Pasa bajos | Corte en 15 Hz, objetivo 5 Hz |
| Pasa altos | Corte en 80 Hz, objetivo 120 Hz |
| Pasa bandas | Intervalo 30–60 Hz, objetivo 40 Hz |
| IIR | Butterworth de orden base 4, SOS |
| FIR | 101 coeficientes, ventana Hamming |

Los seis filtros se aplican con filtrado **adelante-atrás** para lograr **fase cero** en señales almacenadas. Esta técnica utiliza datos futuros y, por tanto, **no es directamente apta para tiempo real**. La respuesta efectiva mostrada en la segunda figura es aproximadamente el módulo de la respuesta de una pasada **al cuadrado**, lo que produce mayor atenuación total.

## Resultados de la simulación

La métrica de relación señal-ruido (SNR) se calcula contra **la componente sinusoidal conocida que cada filtro pretende conservar**; el resto de tonos, el ruido y la posible distorsión cuentan como error. Para evitar efectos de borde, se omiten los primeros y últimos 0.25 segundos en el cálculo de SNR.

| Filtro | Familia | SNR entrada | SNR salida | Mejora |
|---|---|---:|---:|---:|
| Pasa bajos | IIR | −0.37 dB | 17.48 dB | +17.85 dB |
| Pasa bajos | FIR | −0.37 dB | 18.31 dB | +18.69 dB |
| Pasa altos | IIR | −8.60 dB | 1.10 dB | +9.70 dB |
| Pasa altos | FIR | −8.60 dB | 0.93 dB | +9.53 dB |
| Pasa bandas | IIR | −4.75 dB | 12.04 dB | +16.79 dB |
| Pasa bandas | FIR | −4.75 dB | 12.80 dB | +17.55 dB |

Los valores se obtuvieron mediante una **simulación reproducible**, no son datos medidos de personas, sensores industriales o empresas.

## Interpretación

- El pasa bajos favorece el componente de 5 Hz.
- El pasa altos conserva preferentemente la componente de 120 Hz.
- El pasa bandas aísla preferentemente el tono de 40 Hz.
- FIR e IIR pueden lograr efectos comparables con requisitos y respuestas distintos. Ninguno es universalmente superior.
- En el gráfico de respuesta, los cortes corresponden al diseño; como el programa filtra en dos pasadas, la atenuación efectiva es distinta de la respuesta de una pasada.

**Aplicación orientativa:** procesar registros de vibración de una máquina para separar componentes de baja, media o alta frecuencia. Para usarlo en una máquina real, se requieren mediciones auténticas, selección de cortes basada en el equipo y validación técnica.

## Cómo publicar en GitHub

1. Crea una cuenta de GitHub si aún no tienes y abre un repositorio vacío (por ejemplo, `ucnl-filtros-digitales`).
2. En esta carpeta, utiliza los siguientes comandos (sustituye `USUARIO` por tu cuenta):

```bash
git init
git add .
git commit -m "Actividad 3: filtros digitales FIR e IIR"
git branch -M main
git remote add origin https://github.com/USUARIO/ucnl-filtros-digitales.git
git push -u origin main
```

Si Git solicita autenticación, inicia sesión mediante el método indicado por GitHub. **No publiques contraseñas ni tokens en el repositorio.**

## Referencias

- Oppenheim, A. V., & Schafer, R. W. (2010). *Discrete-time signal processing* (3.ª ed.). Pearson.
- SciPy Community. (s. f.). *scipy.signal.butter*. SciPy. https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html
- SciPy Community. (s. f.). *scipy.signal.firwin*. SciPy. https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin.html
- SciPy Community. (s. f.). *scipy.signal.sosfiltfilt*. SciPy. https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfiltfilt.html
- SciPy Community. (s. f.). *scipy.signal.welch*. SciPy. https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html
