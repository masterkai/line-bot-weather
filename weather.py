import time
from dotenv import load_dotenv
import os
import requests
from pprint import pprint as pp
from threading import Thread

load_dotenv()

token = os.getenv("TOKEN")

class Weather:
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001"  # for 有人的氣象站
    url2 = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001"  # for 自動氣象站
    rainURL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"  # for 雨量

    def __init__(self, token):
        self.token = token
        self.result = None
        self.response = None
        self.rain_res = None
        self.urls = [self.url, self.url2, self.rainURL]
        self.info = {}

    # getter for info

    # info to_string method
    def __str__(self):
        return f"觀測時間: {self.info['O']}\n溫度: {self.info['T']}\n濕度: {self.info['H']}\n雨量: {self.info['R']}"

    def grab_all(self, station):
        params = {
            "Authorization": self.token,
            "StationName": station
        }

        def func(url, params):
            x = requests.get(url, params=params)
            if x.json()['records']["Station"]:
                s = x.json()['records']["Station"][0]
                self.info["O"] = s['ObsTime']['DateTime']
                if 'WeatherElement' in s:
                    self.info["T"] = float(s['WeatherElement']["AirTemperature"])
                    self.info["H"] = float(s['WeatherElement']["RelativeHumidity"] / 100)
                elif "RainfallElement" in s:
                    self.info["R"] = float(s['RainfallElement']['Now']['Precipitation'])

        threads = [Thread(target=func, args=(url, params), daemon=True) for url in self.urls]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return self.info

    def get_weather(self, station):
        params = {
            "Authorization": self.token,
            "StationName": station
        }
        try:
            self.response = requests.get(self.url, params=params)
            if self.response.json()['records']["Station"]:
                self.result = self.response.json()['records']["Station"][0]
            else:
                self.response = requests.get(self.url2, params=params)
                self.result = self.response.json()['records']["Station"][0]
        finally:
            rain_res = requests.get(self.rainURL, params=params)
            self.rain_res = rain_res.json()["records"]["Station"][0]["RainfallElement"]["Now"]["Precipitation"]
        return {
            "O": self.result['ObsTime']['DateTime'],
            "T": float(self.result['WeatherElement']["AirTemperature"]),
            "H": float(self.result['WeatherElement']["RelativeHumidity"] / 100),
            "R": float(self.rain_res)
        }


if __name__ == "__main__":
    import argparse

    argparse = argparse.ArgumentParser()
    argparse.add_argument("station",
                          type=str,
                          help="the station you want to get the weather from",
                          default="臺北",
                          )
    args = argparse.parse_args()

    w = Weather(token)
    # pp(w.get_weather("臺北"))
    pp(w.grab_all(args.station))
    print(w.__str__())

