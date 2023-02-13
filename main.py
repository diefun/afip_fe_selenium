import time
import calendar
import yaml

from datetime import date
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.ui import Select

# Datos
with open('datos.yaml', 'r') as datos:
    datos_usuario = yaml.safe_load(datos)

# Cambiar CARO por FEDE dependiendo a quien se le hagan las facturas
cuit = datos_usuario['CARO']['CUIT']
password = datos_usuario['CARO']['PASSWORD']

# Fechas
today = date.today()
mes = str(today.month)
anio = str(today.year)
primer_dia, ultimo_dia = calendar.monthrange(today.year, today.month)

if today.month < 10:
    mes = '0' + mes

fecha_principio_mes = '01/' + mes + '/' + anio
fecha_fin_mes = str(ultimo_dia) + '/' + mes + '/' + anio

# Inicializa el driver con Chrome
driver = webdriver.Chrome('/Users/d/PycharmProjects/afipFE/chromedriver')

try:
    # Accede a la web de AFIP
    driver.get('https://auth.afip.gob.ar/contribuyente_/login.xhtml')
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="F1:username"]'))
    )

    # Carga datos de acceso
    driver.find_element(by='xpath', value='//*[@id="F1:username"]').send_keys(cuit)
    driver.find_element(by='xpath', value='//*[@id="F1:btnSiguiente"]').send_keys(Keys.RETURN)
    driver.find_element(by='xpath', value='//*[@id="F1:password"]').send_keys(password)
    driver.find_element(by='xpath', value='//*[@id="F1:btnIngresar"]').send_keys(Keys.RETURN)

    # Navega el sitio para encontrar servicios y acceder a comprobantes en línea
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="serviciosMasUtilizados"]/div/div/div/div[1]/a/div/h3'))
    )
    driver.find_element(by='xpath', value='//*[@id="serviciosMasUtilizados"]/div/div/div/div[5]/div/a').send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div/main/div/section/div/div[3]/div[11]/a'))
    )

    comprobantes = driver.find_element(by='xpath', value='//*[@id="root"]/div/main/div/section/div/div[3]/div[11]/a')
    comprobantes.click()
    time.sleep(1)

    # Cambia el driver al tab de los comprobantes
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.NUMPAD2)
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(1)

    # Busca la entidad hace click
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="contenido"]/form/table/tbody/tr[4]/td/input[2]'))
    )
    entidad = driver.find_element(by='xpath', value='//*[@id="contenido"]/form/table/tbody/tr[4]/td/input[2]')
    entidad.click()

    # Acá tiene que empezar el loop para cada comprobante
    # CREA UN NUEVO ARCHIVO QUITANDO LOS DUPLICADOS
    with open('facturas.csv', 'r') as archivo:
        lineas = archivo.readlines()
        for linea in lineas:
            items = linea.split(';')
            importe = items[0]
            fecha_cruda = items[1]
            fecha_lista = fecha_cruda.split('-')
            fecha_comprobante = fecha_lista[2].strip('\n') + '/' + fecha_lista[1] + '/' + fecha_lista[0]
            descripcion = 'Clases'

            print(importe)
            print(fecha_comprobante)

            # Busca el botón para generar comprobantes y hace click
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="btn_gen_cmp"]'))
            )
            generar = driver.find_element(by='xpath', value='//*[@id="btn_gen_cmp"]')
            generar.click()

            # Busca el selector de punto de venta y selecciona las opciones
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="puntodeventa"]'))
            )
            pto_venta = driver.find_element(by='xpath', value='//*[@id="puntodeventa"]')
            opciones = Select(pto_venta)
            opciones.select_by_value('5')
            time.sleep(1)
            tipo_comprobante = driver.find_element(by='xpath', value='//*[@id="universocomprobante"]')
            opciones = Select(tipo_comprobante)
            opciones.select_by_value('2')
            continuar = driver.find_element(by='xpath', value='//*[@id="contenido"]/form/input[2]')
            continuar.click()

            # Busca el selector de fecha y carga los datos solicitados
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="fc"]'))
            )
            driver.find_element(by='xpath', value='//*[@id="fc"]').send_keys(Keys.COMMAND + 'A' + Keys.DELETE)
            driver.find_element(by='xpath', value='//*[@id="fc"]').send_keys(fecha_comprobante)
            tipo = driver.find_element(by='xpath', value='//*[@id="idconcepto"]')
            opciones_tipo = Select(tipo)
            opciones_tipo.select_by_visible_text(' Servicios')
            driver.find_element(by='xpath', value='//*[@id="fsd"]').send_keys(Keys.COMMAND + 'A' + Keys.DELETE)
            driver.find_element(by='xpath', value='//*[@id="fsd"]').send_keys(fecha_principio_mes)
            driver.find_element(by='xpath', value='//*[@id="fsh"]').send_keys(Keys.COMMAND + 'A' + Keys.DELETE)
            driver.find_element(by='xpath', value='//*[@id="fsh"]').send_keys(fecha_fin_mes)
            driver.find_element(by='xpath', value='//*[@id="contenido"]/form/input[2]').click()
            condicion = driver.find_element(by='xpath', value='//*[@id="idivareceptor"]')
            opciones_tipo = Select(condicion)
            opciones_tipo.select_by_visible_text(' Consumidor Final')
            time.sleep(1)
            tipo_documento = driver.find_element(by='xpath', value='//*[@id="idtipodocreceptor"]')
            opciones_tipo = Select(tipo_documento)
            opciones_tipo.select_by_visible_text('DNI')
            driver.find_element(by='xpath', value='//*[@id="formadepago7"]').click()
            driver.find_element(by='xpath', value='//*[@id="formulario"]/input[2]').click()

            # Busca el campo de descripción y carga los datos solicitados
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="detalle_descripcion1"]'))
            )
            driver.find_element(by='xpath', value='//*[@id="detalle_descripcion1"]').send_keys(descripcion)
            driver.find_element(by='xpath', value='//*[@id="detalle_precio1"]').send_keys(importe)
            driver.find_element(by='xpath', value='//*[@id="contenido"]/form/input[8]').click()

            # Busca el botón de "Confirmar Datos..." y continúa
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="btngenerar"]'))
            )
            driver.find_element(by='xpath', value='//*[@id="btngenerar"]').click()
            time.sleep(1)
            alerta = Alert(driver)
            alerta.accept()

            time.sleep(1)

            driver.find_element(by='xpath', value='//*[@id="contenido"]/table/tbody/tr[2]/td/input').click()

finally:
    driver.quit()