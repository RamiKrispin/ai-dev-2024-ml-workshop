import pandas as pd
import numpy as np
import datetime
from darts import TimeSeries
from darts.models import LinearRegressionModel, XGBModel
from zoneinfo import ZoneInfo
from statistics import mean

def train_ml(input, 
             lags, 
             likelihood, 
             quantiles, 
             h, 
             num_samples, 
             model,
             seed = 12345,
             pi = 0.95):
    
    class forecast:
        def __init__(output, model, forecast, log):
            output.model = model
            output.forecast = forecast
            output.log = log
    
    start = input.forecast_start
    ts = input.ts
    lower = (1-pi) /2
    upper = 1 - lower
    if model == "LinearRegressionModel":
        md = LinearRegressionModel(lags= lags,
                                 likelihood= likelihood, 
                                 random_state = seed,
                                 quantiles = quantiles)
    elif model == "XGBModel":
                md = XGBModel(lags= lags,
                                 likelihood= likelihood, 
                                 random_state = seed,
                                 quantiles = quantiles)
    md.fit(ts)
    md_preds = md.predict(series = ts, 
                                n = h,
                                num_samples = num_samples)
    
    pred = md_preds.pd_dataframe()
    fc = pred.quantile(axis = 1, q = [lower, 0.5, upper]).transpose().reset_index()
    fc = fc.rename(columns = {lower: "lower", 0.5: "mean", upper: "upper"})
    
    log = {
        "index": None,
        "model": model,
        "time": datetime.datetime.now(tz=ZoneInfo("UTC")).strftime('%Y-%m-%d %H:%M:%S'),
        "label": str(start.date()),
        "start": start,
        "start_act": fc["period"].min(),
        "end_act": fc["period"].max(),
        "h": h,
        "n_obs": len(fc),
        "start_flag": fc["period"].min() == start,
        "n_obs_flag": h == len(fc),
        "model": "LinearRegressionModel",
        "pi":  0.95,
        "score": False,
        "mape": None,
        "rmse": None,
        "coverage": None
    }

    log["success"] = log["start_flag"] and log["n_obs_flag"]

    output = forecast(model = md, forecast = fc, log = log)

    return output



def set_input(input, start, end):
    class ts:
        def __init__(output, ts, start, forecast_start, end = None):
            output.ts = ts
            output.start = start
            output.end = end
            output.forecast_start = forecast_start
            
    if end is None:
        end = input["period"].max()
    
    d = input[(input["period"] >= start) & (input["period"] <= end)]
    ts_raw = pd.DataFrame(np.arange(start = d["period"].min(), 
                                    stop = d["period"].max() + datetime.timedelta(hours = 1), 
                                    step = datetime.timedelta(hours = 1)).astype(datetime.datetime), columns=["index"])
    ts_raw  = ts_raw.merge(d, left_on = "index", right_on = "period", how="left")
    if ts_raw["period"].isnull().sum() > 0:
        m = ts_raw["period"].isnull().sum()
        print("There are " + str(m) + " missing values in the series")
        y = pd.DataFrame(ts_raw["period"].isnull())
        n = y[y["period"] == True].index

        for i in n:
            if i > 24:
                ts_raw.loc[i, "value"] = ts_raw.loc[i - 24, "value"]
            else:
                ts_raw.loc[i, "value"] = ts_raw.loc[i + 24, "value"]
            ts_raw.loc[i, "period"] = ts_raw.loc[i, "index"]
    

    forecast_start = end + datetime.timedelta(hours = 1)
    ts_obj = TimeSeries.from_dataframe(ts_raw,time_col= "period", value_cols= "value")
    output = ts(ts = ts_obj,
                start = start,
                end = end,
                forecast_start = forecast_start)
    
    return output


def append_log(log_path, new_log, save = False, init = False):
    
    new_log = pd.DataFrame([new_log])

    if not init:
        fc_meta = pd.read_csv(log_path)
        fc_meta["start_act"] = pd.to_datetime(fc_meta["start_act"])
        fc_meta["end_act"] = pd.to_datetime(fc_meta["end_act"])
        new_log["index"] = fc_meta["index"].max() + 1
 
        print("Update the forecast metadata")

        
        fc_meta_new = fc_meta._append(new_log)
    else:
        fc_meta_new = new_log
        fc_meta_new["index"] = 1

    if save:
        print("Save the forecast into CSV file")
        fc_meta_new.to_csv(log_path, index = False)
    
    return fc_meta_new

def append_forecast(fc_path, fc_new, save = False, init = False):
    
    
    fc = fc_new.forecast
    fc["label"] = fc_new.log["label"]

    if not init:
        fc_archive = pd.read_csv(fc_path)
        fc_archive["period"] = pd.to_datetime(fc_archive["period"])
        print("Append the new forecast")
        fc["label"] = fc_new.log["label"]
        fc_new = fc_archive._append(fc)
    else:
        fc_new = fc
        
    if save:
        print("Save the updated forecast as CSV file")
        fc_new.to_csv(fc_path, index = False)
    
    return fc_new


def score_forecast(data_path, forecast_path, forecast_log_path, save = False):
    input = pd.read_csv(data_path)
    input["period"] = pd.to_datetime(input["period"])

    fc = pd.read_csv(forecast_path)
    fc["period"] = pd.to_datetime(fc["period"])
    fc_log = pd.read_csv(forecast_log_path)
    fc_log["start_act"] = pd.to_datetime(fc_log["start_act"])
    fc_log["end_act"] = pd.to_datetime(fc_log["end_act"])

    for index, row in fc_log.iterrows():
        if row["score"] == False:
            subba = row["subba"]
            label = row["label"]
            start = row["start_act"]
            end = row["end_act"]
            h = row["h"]
            
            d = input[(input["period"] >= start) & (input["period"] <= end) & (input["subba"] == subba)]

            if len(d) > 0:
                d = d[["period", "subba", "value"]]
                f = fc[(fc["label"] == label) & (fc["subba"] == subba)]
                d = d.merge(f, left_on = "period", right_on = "period", how="left")

                fc_log.at[index, "mape"] = mean(abs(d["value"] - d["mean"]) / d["value"])
                fc_log.at[index, "rmse"] = (mean((d["value"] - d["mean"]) ** 2 )) ** 0.5
                fc_log.at[index, "coverage"] =  sum((d["value"] <= d["upper"]) & (d["value"] >= d["lower"])) / len(d)

                if len(d) == h:
                    fc_log.at[index, "score"] = True


    if save:
        fc_log.to_csv(forecast_log_path, index = False)

    return fc_log


def get_last_fc_start(log_path):
    
    fc_log = pd.read_csv(log_path)
    fc_log = fc_log[fc_log["success"] == True]
    fc_log = fc_log[fc_log["index"] == fc_log["index"].max()]
    fc_log["start_act"] = pd.to_datetime(fc_log["start_act"])
    fc_log["end_act"] = pd.to_datetime(fc_log["end_act"])
    last_start = fc_log["start_act"].iloc[0]
    
    return last_start


def load_forecast(fc_path):
    fc = pd.read_csv(fc_path)
    fc["period"] = pd.to_datetime(fc["period"])
    return fc
    
    
