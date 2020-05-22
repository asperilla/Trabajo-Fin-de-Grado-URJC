import requests
import json
from datetime import timedelta,date,datetime, time, sys
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

if __name__ == "__main__":

	# Get a valid token to do request to the EMT api
	valid_token = get_token()


	# Fecha y hora actual
	now = datetime.now()
	#print(now)
	today_date = str(now.date())
	today = today_date.split('-')[0] + today_date.split('-')[1] + today_date.split('-')[2]
	#print(today)

	"""
	url = "https://openapi.emtmadrid.es/v1/transport/busemtmad/lines/1/info/20191124/"

	headers = {
		'Content-Type': 'text/plain',
		'Accept' : 'text/plain',
    	'accessToken': valid_token
    	}

	response = requests.request("GET", url, headers=headers)
	json_file = json.loads(response.text)

	print(json_file)"""


	# Llamada a la función timetable trips de la API
	url = "https://openapi.emtmadrid.es/v1/transport/busemtmad/lines/1/trips/20200312/"

	headers = {
		'Content-Type': 'text/plain',
		'Accept' : 'text/plain',
    	'accessToken': valid_token
    	}

	response = requests.request("GET", url, headers=headers)
	json_file = json.loads(response.text)

	list_ordenada = []
				
	l = 1
	for item in json_file['data']:
		if item['direction'] == "1":# and item['tripNum'] == "0001": # and item['logicBus'] == "007":# and item['tripNum'] == "0002":
			#if item['startTimeTrip'].split(':')[0] == '14':# or item['startTimeTrip'].split(':')[0] == '10':# or item['startTimeTrip'].split(':')[0] == '17':
			list_ordenada.append([item['startTimeTrip'],item['endTimeTrip']])
			print(item['startTimeTrip'])
			print(item['endTimeTrip'])
			print()
			l = l + 1

	print(sorted(list_ordenada))

	print(l)

