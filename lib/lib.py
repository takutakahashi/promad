import os
from ast import literal_eval
import datetime
import requests
import json
import pandas as pd

def env_defined():
    os.environ.get("PROM_API_URL") and \
    os.environ.get("QUERY") and \
    os.environ.get("ARIMA_ORDER") and \
    os.environ.get("ARIMA_SEAZONAL_ORDER")

def arima_orders():
    return literal_eval(os.environ.get("ARIMA_ORDER")), literal_eval(os.environ.get("ARIMA_SEASONAL_ORDER"))

def query_current():
    prom_api_url = os.environ.get("PROM_API_URL")
    query_api = prom_api_url + "/query"
    query = os.environ.get("QUERY")
    res = requests.get(query_api + "?query={}".format(query))
    data = json.loads(res.content)
    return data["data"]["result"][0]["value"]

def val_to_series(values):
    y = [v[1] for v in values]
    x = [datetime.datetime.fromtimestamp(v[0]) for v in values]
    return pd.Series(y, index=x)

def query_range():
    prom_api_url = os.environ.get("PROM_API_URL")
    query_range = prom_api_url + "/query_range"
    query = os.environ.get("QUERY")
    end = int(datetime.datetime.now().timestamp() - 60 * 60 * 3)
    start = datetime.datetime.now().timestamp() - 60 * 60 * 24 * 7
    step = 3600
    res = requests.get(query_range + "?query={}&start={}&end={}&step={}".format(query, start, end, step))
    data = json.loads(res.content)
    values = data["data"]["result"][0]["values"]
    return values

def find_by_time_from_predict(predict, conf_int):
    now = datetime.datetime.now()
    i = 0
    for k, v in predict.items():
        if (now - k).seconds < 1000:
            return k, v, conf_int[i]
        i += 1

def to_exporter_metrics(d):
    return ""