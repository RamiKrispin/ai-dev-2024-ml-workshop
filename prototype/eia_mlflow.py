import mlflow

def start_experiminet(experiment_name, mlflow_path, tags):
    meta = None
    try:
        mlflow.create_experiment(name = experiment_name,
                             artifact_location= mlflow_path,
                             tags = tags)
        meta = mlflow.get_experiment_by_name(experiment_name)
        print(f"Set a new experiment {experiment_name}")
        print("Pulling the metadata")
    except:
        print(f"Experiment {experiment_name} exists, pulling the metadata")
        meta = mlflow.get_experiment_by_name(experiment_name)

    return meta


def set_params(h, freq, num_samples, lags, likelihood, quantiles, pi):
    
    class params:
        def __init__(output, params):
            output.params = params
    
    p = {
    "h": h,
    "freq": freq,
    "num_samples": num_samples,
    "lags": lags,
    "likelihood": likelihood,
    "quantiles": quantiles,
    "pi": pi
    }


    mlflow.log_params(p)

    output = params(params = p)
    return output


def log_run(run_name, experiment_id, params, tags = None):
    
    with mlflow.start_run(run_name = run_name,
        experiment_id= experiment_id, tags = tags) as run:
        set_params(h = params["h"], 
            freq = params["freq"], 
            num_samples = params["num_samples"], 
            lags = params["lags"],
            likelihood= params["likelihood"],
            quantiles = params["quantiles"],
            pi = params["pi"])
    
    return run


def check_experiment(experiment_name, verbose = True):
    class experiment_check:
        def __init__(output, experiment_name, experiment_meta, experiment_exists):
            output.experiment_name = experiment_name
            output.experiment_meta = experiment_meta
            output.experiment_exists = experiment_exists
            
    ex = mlflow.get_experiment_by_name(experiment_name)
    exists_flag = None
    if ex is None:
        if(verbose):
            print("Experiment " + experiment_name + " does not exist")
        exists_flag = False
        ex_meta = None
    else:

        if(verbose):
            print("Experiment " + experiment_name +  " exists")
        exists_flag = True
        ex_meta = dict(ex)

    output = experiment_check(experiment_name = experiment_name, 
                              experiment_meta = ex_meta,
                              experiment_exists = exists_flag)
    return output 