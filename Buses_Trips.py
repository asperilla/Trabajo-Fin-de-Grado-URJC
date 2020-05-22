from pylab import *
import matplotlib.pyplot as plt
import requests
import json
from datetime import timedelta,date,datetime, time, sys
import csv
import sqlite3
import seaborn as sns
import pandas as pd
import numpy as np

def pintar(id_bus, cursor):
	cursor.execute("SELECT fecha from Datos_Buses where id_bus = " + id_bus)

	rows = cursor.fetchall()

	tiempo = []
	tiempo_total = []
	for lista in rows:
		valor = lista[0]
		fecha = valor.split(' ')[0]
		hora = valor.split(' ')[1]

		if fecha == '2020-03-10':
			tiempo_total.append(hora)

	lista_tiempo = tiempo_total

	cursor.execute("SELECT distancia_bus from Datos_Buses where fecha like '2020-03-10%' and id_bus = " + id_bus)

	rows = cursor.fetchall()

	for lista in rows:
		lista_distancia.append(int(lista[0]))

	return lista_tiempo, lista_distancia


def axis_to_int_axis(eje):
	axis_int = []

	n = 0
	for i in eje:
		axis_int.append(n)
		n = n + 1

	return axis_int


def pinta_planif(bus1_starttime, bus1_endtime, bus1_startdistance, bus1_enddistance, axis_tiempo_int):
	eje_x = []
	eje_y = []

	eje_x.append(str(bus1_starttime))
	eje_x.append(str(bus1_endtime))
	eje_y.append(bus1_startdistance)
	eje_y.append(bus1_enddistance)

	new_eje_y = []

	k = 0
	l = 0
	for i in axis_tiempo:
		j = eje_x[l]
		if i == j:
			new_eje_y.append(eje_y[k])
			if l < (len(eje_x) - 1):
				l = l + 1
				k = k + 1
		else:
			new_eje_y.append(None)
		
	axis_tiempo_int = np.array(axis_tiempo_int)
	new_eje_y = np.array(new_eje_y).astype(np.double)
	mask = np.isfinite(new_eje_y)
				
	ax.plot(axis_tiempo_int[mask], new_eje_y[mask], 'g-', linewidth=1.5)

def get_vmedia(eje_x, eje_y, distancia_paradas):
	k = 0
	j = 0
	r = 0
	for i in range(0, len(eje_y)):
		hora_1 = eje_x[j]

		dist_1 = eje_y[j]
		dist_parada = distancia_paradas[k]
		if eje_y[r] >= dist_parada:
			hora_2 = eje_x[r-1]
			dist_2 = eje_y[r-1]
			if dist_1 >= dist_2:
				hora_2 = eje_x[r]
				dist_2 = eje_y[r]
				j = r + 1
				r = r + 1
				w = 1
				while dist_1 >= dist_2:
					j = r + w
					r = r + w
					hora_2 = eje_x[r]
					dist_2 = eje_y[r]
					w = w + 1
	
			else:
				j = r
			
			k = k + 1

			list_hora1.append(hora_1)
			list_hora2.append(hora_2)		

			hora_1 = datetime.strptime(hora_1, '%H:%M:%S')
			hora_2 = datetime.strptime(hora_2, '%H:%M:%S')

			tiempo_tramo = hora_2 - hora_1
			tiempo_tramo = int(tiempo_tramo.seconds)
			if tiempo_tramo < 5:
				hora_1 = list_hora2[-2]
				list_hora1[-1] = hora_1
				hora_1 = datetime.strptime(hora_1, '%H:%M:%S')
				tiempo_tramo = hora_2 - hora_1
				tiempo_tramo = int(tiempo_tramo.seconds)

			dist_tramo = dist_2 - dist_1

			v_media = ((dist_tramo) / (tiempo_tramo)) # metros/segundos

			list_v_media.append(round(v_media,2))

			if dist_parada == distancia_paradas[-1]:
				break

		r = r + 1

	return list_v_media, list_hora1, list_hora2

def pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int):
	for i in range(0, len(list_hora1)):
		h1 = list_hora1[i]
		h2 = list_hora2[i]

		eje_x_vmedia.append((h1,h2))
		d1 = lista_distancia_paradas[i]
		d2 = lista_distancia_paradas[i+1]
		eje_y_vmedia.append((d1,d2))

		eje_x = []
		eje_y = []

		eje_x.append(h1)
		eje_x.append(h2)
		eje_y.append(d1)
		eje_y.append(d2)

		new_eje_y = []

		k = 0
		l = 0
		for i in axis_tiempo:
			j = eje_x[l]
			if i == j:
				new_eje_y.append(eje_y[k])
				if l < (len(eje_x) - 1):
					l = l + 1
					k = k + 1
			else:
				new_eje_y.append(None)
			
		axis_tiempo_int = np.array(axis_tiempo_int)
		new_eje_y = np.array(new_eje_y).astype(np.double)
		mask = np.isfinite(new_eje_y)
					
		ax.plot(axis_tiempo_int[mask], new_eje_y[mask], 'ko-', linewidth=2)

def pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int):
	new_eje_y = []

	k = 0
	l = 0
	for i in axis_tiempo:
		j = eje_x[l]
		if i == j:
			new_eje_y.append(eje_y[k])
			if l < (len(eje_x) - 1):
				l = l + 1
				k = k + 1
		else:
			new_eje_y.append(None)
		
	axis_tiempo_int = np.array(axis_tiempo_int)
	new_eje_y = np.array(new_eje_y).astype(np.double)
	mask = np.isfinite(new_eje_y)
				
	#ax.plot(axis_tiempo_int[mask], new_eje_y[mask], 'k-', linewidth=1.5)# , label='bus_8240')
	

# MAIN #############################################################################################################
if __name__ == "__main__":
	
	#Conectamos con la base de datos
	bd = sqlite3.connect("Buses.db")
	cursor = bd.cursor()

	# VISUALIZACIÓN
	fig, ax = plt.subplots()

	fig.subplots_adjust(left=0.05,right=0.95)

	ax.set_title('Recorrido_Buses vs Nivel de Servicio - 10/03/2020')
	ax.set_xlabel('Tiempo')
	ax.set_ylabel('Distancia (m)')
	ax.set_ylim(0,9000)

	dicc_paradas = {}
	with open('lineas_paradas.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['line'] == '1':
				direccion = row['secDetail']
				if direccion == '10':
					x = row['latitude']
					y = row['longitude']
					name = row['name']
					distance = row['distance']
					dicc_paradas[name] = distance

	lista_distancia_paradas = []
	for name, value in dicc_paradas.items():
		lista_distancia_paradas.append(int(value))
	
	distancia_paradas = []
	distancia_paradas = lista_distancia_paradas[1:]
	#print(distancia_paradas)

	# Segundo eje Y, paradas 
	ax2 = ax.twinx()
	ax2.set_ylim(0, 9000)
	ax2.set_yticks(distancia_paradas)
	ax2.set_ylabel('Paradas')

	# EJE TIEMPO
	axis_tiempo = []

	for k in (9,10,11,12):
		for j in range(0,60):
			for i in range(0,60):
				value = time(k,j,i)
				axis_tiempo.append(str(value))

	labels = axis_tiempo

	axis_tiempo_int = axis_to_int_axis(axis_tiempo)
	list_axis_tiempo_int = axis_tiempo_int

	# RECORRIDO REAL BUS ###########################################

	### BUS1
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('8240', cursor)

	#print(lista_tiempo)
	#print()
	#print(lista_distancia)

	eje_x = lista_tiempo[37:543]
	eje_y = lista_distancia[37:543]
	#print(eje_y)

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)


	### BUS2
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('122', cursor)

	eje_x = lista_tiempo[18:535]
	eje_y = lista_distancia[18:535]
	#print(eje_y)

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)


	### BUS3
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('111', cursor)

	eje_x = lista_tiempo[47:549]
	eje_y = lista_distancia[47:549]
	#print(eje_y)

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)

	### BUS4
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('123', cursor)

	eje_x = lista_tiempo[164:624]
	eje_y = lista_distancia[164:624]

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)

	### BUS5
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('8243', cursor)

	eje_x = lista_tiempo[275:746]
	eje_y = lista_distancia[275:746]

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)

	### BUS6
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('107', cursor)

	eje_x = lista_tiempo[7:424]
	eje_y = lista_distancia[7:424]

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)

	### BUS7
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('8241', cursor)

	eje_x = lista_tiempo[511:1030]
	eje_y = lista_distancia[511:1030]

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)

	### BUS8
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('119', cursor)

	eje_x = lista_tiempo[576:1062]
	eje_y = lista_distancia[576:1062]

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)

	### BUS9
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('120', cursor)

	eje_x = lista_tiempo[703:1259]
	eje_y = lista_distancia[703:1259]

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)

	### BUS10
	lista_tiempo = []
	lista_distancia = []

	lista_tiempo, lista_distancia = pintar('124', cursor)

	eje_x = lista_tiempo[583:1203]
	eje_y = lista_distancia[583:1203]

	pinta_recorrido(eje_x,eje_y,axis_tiempo,axis_tiempo_int)

	# RECORRIDO V_MEDIA ENTRE PARADAS ################################
	list_v_media = []
	list_hora1 = []
	list_hora2 = []

	list_v_media, list_hora1, list_hora2 = get_vmedia(eje_x, eje_y, distancia_paradas)

	# PINTA RECORRIDO REAL BUS CON V_MEDIA ENTRE PARADAS #############
	eje_x_vmedia = []
	eje_y_vmedia = []

	pinta_vmedia_bus(list_hora1, list_hora2, lista_distancia_paradas, axis_tiempo_int)

	# RECORRIDO PLANIFICACION BUS #

	bus_startdistance = 0
	bus_enddistance = 8795

	### BUS1
	bus1_starttime = time(9,3,0)
	bus1_endtime = time(10,1,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	### BUS2
	bus1_starttime = time(9,16,0)
	bus1_endtime = time(10,13,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	### BUS3
	bus1_starttime = time(9,28,0)
	bus1_endtime = time(10,35,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	### BUS4
	bus1_starttime = time(9,40,0)
	bus1_endtime = time(10,46,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	### BUS5
	bus1_starttime = time(9,53,0)
	bus1_endtime = time(10,57,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	### BUS6
	bus1_starttime = time(10,5,0)
	bus1_endtime = time(11,8,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	### BUS7
	bus1_starttime = time(10,17,0)
	bus1_endtime = time(11,19,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	### BUS8
	bus1_starttime = time(10,29,0)
	bus1_endtime = time(11,31,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	### BUS9
	bus1_starttime = time(10,42,0)
	bus1_endtime = time(11,43,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	### BUS10
	bus1_starttime = time(10,55,0)
	bus1_endtime = time(11,55,0)

	pinta_planif(bus1_starttime, bus1_endtime, bus_startdistance, bus_enddistance, axis_tiempo_int)

	##### DATOS ESPIRAS ###############################################################

	# Listas / Diccionarios
	lista_tiempo = []
	lista_espiras = []
	lista_nivelServicio = []
	dicc = {}

	# Conectamos con la base de datos
	bd = sqlite3.connect("Espiras_10_03.db")
	cursor = bd.cursor()

	cursor.execute("SELECT hora_xml,idelem,nivelServicio from Datos_Espiras where hora_xml like '9%' or hora_xml like '10%' or hora_xml like '11%'")

	rows = cursor.fetchall()

	for lista in rows:
		if int(lista[0].split(':')[0]) < 10:
			hora = "0" + lista[0]
		else:
			hora = lista[0]
		lista_tiempo.append(hora)
		lista_espiras.append(str(lista[1]))
		lista_nivelServicio.append(lista[2])

	eje_x = []
	eje_x = lista_tiempo
	#print(eje_x)

	eje_z = []
	eje_z = lista_nivelServicio
	#print(eje_z)

	# Diccionario Espira - Distancia
	with open('espiras_filtradas.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			idelem = str(row['Id'])
			distancia = int(str(row['Dist']).split('.')[0])
			dicc[idelem] = distancia

	eje_y = []
	for i in lista_espiras:
		dist = dicc[i]
		eje_y.append(dist)

	# Scatter Plot
	new_eje_y = []
	x_axis = []
	new_eje_z = []

	eje_x_scatter = []
	eje_y_scatter = []
	eje_color = []

	l = 0
	k = 0
	for i in axis_tiempo:
		j = eje_x[l]
		if i == j:
			pos = axis_tiempo.index(i)
			value = axis_tiempo_int[pos]
			new_eje_y = eje_y[k:k+70]
			eje_y_scatter.extend(eje_y[k:k+70])
			new_eje_z = eje_z[k:k+70]
			eje_color.extend(eje_z[k:k+70])
			for q in range(0, len(new_eje_y)):
				x_axis.append(value)
			eje_x_scatter.extend(x_axis)

			new_eje_y = []
			x_axis = []
			new_eje_z = []

			k = k + 70
			l = l + 70
		
		if l >= len(eje_x):
			break

	ax.scatter(eje_x_scatter, eje_y_scatter, alpha=0.2, c = eje_color, cmap="Purples")
	ax.legend()

	#PLOT
	my_xticks = []

	a = ax.get_xticks()
	for i in a:
		if int(i) in list_axis_tiempo_int:
			pos = list_axis_tiempo_int.index(int(i))
			my_xticks.append(axis_tiempo[pos])
		else:
			my_xticks.append('')

	plt.xticks(a, my_xticks)

	#Leyenda
	#ax.legend()

	plt.show()	

