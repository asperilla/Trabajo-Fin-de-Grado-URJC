import requests
import json
from datetime import datetime, time, sys
import csv
import sqlite3


def get_token():
	url = "https://openapi.emtmadrid.es/v1/mobilitylabs/user/login"

	headers = {
		'email': 'xxx',
		'password':'xxx'
		}

	response = requests.request('GET', url, headers=headers)
	valid_token = json.loads(response.text)['data'][0]['accessToken']
	
	return valid_token	


def find_closest(array, value):
	for i in range(0, len(array)):
		num = array[i]
		resta = value - int(num)
		if resta <= 0:
			return array[i-1]

def time_arrival_bus(valid_token, stop_id, stop_distance, cursor, list_id_buses):
	url = "https://openapi.emtmadrid.es/v1/transport/busemtmad/stops/" + str(stop_id) + "/arrives/1/"

	now = datetime.now()
	today_date = str(now.date())
	today = today_date.split('-')[0] + today_date.split('-')[1] + today_date.split('-')[2]

	now = str(now)
	date = now.split(' ')[0] + ' ' + now.split(' ')[1].split('.')[0]
	print(date)



	payload = {
		'cultureInfo': 'ES',
		'Text_StopRequired_YN': 'Y',
		'Text_EstimationsRequired_YN': 'Y',
		'Text_IncidencesRequired_YN': 'Y',
		'DateTime_Referenced_Incidencies_YYYYMMDD': today
		}


	headers = {
		'Content-Type': 'text/plain',
		'Accept' : 'text/plain',
    	'accessToken': valid_token
    	}

	response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
	json_file = json.loads(response.text)

	for item in json_file['data']:
		if item['Arrive'] == []:
			return 'null'
		else:
			lista_distance_buses = []
			for bus in item['Arrive']:
				bus_ident = bus['bus']
				distance_to_stop = bus['DistanceBus']
				stop_ident = bus['stop']
				distance = int(stop_distance) - int(distance_to_stop)

				lista_distance_buses.append(distance)
				if 0 <= distance <= 8795 and bus_ident not in list_id_buses:
					list_id_buses.append(bus_ident)
					cursor.execute("INSERT INTO Datos_Buses (fecha, id_bus, distancia_to_stop, distancia_bus, id_parada, distancia_parada) VALUES (?, ?, ?, ?, ?, ?)",
					(date, str(bus_ident), str(distance_to_stop), str(distance), str(stop_ident), str(stop_distance)))

			distance_min_bus = min(lista_distance_buses)

			return distance_min_bus				
			

if __name__ == "__main__":
	
	# Diccionario paradas y su distancia
	dicc_stops = {}
	dicc_stops_reverse = {}
	list_stops = []

	with open('lineas_paradas.csv') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['line'] == '1' and row['secDetail'] == '10':
				id_stop = row['node']
				distance = row['distance']
				list_stops.append(distance)
				dicc_stops[distance] = id_stop
				dicc_stops_reverse[id_stop] = distance


	# Get a valid token to do request to the EMT api
	valid_token = get_token()

	#Creación de la base de datos
	bd = sqlite3.connect("Buses.db")
	cursor = bd.cursor()

	#Creamos la tabla en la base de datos
	cursor.execute('CREATE TABLE IF NOT EXISTS Datos_Buses (fecha TEXT, id_bus TEXT, distancia_to_stop TEXT, distancia_bus TEXT, id_parada TEXT, distancia_parada TEXT)')

	# POST a Prosperidad (última parada)
	list_id_buses = []
	distance_min_bus = time_arrival_bus(valid_token, 273, 8795, cursor, list_id_buses)
	bd.commit()
	
	while distance_min_bus != 'null' and distance_min_bus > 0 and distance_min_bus <= 8795:
		valid_token = get_token()
		stop_to_post = dicc_stops[find_closest(list_stops, distance_min_bus)]	
		stop_distance = dicc_stops_reverse[stop_to_post]
		distance_min_bus = time_arrival_bus(valid_token, stop_to_post, stop_distance, cursor, list_id_buses)
		bd.commit()
		
	# FIN del barrido a la línea
	cursor.close()
	bd.close()

				
