import mlflow
import pandas as pd
import eia_forecast as fc
import eia_mlflow
from statistics import mean
import plotly.express as px
import plotly.subplots as sp

def create_partitions(input, partitions, overlap, h, train = None):
    df = None

    for i in range(partitions, 0, -1):
        if train is None:
            s = 1
        else:
            s = len(input) - train - i * h + overlap * (i -1) - 1

        e = len(input) - i * h  + overlap * (i -1) - 1
        train_start = input["period"].iloc[s]
        train_end = input["period"].iloc[e]
        test_start = input["period"].iloc[e + 1]
        test_end = input["period"].iloc[e + h]
        
        data = {"partition": partitions - i + 1,
                "train_start": [train_start], 
                "train_end" : [train_end],
                "test_start": [test_start], 
                "test_end" : [test_end],
                }
        if df is None:
            df = pd.DataFrame(data)
        else:
            temp = pd.DataFrame(data)
            df = df._append(temp)

    df = df.sort_values(by = ["partition"])
    df.reset_index(inplace = True, drop = True)
    return df
        
    
def backtesting(input, 
                partitions, 
                overlap, 
                h, 
                params,
                experiment_name,
                mlflow_path,
                tags,
                overwrite = False):
    
    class bkt:
        def __init__(output, params, score, leaderboard, meta):
            output.params = params
            output.score = score
            output.leaderboard = leaderboard
            output.meta = meta
    
    ex = eia_mlflow.check_experiment(experiment_name)
    
    if overwrite and ex.experiment_exists:
        id = ex.experiment_meta["experiment_id"]
        print("Deleting previous experiment: " + id)
        mlflow.delete_experiment(experiment_id = id)
            
        
        
    
    
    meta = eia_mlflow.start_experiminet(experiment_name = experiment_name,
                                        mlflow_path = mlflow_path,
                                        tags = tags)
    score = None
    leaderboard = None
    for i in params:

        if "train" not in i:
            i["train"] = None
            

        bkt_grid = create_partitions(input = input, 
                      partitions = partitions, 
                      overlap = overlap, 
                      h = h, 
                      train = i["train"])

        score_temp = bkt_score(bkt_grid = bkt_grid, params = i, input = input, meta = meta)

        if score is None:
            score = score_temp.score
            leaderboard = score_temp.summary
        else:
            score = score._append(score_temp.score)
            leaderboard = leaderboard._append(score_temp.summary)
    
    score.reset_index(inplace = True, drop = True) 
    leaderboard.reset_index(inplace = True, drop = True) 

    output = bkt(params = params, 
                 score = score, 
                 leaderboard = leaderboard,
                 meta = meta)
   
    return output



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

        if params["model"] == "LinearRegressionModel" or  params["model"] == "XGBModel":
            f = fc.train_ml(input =  ts_train, 
                            model = params["model"],
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

def plot_score(score, type = "box"):
    
    if type == "box":
        p = px.box(score, x="model_label", y="mape", points="all", color = "model_label")
    elif type == "line":
        p = px.line(score, x="partition", y="mape", color="model_label", markers=True)
    elif type == "both":
        p1 = px.box(score, x="model_label", y="mape", points="all")
        p2 = px.line(score, x="partition", y="mape", color="model_label", markers=True)
        
    return p
    
    