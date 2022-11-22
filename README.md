# promad

Anomaly Detection exporter with Prometheus metrics

If you want to get more details, please see below presentation! (Japanese)

https://speakerdeck.com/takutakahashi/sikiizhi-jian-shi-karanozu-ye-prometheus-niyoruji-jie-xue-xi-woyong-itayi-chang-jian-zhi-aratonoshi-zhuang

## Usage

### Write config

Prometheus query, ARIMA param, Seasonal param is needed.

```
- query: up
  order: (1,0,0)
  seasonal_order: (1,0,0)
```

### Execute exporter

Environment Variables PROM_API_URL, RULES_PATH are required.

```

docker run -e PROM_API_URL=http://localhost:9090/api/v1 -e RULES_PATH=path/to/rules.yaml -v $PWD/rules.yaml:path/to/rules.yaml -it ghcr.io/takutakahashi/promad:v0.3.0

```