from fastapi import FastAPI
import pmdarima as pm
import datetime
import numpy as np

app = FastAPI()

arima_model = pm.ARIMA(order=(1,1,0),seasonal_order=(2,1,0,24))

@app.get("/")
async def root():
    return {"message": "hello"}

@app.get("/metrics")
async def metrics():
    after_h = 24 * 7
    y = np.zeros(after_h)
    now = datetime.datetime.now().timestamp()
    y[0] = now
    for t in range(1, after_h):
        y[t] = y[t-1] + 3600
    arima_model.fit(y=y)
    print(arima_model.summary())
    predict, conf_int = arima_model.predict(return_conf_int=True)
    return {"message": "hello"}