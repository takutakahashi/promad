import os
from ast import literal_eval
import datetime
import requests
import json
import pandas as pd
import yaml
import pmdarima as pm


def env_defined():
    if os.environ.get("PROM_API_URL") == "":
        return "env PROM_API_URL is not defined. ex: http://localhost:9090/api/v1"
    if os.environ.get("RULES_PATH") == "":
        return "env RULES_PATH is not defined. ex: /path/to/rules.yaml"
    return ""


def arima_orders():
    return literal_eval(os.environ.get("ARIMA_ORDER")), literal_eval(os.environ.get("ARIMA_SEASONAL_ORDER"))


def query_current(query):
    prom_api_url = os.environ.get("PROM_API_URL")
    query_api = prom_api_url + "/query"
    res = requests.get(query_api + "?query={}".format(query))
    if os.environ.get("PROMAD_DEBUG") == "true":
        print(res.status_code)
        print(res.content)
    data = json.loads(res.content)
    return data["data"]["result"][0]["value"]


def val_to_series(values):
    y = [v[1] for v in values]
    x = [datetime.datetime.fromtimestamp(v[0]) for v in values]
    return pd.Series(y, index=x)


def query_range(query):
    prom_api_url = os.environ.get("PROM_API_URL")
    query_range = prom_api_url + "/query_range"
    end = int(datetime.datetime.now().timestamp() - 60 * 60 * 1)
    start = datetime.datetime.now().timestamp() - 60 * 60 * 24 * 3
    step = 3600
    res = requests.get(
        query_range + "?query={}&start={}&end={}&step={}".format(query, start, end, step))
    if os.environ.get("PROMAD_DEBUG") == "true":
        print(res.status_code)
        print(res.content)
    data = json.loads(res.content)
    values = data["data"]["result"][0]["values"]
    return values


def find_current_value(predict, conf_int):
    now = datetime.datetime.now()
    i = 0
    if os.environ.get("PROMAD_DEBUG"):
        print("=== predict ===")
        print(predict)
        print("=== conf_int ===")
        print(conf_int)
    selected_conf_int, selected_k, selected_v = None, None, None
    for k, v in predict.items():
        if selected_k is None:
            selected_k = k
            selected_v = v
            selected_conf_int = conf_int[i]
        if os.environ.get("PROMAD_DEBUG"):
            print("------")
            print(k)
            print(abs((now - k).seconds))
            print(selected_k)
            print(abs((now - selected_k).seconds))
            print(i)
            print("------")
        if abs((now - k).seconds) < abs((now - selected_k).seconds):
            selected_k = k
            selected_v = v
            selected_conf_int = conf_int[i]
        i += 1
    return selected_k, selected_v, selected_conf_int


def to_exporter_metrics(d):
    ret = []
    for metric_name, data in d.items():
        ret.append('promad_anomaly_band{name=\"%s\", type="range_max"} %f' % (
            metric_name, data["predict"]["range_max"]))
        ret.append('promad_anomaly_band{name=\"%s\", type="range_min"} %f' % (
            metric_name, data["predict"]["range_min"]))
        ret.append('promad_anomaly_band{name=\"%s\" type="actual"} %s' %
                   (metric_name, data["actual"]["value"]))
        ret.append('promad_anomaly_info{name=\"%s\", type="predicted"} %f' %
                   (metric_name, data["predict"]["value"]))
        ret.append('promad_anomaly_info{name=\"%s\", type="error"} %f' % (metric_name, abs((float(
            data["actual"]["value"]) - data["predict"]["value"])/data["predict"]["value"])))
        ret.append('promad_anomaly_detected{name=\"%s\"} %f' % (
            metric_name, data["actual"]["out_of_range"]))
    return "\n".join(ret)


def parse_rules():
    with open(os.environ.get("RULES_PATH")) as f:
        return yaml.safe_load(f)


def fit_model():
    return {v["name"]: pm.ARIMA(
        order=literal_eval(v["arima"]["order"]),
        seasonal_order=literal_eval(v["arima"]["seasonal_order"])
    ).fit(
        y=val_to_series(query_range(v["query"]))
    ) for v in parse_rules()}
