import json
import requests
import time
import datetime
import numpy as np

# save constants
SOURCE_URL = "http://gbfs.citibikenyc.com/gbfs/gbfs.json"
SLEEP_DURATION = 10
END_RECORDING = datetime.datetime(2020, 8, 25, 12, 0, 0)
SAVE_CONDITION = {"microsecond": 0, "second": 0}  # save every minute
# SAVE_CONDITION = {"microsecond": 0, "second": 0, "minute":0}  # save every hour
# SAVE_CONDITION = {"microsecond": 0, "second": 0, "hour":0}  # save every day


data_urls = requests.get(SOURCE_URL).json()
station_status_url = data_urls["data"]["en"]["feeds"][2]["url"]


def floor_datetime(timeobj, round_sec=5):
    floor_sec = int(np.floor(timeobj.second / round_sec) * round_sec)
    tfloor = timeobj.replace(second=floor_sec, microsecond=0)
    return tfloor


data_dict = {}
last_looptime = datetime.datetime.now().replace(microsecond=0, second=0)

while True:
    loop_time = datetime.datetime.now()
    print(f"loop startime: {loop_time}")

    station_status = requests.get(station_status_url).json()
    for station in station_status["data"]["stations"]:
        station_id = station.get("station_id", "-1")
        station_time = station.get("last_reported", 100)

        try:
            data_dict[station_id]
        except KeyError:
            data_dict[station_id] = {}

        if station_time not in data_dict[station_id]:
            subsubdict = {
                "num_bikes_available": station["num_bikes_available"],
                "num_ebikes_available": station["num_ebikes_available"],
            }
            subdict = {station_time: subsubdict}
            olddict = data_dict[station_id]
            data_dict[station_id] = {**olddict, **subdict}

    # save if you passed a minute mark
    new_looptime = loop_time.replace(**SAVE_CONDITION)

    if new_looptime > last_looptime:
        last_looptime = new_looptime
        now_time = loop_time.strftime("%Y%m%d_%H%M%S")
        filename = "data/citibike_stations_" + now_time + ".json"
        print(f"Saving file: {filename}")

        with open(filename, "w") as outfile:
            json.dump(data_dict, outfile)
        data_dict = {}

    # break loop after end of duration
    if loop_time > END_RECORDING:
        print("End of script")
        break

    tnow = datetime.datetime.now()

    # compute sleep time
    delta_sec = datetime.timedelta(seconds=SLEEP_DURATION)
    t_add = tnow + delta_sec
    end_sleep_goal = floor_datetime(t_add, round_sec=SLEEP_DURATION)
    actual_dt = end_sleep_goal - tnow
    loop_duration = actual_dt.seconds + actual_dt.microseconds / 1e6

    time.sleep(loop_duration)
