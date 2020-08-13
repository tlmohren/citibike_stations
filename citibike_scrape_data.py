import json
import requests
import time
import sys
import datetime

SOURCE_URL = "http://gbfs.citibikenyc.com/gbfs/gbfs.json"
SLEEP_DURATION = 10

data_urls = requests.get(SOURCE_URL).json()
station_status_url = data_urls["data"]["en"]["feeds"][2]["url"]

# initialize data dictionary
data_dict = {}
station_status = requests.get(station_status_url).json()
for station in station_status["data"]["stations"]:
    station_id = station["station_id"]
    station_time = station["last_reported"]

    subsubdict = {
        "num_bikes_available": station["num_bikes_available"],
        "num_ebikes_available": station["num_ebikes_available"],
    }
    subdict = {station_time: subsubdict}
    data_dict[station_id] = subdict

starttime = datetime.datetime.now()
while True:
    station_status = requests.get(station_status_url).json()

    for station in station_status["data"]["stations"]:

        station_id = station["station_id"]
        station_time = station["last_reported"]
        if station_time not in data_dict[station_id]:
            subsubdict = {
                "num_bikes_available": station["num_bikes_available"],
                "num_ebikes_available": station["num_ebikes_available"],
            }
            subdict = {station_time: subsubdict}
            olddict = data_dict[station_id]
            data_dict[station_id] = {**olddict, **subdict}
    time.sleep(SLEEP_DURATION)

    run_duration = datetime.datetime.now() - starttime
    if run_duration.seconds / 60 >= 1.0:
        break

    print(f"Run duration: {run_duration.seconds}")


with open("station_data.json", "w") as outfile:
    json.dump(data_dict, outfile)

