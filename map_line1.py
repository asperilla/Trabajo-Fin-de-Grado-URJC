#!/usr/bin/python3
# -*- coding: utf-8 -*-

# Devuelve un mapa con la localización de los buses de la Línea 1 de la EMT

from xml.dom import minidom
import folium
import branca
import pyproj
from pyemtmad import Wrapper, types
import datetime, time, sys
import pickle

import csv



if __name__ == "__main__":

   	#Creamos el mapa
	mapa = folium.Map(location=(40.4167278, -3.7033387), zoom_start=13)

	lista_distancias = []
	dicc = {}
	lista_coord = []
	lista_coord_esp = [] 
	lista_ids = []

	with open('lineas_paradas.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['line'] == '1' and row['secDetail'] == '10':
				distance = row['distance']
				lista_distancias.append(int(distance))
				x = row['latitude']
				y = row['longitude']
				name = row['name']

				dicc[int(distance)] = [float(x),float(y)]

				marcador = folium.Marker(location=(float(x),float(y)),
						 				icon=folium.Icon(color="red"),
										tooltip = name)
				marcador.add_to(mapa)

	# PARADAS
	with open('lineas_nodos.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['line'] == '1' and row['secDetail'] == '19':
				distance = row['distance']
				lista_distancias.append(int(distance))
				x = row['latitude']
				y = row['longitude']
	
				dicc[int(distance)] = [float(x),float(y)]
				#print([float(x),float(y)])
	print()

	lista_distancias.sort()
	#print(lista_distancias)

	for i in lista_distancias:
		lista_coord.append(dicc[i])

	print(lista_coord)
	print()
		
	aline = folium.PolyLine(locations=lista_coord, weight=4, color="blue")
	aline.add_to(mapa)
	#print(lista_distancias)

	# ESPIRAS
	with open('espiras_filtradas.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			utm_y = float(row['Lat'])
			utm_x = float(row['Long'])

			opcion = 2
			 
			if opcion == 1:
				elipsoide1 = "intl"
			 
			elif opcion == 2:
				elipsoide1 = "WGS84"

			huso = 30

			srcProj = pyproj.Proj(proj="utm", zone=huso, ellps=elipsoide1, units="m")
			dstProj = pyproj.Proj(proj='longlat', ellps='WGS84', datum='WGS84')
			 
			y,x = pyproj.transform(srcProj, dstProj, utm_x, utm_y)

			c = [float(x),float(y)]
			#aline = folium.PolyLine(locations=c, weight=2, color="green")
			#aline.add_to(mapa)	
			#print(c)
			if str(float(x)).split('.')[0] == '40':
				lista_coord_esp.append(c)
	
				icon_url = "/home/sergioaspe/Escritorio/MapayBuses/Otros/sensor.png"
				icon = folium.features.CustomIcon(icon_url,icon_size=(30,30))

				marcador2 = folium.Marker(location=(float(x),float(y)), icon=icon)#folium.Icon(color="green"))#, weight=2)
				marcador2.add_to(mapa)

	print(lista_coord_esp)

	mapa.save("Linea_Esp.html")	






																	

