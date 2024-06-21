import mlflow
import eia_forecast as fc
import eia_mlflow
import pandas as pd
import numpy as np
import datetime
from darts import TimeSeries


def check_args(self, args):
    arg_flag = False
    arg_missing = []
    for i in args:
        if not hasattr(self, i):
            arg_flag = True
            arg_missing.append(i)
    if arg_flag:
        print("Error: The following arguments are missings:", *arg_missing, sep = ", ")
        return False
    else:
        return True
    
    
def object_items(self):
    list = [l for l in dir(self) if not l.startswith('__')]
    return list

def object_to_list(self):
    
    d = {}
    
    for i in object_items(self):
        if not callable(getattr(self, i)):
            d[i] = getattr(self, i)  

    return d


class forecast_object:
    def __init__(self):
        self.object = "forecast"

    def add_input(self, input):
        self.input = input

    def add_model_params(self, model_params):
        self.model_params = model_params
    
    def add_mlflow_settings(self, mlflow_settings):
        self.mlflow_settings = mlflow_settings

    def create_forecast(self):
        args_flag = check_args(self = self, args = ["input", "model_params", "mlflow_settings"])
        if not args_flag:
            return
        md = train_model(input = self.input, 
                         model_params = self.model_params, 
                         mlflow_settings = self.mlflow_settings)
        
        run_output = object_to_list(md.run.info)
        forecast = md.model.forecast
        forecast["label"] = self.input.forecast_label
        forecast["experiment_id"] = run_output["_experiment_id"]
        forecast["run_id"] = run_output["_run_id"]
        forecast_meta = {"label": self.input.forecast_label,
                         "experiment_id": run_output["_experiment_id"],
                         "run_id": run_output["_run_id"]}
        
        md.model.log.update(forecast_meta)
        self.forecast_meta = forecast_meta
        self.mlflow_meta = md.meta.__dict__ 
        self.mlflow_run = run_output
        self.forecast = forecast
        self.model_meta = md.model.log
        self.model = md.model.model

        


class fc_obj:
    def __init__(self, input, model_params, mlflow_params):
        self.input = input
        self.model_params = model_params
        self.mlflow_params = mlflow_params
        
    def train_forecast(self):
        forecast = train_model(input = self.input, 
                    model_params = self.model_params, 
                    mlflow_params = self.mlflow_params)
        return forecast

class model_params:
    def __init__(self, model, model_label, comments, 
                 h, lags, freq, num_samples, pi, train_length, 
                 likelihood, quantiles, seed):
        self.model = model
        self.model_label = model_label
        self.forecast_label = None
        self.comments = comments
        self.h = h
        self.num_samples = num_samples
        self.lags = lags
        self.freq = freq
        self.pi = pi
        self.train_length = train_length
        self.likelihood = likelihood
        self.quantiles = quantiles  
        self.seed = seed
    
    def print(self):
        print(f"Model: {self.model}\nModel Label: {self.model_label}\nForecast Label: {self.forecast_label}\nComments: {self.comments}")
        print(f"Horizon: {self.h}\nLags: {self.lags}\nFreuqency: {self.freq}")
        print(f"Prediction Intervals: {self.pi}\nNumber of Samples:{self.num_samples}\nTraining Length: {self.train_length}")
        print(f"Likelihood: {self.likelihood}\nQuantiles: {self.quantiles}\nSeed: {self.seed}")


class mlflow_params:
    def __init__(self, path, experiment_name, type, append, version, score, label = None):
        self.path = path
        self.experiment_name = experiment_name
        self.type = type
        self.append = append
        self.score = score
        self.version = version
        self.label = label

    def print(self):
        print(f"Path: {self.path}\nExperiment Name: {self.experiment_name}")
        print(f"Type: {self.tags}\nScore: {self.score}")
        print(f"Version: {self.version}\nAppend: {self.append}")


def model_register(model_params, mlflow_settings):
    class mlflow_metadata:
        def __init__(self, meta, run):
            self.meta = meta
            self.run = run
        
    ex = eia_mlflow.check_experiment(mlflow_settings.experiment_name)
    
    if not mlflow_settings.append and ex.experiment_exists:
        id = ex.experiment_meta["experiment_id"]
        print("Deleting previous experiment: " + id)
        mlflow.delete_experiment(experiment_id = id)
    tags = {"type": mlflow_settings.type, 
            "score": mlflow_settings.score, 
            "version": mlflow_settings.version}
    meta = eia_mlflow.start_experiminet(experiment_name = mlflow_settings.experiment_name,
                                        mlflow_path = mlflow_settings.path,
                                        tags = tags)
        
    with mlflow.start_run(run_name = mlflow_settings.label,
                          experiment_id=meta.experiment_id,
                          tags = tags) as run:
                mlflow.log_params(params = model_params)
                
    output = mlflow_metadata(meta = meta, run = run)
    return output



def train_model(input, model_params, mlflow_settings):
    
    class model:
         def __init__(self, model, meta, run):
              self.model = model
              self.meta = meta
              self.run = run

    mlflow_settings.label = str(input.start.date())
    
    if model_params["model"] == "LinearRegressionModel":
        md = fc.train_ml(input = input, 
                         model = model_params["model"],
                         lags = model_params["lags"], 
                         likelihood = model_params["likelihood"],  
                         quantiles = model_params["quantiles"], 
                         h = model_params["h"], 
                         num_samples = model_params["num_samples"], 
                         seed = model_params["seed"], 
                         pi = model_params["pi"])
        
        md_reg = model_register(model_params= model_params, 
                   mlflow_settings = mlflow_settings)
        output = model(model = md, meta = md_reg.meta, run = md_reg.run)
    else:
        print("The model argument is not valid")
        return
    
    return output



def set_input(input, start, end):
    class ts:
        def __init__(self, ts, start, forecast_start, forecast_label, end = None):
            self.ts = ts
            self.start = start
            self.end = end
            self.forecast_start = forecast_start
            self.forecast_label = forecast_label
            
    if end is None:
        end = input["period"].max()
    
    d = input[(input["period"] >= start) & (input["period"] <= end)]
    ts_raw = pd.DataFrame(np.arange(start = d["period"].min(), 
                                    stop = d["period"].max() + datetime.timedelta(hours = 1), 
                                    step = datetime.timedelta(hours = 1)).astype(datetime.datetime), columns=["index"])
    ts_raw  = ts_raw.merge(d, left_on = "index", right_on = "period", how="left")
    forecast_start = end + datetime.timedelta(hours = 1)
    forecast_label =  str(forecast_start.date())

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
    ts_raw = ts_raw.sort_values(by = ["period"])
    ts_obj = TimeSeries.from_dataframe(ts_raw,time_col= "period", value_cols= "value")
    output = ts(ts = ts_obj,
                start = start,
                end = end,
                forecast_start = forecast_start,
                forecast_label = forecast_label)
    
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
    

    if not init:
        fc_archive = pd.read_csv(fc_path)
        fc_archive["period"] = pd.to_datetime(fc_archive["period"])
        print("Append the new forecast")
        # fc["label"] = fc_new.log["label"]
        fc_new = fc_archive._append(fc)
    else:
        fc_new = fc
        
    if save:
        print("Save the updated forecast as CSV file")
        fc_new.to_csv(fc_path, index = False)
    
    return fc_new

def get_last_fc_start(log_path, subba):
    class forecast_metadata:
        def __init__(self, start, end, start_new, experiment_id, run_id, subba):
            self.start = start
            self.end = end
            self.start_new = start_new
            self.experiment_id = experiment_id
            self.run_id = run_id
            self.subba = subba
    
    fc_log = pd.read_csv(log_path)
    fc_log = fc_log[(fc_log["success"] == True) & (fc_log["subba"] == subba) ]
    fc_log = fc_log[fc_log["index"] == fc_log["index"].max()]
    fc_log["start_act"] = pd.to_datetime(fc_log["start_act"])
    fc_log["end_act"] = pd.to_datetime(fc_log["end_act"])
    start = fc_log["start_act"].iloc[0]
    end = fc_log["end_act"].iloc[0]
    experiment_id = fc_log["experiment_id"].iloc[0]
    run_id = fc_log["run_id"].iloc[0]
    start_new = end  + datetime.timedelta(hours = 1) 

    output = forecast_metadata(start = start,
                               end = end,
                               start_new = start_new,
                               experiment_id = experiment_id,
                               run_id = run_id,
                               subba = subba)

    
    return output






