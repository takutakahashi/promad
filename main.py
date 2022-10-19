from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

import lib.lib as lib

app = FastAPI()

app.models = lib.fit_model()


@app.get("/")
async def root():
    return {"metrics": list(app.models.keys())}


@app.post("/fit")
async def fit():
    app.models = lib.fit_model()
    return {"metrics": list(app.models.keys())}


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    ret = {}
    for k, model in app.models.items():
        predict, conf_int = model.predict(
            n_periods=12, return_conf_int=True)
        _, predict_value, ci = lib.find_current_value(predict, conf_int)
        value = lib.query_current()
        ret[k] = {
            "predict": {
                "value": predict_value,
                "range_max": ci[1],
                "range_min": ci[0]
            },
            "actual": {
                "value": value[1],
                "out_of_range": 0 if ci[0] < float(value[1]) < ci[1] else 1
            }
        }
    return lib.to_exporter_metrics(ret)
