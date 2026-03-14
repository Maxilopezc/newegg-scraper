import os, time, logging, json, random
from urllib.parse import urljoin
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def setup_logger(log_path):
    """Configura el logger para escribir en consola y en un archivo dinámico."""
    logger = logging.getLogger("PDF_Processor")
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        
        file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
    return logger


def human_delay(a=1.5, b=3.5):
    """Simula comportamiento humano"""
    time.sleep(random.uniform(a, b))


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # Configuración de sistema de archivos para outputs
    carpeta_origen = os.path.dirname(os.path.abspath(__file__))
    carpeta_salida = os.path.join(carpeta_origen, "output")
    carpeta_log = os.path.join(carpeta_origen, "log")
    os.makedirs(carpeta_salida, exist_ok=True)
    os.makedirs(carpeta_log, exist_ok=True)

    archivo_json = os.path.join(carpeta_salida, f"productos_newegg_{timestamp}.json")
    archivo_log = os.path.join(carpeta_log, f"process_{timestamp}.log")

    logger = setup_logger(archivo_log)
    logger.info("Iniciando scrapeo con guardado dinámico")
    logger.info(f"El log de esta sesión se guardará en: {archivo_log}")

    url_base = "https://www.newegg.com/"

    # Abre el JSON en modo "streaming" para guardar registro a registro sin cargar todo en RAM
    json_file = open(archivo_json, "w", encoding="utf-8")
    json_file.write("[\n")
    first_item = True

    try:
        with sync_playwright() as p:
            # Configuración anti-bot: Navegador visible y User-Agent realista
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
                locale="en-US"
            )

            page = context.new_page()
            
            # Táctica anti-bot: Simular tráfico referencial desde Google antes de ir al target
            page.goto("https://www.google.com")
            page.wait_for_load_state("domcontentloaded")
            page.goto(url_base)
            
            # Interacción inicial para generar eventos de mouse y parecer humano
            page.mouse.move(random.randint(100,800), random.randint(100,600))
            page.mouse.wheel(random.randint(100,500), random.randint(100,500))
            page.wait_for_load_state("domcontentloaded")
            human_delay() 

            # Identifica todas las categorías principales disponibles
            items = page.locator("li.menu-level-3")
            items.first.wait_for(state="attached", timeout=15000)
            total_items = items.count()

            # Nivel 1: Iteración sobre categorías
            for i in range(total_items):
                try:
                    item = items.nth(i)
                    href_item = item.locator("a.menu-list-link").first.get_attribute("href")
                    url_item = urljoin(url_base, href_item)
                    
                    if not url_item:
                        logger.error("No se encontró la URL de la categoría.")
                        continue

                    page.goto(url_item, timeout=30000)
                    page.wait_for_load_state("domcontentloaded")
                    human_delay()

                    # Busca el botón de redirección hacia la grilla de todos los productos
                    page.wait_for_selector("div.standard-box-top", timeout=15000)
                    btn_prod = page.locator("div.standard-box-top a.btn").first
                    btn_prod.wait_for(state="attached", timeout=10000)

                    href_boton = btn_prod.get_attribute("href")

                    if not href_boton:
                        logger.error("No se encontró el botón para visualizar los productos.")
                        continue

                    page.goto(href_boton, timeout=30000)
                    page.wait_for_load_state("domcontentloaded")
                    human_delay()

                    # Nivel 2: Bucle infinito de paginación (se rompe al no hallar "Next")
                    while True:
                        try:
                            page.wait_for_selector("div.item-cell", timeout=15000)
                            page.mouse.wheel(0, random.randint(400, 1000))

                            # Recopila todos los enlaces de los productos de la página actual
                            productos = page.locator("div.item-cell a.item-img")
                            links_productos = []
                            
                            for j in range(productos.count()):
                                href_prod = productos.nth(j).get_attribute("href")
                                if href_prod:
                                    links_productos.append(href_prod)

                            # Nivel 3: Extracción de detalles por producto
                            for link in links_productos:
                                product_page = None
                                try:
                                    # Crucial: Aislar cada producto en una pestaña nueva para proteger el estado del DOM principal
                                    product_page = context.new_page()
                                    product_page.goto(link, timeout=20000)
                                    product_page.wait_for_load_state("domcontentloaded")
                                    human_delay(1, 2)

                                    product_page.wait_for_selector("h1.product-title", timeout=10000)
                                    titulo = product_page.locator("h1.product-title").inner_text()

                                    precio_locator = product_page.locator("div.product-price div.price-current").first
                                    precio = precio_locator.inner_text() if precio_locator.count() else "N/A"

                                    desc_locator = product_page.locator("div.product-bullets")
                                    description = desc_locator.inner_text() if desc_locator.count() else ""

                                    imagen_locator = product_page.locator("img.product-view-img-original").first
                                    imagen = imagen_locator.get_attribute("src") if imagen_locator.count() else ""

                                    producto = {
                                        "titulo": titulo,
                                        "precio": precio,
                                        "descripcion": description,
                                        "imagen": imagen,
                                        "url": link
                                    }

                                    if not first_item:
                                        json_file.write(",\n")
                                        
                                    # Guardado incremental en disco (.flush) para no perder datos si el script colapsa
                                    json.dump(producto, json_file, ensure_ascii=False, indent=4)
                                    json_file.flush() 
                                    first_item = False

                                    logger.info(f"Producto guardado: {titulo[:30]}...")

                                except PlaywrightTimeoutError:
                                    logger.warning(f"Timeout al intentar cargar el producto: {link}")
                                except Exception as e:
                                    logger.error(f"Error procesando producto {link}: {e}")
                                finally:
                                    # Liberación de memoria cerrando la pestaña actual
                                    if product_page and not product_page.is_closed():
                                        product_page.close()
                                    human_delay(0.5, 1.5)

                            # Verificación de continuidad: Chequea si existe el botón "Siguiente" y si es clickeable
                            next_button = page.locator('.btn-group-cell a[title="Next"]').first
                            if next_button.count() == 0 or next_button.is_disabled():
                                logger.info("Fin de la paginación para esta categoría.")
                                break 

                            next_button.scroll_into_view_if_needed()
                            next_button.click(timeout=10000)
                            page.wait_for_load_state("domcontentloaded")
                            human_delay()
                            
                        except PlaywrightTimeoutError:
                            logger.warning("Timeout durante la extracción de la página de la paginación.")
                            break 
                        except Exception as e:
                            logger.error(f"Error inesperado en la paginación: {e}")
                            break

                except Exception as e:
                    logger.warning(f"Error al intentar extraer la categoría completa (Índice {i}): {e}")
                    continue

    except KeyboardInterrupt:
        # Permite al usuario abortar (Ctrl+C) sin corromper el formato del archivo JSON final
        logger.warning("Script cancelado manualmente por el usuario. Iniciando cierre seguro...")
        
    finally:
        # Cierre estructural del JSON para garantizar que sea parseable en análisis posteriores
        json_file.write("\n]")
        json_file.close()
        logger.info(f"Datos guardados correctamente y archivo cerrado en {archivo_json}")


if __name__ == "__main__":
    main()