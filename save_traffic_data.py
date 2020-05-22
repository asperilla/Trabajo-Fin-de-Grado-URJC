#!/usr/bin/python3

from xml.dom import minidom
import sqlite3
import requests
import datetime, time, sys
import csv

# Función que coge cada característica y la guarda en un diccionario 
def insertar(elemento, lista):
	nombre_elemento = lista.getElementsByTagName(elemento)
	for item in nombre_elemento:
		key = item.nodeName
		value = item.childNodes[0].nodeValue
		dicc[key] = value	
	return


# MAIN #############################################################################################################
if __name__ == "__main__":
	while True:	

		#HORA
		hora = time.strftime("%H:%M")

		# Descargo xml
		URL = "http://informo.munimadrid.es/informo/tmadrid/pm.xml"

		response = requests.get(URL)
		with open('/home/sergioaspe/Escritorio/Espiras_Data/Get_Data/datos_transporte.xml', 'wb') as file:
			file.write(response.content)

		xmldoc = minidom.parse('/home/sergioaspe/Escritorio/Espiras_Data/Get_Data/datos_transporte.xml')

		# Me quedo con la fecha y hora
		NodeChild = xmldoc.firstChild
		fecha_xml = NodeChild.childNodes[1]
		fecha_hora_name = fecha_xml.nodeName
		fecha_hora_value = fecha_xml.childNodes[0].nodeValue
		fecha = fecha_hora_value.split(" ")[0]
		hora_xml = fecha_hora_value.split(" ")[1]


		# Creación de la base de datos
		bd = sqlite3.connect("/home/sergioaspe/Escritorio/Espiras_Data/Get_Data/Espiras.db")
		cursor = bd.cursor()

		# Creamos la tabla en la base de datos
		cursor.execute('CREATE TABLE IF NOT EXISTS Datos_Espiras (hora_xml REAL, hora REAL, idelem INT, intensidad INT, ocupacion INT, carga INT, nivelServicio INT)')

		lista_espiras_l1 = []
		with open('/home/sergioaspe/Escritorio/Espiras_Data/Get_Data/espiras_filtradas.csv') as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				lista_espiras_l1.append(int(row['Id']))

		listt = []
		# Recorremos el XML -> para cada bloque <pm>, cogemos las características que deseamos
		for i in range(3750):
			dicc = {}
			pm_list = xmldoc.getElementsByTagName('pm')[i]
			if pm_list is None:
				break
			insertar('idelem', pm_list)
			idelem = dicc['idelem']
			#listt.append(int(idelem))
			if int(idelem) in lista_espiras_l1:
				#input("YES")
				insertar('intensidad', pm_list)
				insertar('ocupacion', pm_list)
				insertar('carga', pm_list)
				insertar('nivelServicio', pm_list)
				
				# Guardamos para cada bloque sus características en la base de datos
				intensidad = dicc['intensidad']
				ocupacion = dicc['ocupacion']
				carga = dicc['carga']
				nivelServicio = dicc['nivelServicio']
				cursor.execute("INSERT INTO Datos_Espiras (hora_xml, hora, idelem, intensidad, ocupacion, carga, nivelServicio) VALUES (?, ?, ?, ?, ?, ?, ?)",
							  (hora_xml, hora, idelem, intensidad, ocupacion, carga, nivelServicio))

				bd.commit()

		cursor.close()
		bd.close()

		time.sleep(260)

	#print(listt)
	#print(lista_espiras_l1)
