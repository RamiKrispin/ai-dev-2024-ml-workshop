import eia_api
import eia_etl as etl
import eia_forecast as fc
import eia_mlflow
import mlflow
import os
import datetime
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from statistics import mean
from pathlib import Path
from ydata_profiling import ProfileReport
from zoneinfo import ZoneInfo
from darts import TimeSeries
from darts.models.forecasting.linear_regression_model import LinearRegressionModel

freq = 24
h = 24
overlap = 0
tags = {"type:": "backfill", "version": "0.0.0.9000"}
experiment_name = "Forecast-Deployment"
mlflow_path = "./metadata/"


quantiles = [0.025, 0.1, 0.25, 0.5, 0.75, 0.9, 0.975]

params = {
    "model": "LinearRegressionModel",
    "model_label": "model 1",
    "comments": "LM model with lags, training with 2 years of history",
    "h": h,
    "freq": freq,
    "num_samples": 500,
    "lags": [ -freq, -7 * freq,  - 365 * freq],
    "likelihood": "quantile",
    "quantiles": quantiles,
    "pi": 0.95,
    "train": 24*365*2,
    "seed": 12345
    }

mlflow_params = {
    "path": "./metadata/",
    "experiment_name": "Forecast-Deployment",
    "tags": {"type": "backfill", "version": "0.0.0.9000"}
}
log_path = "data/fc48_metadata.csv"
fc_path = "data/fc48.csv"



data = pd.read_csv("./data/us48.csv")
data["period"] = pd.to_datetime(data["period"])
end = data["period"].max().floor(freq = "d")  - datetime.timedelta(hours = 1)
data = data[data["period"] <= end]
data.tail

start = end - datetime.timedelta(hours = params["train"])

forecast_start = data["period"].max().floor(freq = "d")
last_start = fc.get_last_fc_start(log_path = log_path)
input = fc.set_input(input = data, start = start, end = end)

def train_fc(params, 
             input, 
             mlflow_params, 
             append = True):
    
    class model:
        def __init__(output, model, meta, label):
            output.model = model
            output.meta = meta
            output.label = label

    label = str(input.start.date())



    if params["model"] == "LinearRegressionModel":
        md = fc.train_lm(input = input, 
                         lags = params["lags"], 
                         likelihood = params["likelihood"],  
                         quantiles = params["quantiles"], 
                         h = params["h"], 
                         num_samples = params["num_samples"], 
                         seed = params["seed"], 
                         pi = params["pi"])
        
        meta = model_register(model_params= params, 
                   mlflow_params = mlflow_params, 
                   label = label,
                   append = append)
        

    else:
        print("The model argument is not valid")
        return
    
    output = model(model = md, meta = meta, label = label)
    
    return output


def model_register(model_params, mlflow_params, label, append):
        
    ex = eia_mlflow.check_experiment(mlflow_params["experiment_name"])
    
    if not append and ex.experiment_exists:
        id = ex.experiment_meta["experiment_id"]
        print("Deleting previous experiment: " + id)
        mlflow.delete_experiment(experiment_id = id)
    
    meta = eia_mlflow.start_experiminet(experiment_name = mlflow_params["experiment_name"],
                                        mlflow_path = mlflow_params["path"],
                                        tags = mlflow_params["tags"])
        
    with mlflow.start_run(run_name = label,
                          experiment_id=meta.experiment_id,
                          tags = {"type": "forecast",  
                                  "label": label}) as run:
                mlflow.log_params(params = model_params)
                
    
    return meta

def score_model():
    
    return True


def bkt_score(bkt_grid, params, input, meta):
    
    class model_score:
        def __init__(output, score, summary):
            output.score = score
            output.summary = summary
    
    score = None
    print("Model: " + params["model_label"])
    for index, row in bkt_grid.iterrows():
        start = row["train_start"]
        end = row["train_end"]
        ts_train = fc.set_input(input = input, start = start, end = end)
        test_start = row["test_start"]
        test_end = row["test_end"]
        label = str(test_start.date())
        test = input[(input["period"] >= test_start) &  (input["period"] <= test_end)]

        if params["model"] == "LinearRegressionModel":
            f = fc.train_lm(input =  ts_train, 
                            lags = params["lags"],
                            likelihood = params["likelihood"],
                            quantiles = params["quantiles"],
                            h = params["h"],
                            pi = params["pi"],
                            num_samples = params["num_samples"])
        else:
            print("The model argument is not valid")

        f_df = test.merge(f.forecast, on = "period", how = "left")
        
        mape =  mean(abs(f_df["value"] - f_df["mean"]) / f_df["value"])
        rmse = (mean((f_df["value"] - f_df["mean"]) ** 2 )) ** 0.5
        coverage = sum((f_df["value"] <= f_df["upper"]) & (f_df["value"] >= f_df["lower"])) / len(f_df)

        metrics = {"mape": mape, 
                   "rmse": rmse, 
                   "coverage": coverage} 
        
        with mlflow.start_run(run_name = label,
                              experiment_id=meta.experiment_id,
                              tags = {"type": "backtesting", 
                                      "partition": row["partition"], 
                                      "label": label}) as run:
                mlflow.log_params(params = params)
                mlflow.log_metrics(metrics = metrics)

        score_temp = pd.DataFrame([{"forecast_label": label, 
                                    "model_label": params["model_label"],
                                    "model": params["model"],
                                    "partition": row["partition"],
                                    "mape": mape, 
                                    "rmse": rmse, 
                                    "coverage": coverage,
                                    "run_id": run.info.run_id,
                                    "comments": params["comments"]}])
       
        if score is None:
            score = score_temp
        else:
            score = score._append(score_temp)

    score.reset_index(inplace = True, drop = True)

    score_summary = pd.DataFrame([{"forecast_label": label, 
                                    "model_label": params["model_label"],
                                    "model": params["model"],
                                    "mape": score["mape"].mean(), 
                                    "rmse": score["rmse"].mean(), 
                                    "coverage": score["coverage"].mean(),
                                    "comments": params["comments"]}])
    score_summary.reset_index(inplace = True, drop = True)
    output = model_score(score = score, summary = score_summary)

    return output



md = train_fc(params = params,
         input = input,
         mlflow_params = mlflow_params,
         append = True)
        
    



