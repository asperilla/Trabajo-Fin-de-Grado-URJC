#bin/bash!
pwd
cd /home/sergioaspe/Escritorio/Script_Server
pwd

while true
do
	python3 save_info_buses.py
	sleep 5
done
