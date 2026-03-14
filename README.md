# E-commerce Scraper PoC (Proof of Concept)

> **EDUCATIONAL PURPOSES ONLY / SOLO FINES EDUCATIVOS**
> This repository contains a Proof of Concept (PoC) script created strictly for educational purposes and to demonstrate web automation techniques, DOM manipulation, and memory management in Python. 
> 
> The author does not endorse, encourage, or support the use of this script to violate the Terms of Service (ToS) of Newegg or any other website. Do not use this code to perform unauthorized scraping, cause server overload (DDoS), or extract data for commercial distribution. The repository does not include any scraped data. Use at your own risk.

## Sobre el Proyecto
Este proyecto es una demostración técnica de automatización web utilizando **Python** y **Playwright**. Su objetivo es ilustrar cómo construir una arquitectura robusta para la extracción de datos, manejando problemas comunes en la ingeniería de datos.

### Habilidades Técnicas Demostradas
* **Gestión de Memoria y Rendimiento:** Implementación de escritura dinámica en disco (streaming JSON) con `json.flush()` para evitar sobrecargas de RAM durante ejecuciones prolongadas.
* **Aislamiento de Entornos (Context/Pages):** Uso de múltiples pestañas dinámicas en Playwright para no corromper el estado del DOM de la página principal de navegación.
* **Manejo de Excepciones Avanzado:** Bloques `try-except` anidados para capturar `TimeoutError` y garantizar el cierre seguro de archivos (evitando JSONs corruptos) ante interrupciones del usuario (`KeyboardInterrupt`).
* **Lógica de Paginación:** Algoritmos de navegación iterativa para detectar y validar botones de "Siguiente" dinámicos.
* **Registro de Eventos (Logging):** Implementación de un sistema de logging dual (consola y archivo dinámico con timestamps) para monitoreo de procesos.

## Uso
Este código se proporciona únicamente para análisis y revisión de código. No se brindan instrucciones de despliegue para evitar su uso masivo. El archivo .json de ejemplo es de un scrapeo corto ya que el scrapeo completo llevaria demasiado tiempo.
