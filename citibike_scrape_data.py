import json
import requests
import time
import sys
import datetime
import numpy as np

# save constants
SOURCE_URL = "http://gbfs.citibikenyc.com/gbfs/gbfs.json"
SLEEP_DURATION = 10
COLLECTION_SECONDS = 60
SAVE_SPAN_SECONDS = 20

# pre-process data source
data_urls = requests.get(SOURCE_URL).json()
station_status_url = data_urls["data"]["en"]["feeds"][2]["url"]


# define functions ------------
def initialize_data_dict(station_status_url):
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

    return data_dict


# start loop -----------------------------------
starttime = datetime.datetime.now()
times_passed_previous = 0

data_dict = initialize_data_dict(station_status_url)

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

    # sleep until next request
    time.sleep(SLEEP_DURATION)
    run_duration = datetime.datetime.now() - starttime
    print(f"Run duration: {run_duration.seconds}")

    # Save data and reset data dict periodically
    times_passed = np.floor(run_duration.seconds / SAVE_SPAN_SECONDS)
    if times_passed != times_passed_previous:
        times_passed_previous = times_passed
        print("---------")
        print(f"times passed: {times_passed}")

        # if (run_duration.seconds % SAVE_SPAN_SECONDS) == 0:
        now_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        filename = "data/citibike_stations_" + now_time + ".json"
        print(f"Running for {run_duration.seconds}, Saving file: {filename}")
        with open(filename, "w") as outfile:
            json.dump(data_dict, outfile)
        data_dict = initialize_data_dict(station_status_url)

    # break loop after end of duration
    if run_duration.seconds >= COLLECTION_SECONDS:
        print("End of script")
        break

