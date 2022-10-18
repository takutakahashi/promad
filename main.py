from fastapi import FastAPI
import pmdarima as pm
import datetime

import lib.lib as lib

app = FastAPI()
print(lib.parse_rules())
order, seasonal_order = lib.arima_orders()
#models = {v["name"]: pm.ARIMA(order=order, seasonal_order=seasonal_order).fit(
#    lib.query_range(v["query"])) for v in lib.parse_rules()}
models = {v["name"]: pm.ARIMA(order=order, seasonal_order=seasonal_order).fit(y=lib.val_to_series(lib.query_range(v["query"]))) for v in lib.parse_rules()}


@app.get("/")
async def root():
    return {"message": "hello"}


@app.get("/metrics")
async def metrics():
    predict, conf_int = models["pod_cpu"].predict(n_periods=12, return_conf_int=True)
    predict_time, predict_value, ci = lib.find_current_value(predict, conf_int)
    value = lib.query_current()
    return {
        "predict": {
            "time": predict_time,
            "value": predict_value,
            "range_max": ci[1],
            "range_min": ci[0]
        },
        "actual": {
            "time": datetime.datetime.fromtimestamp(value[0]),
            "value": value[1],
            "in_range": 1 if ci[0] < float(value[1]) < ci[1] else 0
        }
    }
