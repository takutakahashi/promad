from fastapi import FastAPI
from ast import literal_eval
import pmdarima as pm
import datetime
import numpy as np
import requests
import os
import json
import pandas as pd

app = FastAPI()
prom_api_url = os.environ.get("PROM_API_URL")
query_api = prom_api_url + "/query"
query_range = prom_api_url + "/query_range"
query = os.environ.get("QUERY")
end = int(datetime.datetime.now().timestamp() - 60 * 60 * 3)
start = datetime.datetime.now().timestamp() - 60 * 60 * 24 * 7
step = 3600

order = literal_eval(os.environ.get("ARIMA_ORDER"))
seasonal_order = literal_eval(os.environ.get("ARIMA_SEASONAL_ORDER"))
arima_model = pm.ARIMA(order=order,seasonal_order=seasonal_order)
res = requests.get(query_range + "?query={}&start={}&end={}&step={}".format(query, start, end, step))
data = json.loads(res.content)
values = data["data"]["result"][0]["values"]
y = [v[1] for v in values]
x = [datetime.datetime.fromtimestamp(v[0]) for v in values]
s = pd.Series(y, index=x)
arima_model.fit(y=s)

@app.get("/")
async def root():
    return {"message": "hello"}

@app.get("/metrics")
async def metrics():
    now = datetime.datetime.now()
    res = requests.get(query_api + "?query={}".format(query))
    data = json.loads(res.content)
    predict, conf_int = arima_model.predict(n_periods=12, return_conf_int=True)
    i = 0
    for k, v in predict.items():
        if (now - k).seconds < 1000:
            predict_value = v
            predict_time = k
            break
        i += 1
    predict_range_min, predict_range_max = conf_int[i]
    actual_time = datetime.datetime.fromtimestamp(data["data"]["result"][0]["value"][0])
    actual_value = data["data"]["result"][0]["value"][1]
    predict_range_in = predict_range_min < float(actual_value) < predict_range_max
    return {
        "predict": {
            "time": predict_time,
            "value": predict_value,
            "max": predict_range_max,
            "min": predict_range_min
        },
        "actual": {
            "time": actual_time,
            "value": actual_value,
            "in_range": 1 if predict_range_in else 0
        }
    }