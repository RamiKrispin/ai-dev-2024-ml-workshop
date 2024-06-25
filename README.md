# Deploy and Monitor ML Pipelines with Open Source and Free Applications

WIP...pre-spell check

Materials for the **Deploy and Monitor ML Pipelines with Open Source and Free Applications** workshop at the [AI_dev 2024](https://events.linuxfoundation.org/ai-dev-europe/) conference in Paris, France.

When 📆: Wednesday, June 19th, 13:50 CEST

The workshop is based on the LinkedIn Learning course - [Data Pipeline Automation with GitHub Actions](https://www.linkedin.com/learning/data-pipeline-automation-with-github-actions-using-r-and-python/), code is available [here](https://github.com/LinkedInLearning/data-pipeline-automation-with-github-actions-4503382).

The workshop will focus on different deployment designs of machine learning pipelines using open-source applications and free-tier tools. We will use the US hourly demand for electricity data from the EIA API to demonstrate the deployment of a pipeline with GitHub Actions and Docker that fully automates the data refresh process and generates a forecast on a regular basis. This includes the use of open-source tools such as MLflow and YData Profiling to monitor the health of the data and the model's success. Last but not least, we will use Quarto doc to set up the monitoring dashboard and deploy it on GitHub Pages.




<figure>
 <img src="images/paris.png" width="100%" align="center"/></a>
<figcaption> The Seine River, Paris (created with Midjourney)</figcaption>
</figure>

<br>
<br />

## Table of Content

* [Milestones](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#milestones)
* [Scope](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#scope)
* [Set a Development Environment](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#set-a-development-environment)
* [Data Pipeline](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#data-pipeline)
* [Forecasting Models](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#forecasting-models)
* [Metadata](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#metadata)
* [Dashboard](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#dashboard)
* [Deployment](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#deployment)
* [Resources](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#license)
* [License](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop?tab=readme-ov-file#resources)


## Milestones
To organize and track the project requirements, we will set up a GitHub Project, create general milestones, and use issues to define sub-milestone. For setting up a data/ML pipeline, we will define the following milestones:
- Define scope and requirements:
    - Pipeline scope
    - Forecasting scope
- General tools and requirements 
    - Set a development environment:
    - Set a Docker image
    - Update the Dev Containers settings
- Data pipeline prototype:
    - Create pipeline schema/draft
    - Build a prototype
    - Test deployment on GitHub Actions
- Set forecasting models:
    - Create MLflow experiment
    - Set backtesting function
    - Define forecasting models
    - Test and evaluate the models' performance
    - Select the best model for deployment
- Set a Quarto dashboard:
    - Create a Quarto dashboard
    - Track the data and forecast
    - Monitor performance 
- Productionize the pipeline:
    - Clean the code
    - Define unit tests
- Deploy the pipeline and dashboard to GitHub Actions and GitHub Pages:
    - Create a GitHub Actions workflow
    - Refresh the data and forecast
    - Update the dashboard 


The milestones are available in the repository [issues section](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop/milestones), and you can track them on the [project tracker](https://github.com/users/RamiKrispin/projects/6/views/1).

<figure>
 <img src="images/github-project.png" width="100%" align="center"/></a>
<figcaption> The project tracker</figcaption>
</figure>

<br>
<br />

## Scope

**Goal:** Forecast the hourly demand for electricity in the California Independent System Operator subregion (CISO). 

This includes the following four providers:
- Pacific Gas and Electric (PGAE)
- Southern California Edison (SCE)
- San Diego Gas and Electric (SDGE)
- Valley Electric Association (VEA)

**Forecast Horizon:** 24 hours
**Refresh:** Every 24 hours

### Data 
The data is available on the [EIA API](https://www.eia.gov/opendata/), the API [dashboard provides](https://www.eia.gov/opendata/browser/electricity/rto/region-sub-ba-data?frequency=hourly&data=value;&facets=parent;&parent=CISO;&sortColumn=period;&sortDirection=desc;) the GET setting to pull the above series.

 
<figure>
 <img src="images/get-request.png" width="100%" align="center"/></a>
<figcaption> The GET request details from the EIA API dashboard</figcaption>
</figure>

<br>
<br />

### General Requirements
- The following functions:
    - Data backfill function
    - Data refresh function
    - Forecast function
    - Metadata function
- Docker image
- EIA API key

## Set a Development Environment

To make the deployment to GitHub Actions seamless, we will use Docker. In addition, we will set a development environment using VScode and the Dev Containers extension.

### Docker Settings

To make the deployment to GitHub Actions seamless, we will use Docker. This will enable us to ship our code to GitHub Actions using the same environment we used to develop and test our code. We will use the below `Dockerfile` to set the environment:

``` Dockerfile
FROM python:3.10-slim AS builder

ARG QUARTO_VER="1.5.45"
ARG VENV_NAME="ai_dev_workshop"
ENV QUARTO_VER=$QUARTO_VER
ENV VENV_NAME=$VENV_NAME
RUN mkdir requirements

COPY install_requirements.sh requirements/


COPY requirements.txt requirements/
RUN bash ./requirements/install_requirements.sh $VENV_NAME


FROM python:3.10-slim

ARG QUARTO_VER="1.5.45"
ARG VENV_NAME="ai_dev_workshop"
ENV QUARTO_VER=$QUARTO_VER
ENV VENV_NAME=$VENV_NAME

COPY --from=builder /opt/$VENV_NAME /opt/$VENV_NAME

COPY install_requirements.sh install_quarto.sh install_dependencies.sh requirements/
RUN bash ./requirements/install_dependencies.sh
RUN bash ./requirements/install_quarto.sh $QUARTO_VER

RUN echo "source /opt/$VENV_NAME/bin/activate" >> ~/.bashrc
```

We will use the [Python slim image](https://hub.docker.com/layers/library/python/3.10-slim/images/sha256-a31c40a8a991eeb3f3923b9c4efc94e269589b1f35b6987a587550a6cc182245?context=explore) as our baseline, along with a Multi-Stage build approach, to make the image size as minimal as possible.

More about Multi-Stage is available 

To make the image size as minimal as possible, we will use the [Python slim image](https://hub.docker.com/layers/library/python/3.10-slim/images/sha256-a31c40a8a991eeb3f3923b9c4efc94e269589b1f35b6987a587550a6cc182245?context=explore) as our baseline along with a Multi-Stage build approach. 

More details about the Multi-Stage build are available in the Docker [documentation](https://docs.docker.com/build/building/multi-stage/) and this [tutorial](https://medium.com/p/41b94ebe8bb3).

We will use the below Bash script (`build_image.sh`) to build and push the image to the Docker Hub:

``` bash
#!/bin/bash

echo "Build the docker"

# Identify the CPU type (M1 vs Intel)
if [[ $(uname -m) ==  "aarch64" ]] ; then
  CPU="arm64"
elif [[ $(uname -m) ==  "arm64" ]] ; then
  CPU="arm64"
else
  CPU="amd64"
fi


label="ai-dev"
tag="$CPU.0.0.1"
image="rkrispin/$label:$tag"

docker build . -f Dockerfile \
               --progress=plain \
               --build-arg QUARTO_VER="1.5.45" \
               --build-arg VENV_NAME="ai_dev_workshop" \
               -t $image

if [[ $? = 0 ]] ; then
echo "Pushing docker..."
docker push $image
else
echo "Docker build failed"
fi
```

The Dockerfile and its supporting files are under the [docker folder](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop/tree/main/docker).

**Note:** GitHub Actions, by default, does not support ARM64 processer but AMD64 (e.g., Intel). Therefore, if you are using Apple Silicon (M1/M2/M3) or any other ARM64-based machine, you will have to use [Docker BuildX](https://docs.docker.com/reference/cli/docker/buildx/) or similar to build the image to AMD64 architecture.   

### VScode Dev Containers Setting

We will use the following `devcontainer.json` file to set the development environment:

``` json
{
    "name": "AI-Dev Workshop",
    "image": "docker.io/rkrispin/ai-dev:amd64.0.0.1",
    "customizations": {
        "settings": {
            "python.defaultInterpreterPath": "/opt/ai_dev_workshop/bin/python3",
            "python.selectInterpreter": "/opt/ai_dev_workshop/bin/python3"
        },
        "vscode": {
            "extensions": [
                // Documentation Extensions
                "quarto.quarto",
                "purocean.drawio-preview",
                "redhat.vscode-yaml",
                "yzhang.markdown-all-in-one",
                // Docker Supporting Extensions
                "ms-azuretools.vscode-docker",
                "ms-vscode-remote.remote-containers",
                // Python Extensions
                "ms-python.python",
                "ms-toolsai.jupyter",
                // Github Actions
                "github.vscode-github-actions"
            ]
        }
    },
    "remoteEnv": {
        "EIA_API_KEY": "${localEnv:EIA_API_KEY}"
    }
}

```

If you want to learn more about setting up a dockerized development environment with the Dev Containers extension, please check the [Python](https://github.com/RamiKrispin/vscode-python) and [R](https://github.com/RamiKrispin/vscode-python) tutorials.


## Pipeline Design

Once we have a clear scope, we can start designing the pipeline. The pipeline has the following two main components:
- Data refresh
- Forecasting model

I typically start with drafting the process using paper and pencil (or the electronic version using iPad and Apple Pencil 😎). This helps me to understand better what functions I need to build:

<figure>
 <img src="images/pipeline-draft.jpg" width="100%" align="center"/></a>
<figcaption> The data pipeline draft</figcaption>
</figure>

<br>
<br />

Drawing the pipeline components and sub-components helps us plan the required functions that we need to build.


Drawing the pipeline components and sub-components helps us plan the required functions that we need to build. Once the pipeline is ready, I usually create a  design blueprint to document the process:

<figure>
 <img src="images/pipeline-diagram.png" width="100%" align="center"/></a>
<figcaption> The pipeline final design</figcaption>
</figure>

<br>
<br />


The pipeline will have the following two components:
- Data refresh function to keep the data up-to-date
- Forecast refresh to keep the forecast up-to-date

In addition, we will use the following two functions locally to prepare the data and models:
- Backfill function to initiate (or reset) the data pipeline
- Backtesting function to train, test, and evaluate time series models

We will set the pipeline to render and deploy a dashboard on GitHub pages whenever we refresh the data or the forecast. 

We will use a [JSON file](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop/blob/main/settings/series.json) to define the pipeline settings. This will enable us to seamlessly modify or update the pipeline without changing the functions. For example, we will define the required series from the EIA API under the series section:

```JSON
"series": [
        {
            "parent_id": "CISO",
            "parent_name": "California Independent System Operator",
            "subba_id": "PGAE",
            "subba_name": "Pacific Gas and Electric"
        },
        {
            "parent_id": "CISO",
            "parent_name": "California Independent System Operator",
            "subba_id": "SCE",
            "subba_name": "Southern California Edison"
        },
        {
            "parent_id": "CISO",
            "parent_name": "California Independent System Operator",
            "subba_id": "SDGE",
            "subba_name": "San Diego Gas and Electric"
        },
        {
            "parent_id": "CISO",
            "parent_name": "California Independent System Operator",
            "subba_id": "VEA",
            "subba_name": "Valley Electric Association"
        }
    ]
```

Last but not least, we will create two `CSV` files to store the data and the metadata. 

### Data

To pull the data from the EIA API, we will use Python libraries such as `requests`, `datetime`, and `pandas` to send GET requests to the API and process the data.

All the supporting functions to call the API and process the data are under the [eia_api.py](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop/blob/main/functions/eia_api.py) and [eia_data.py](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop/blob/main/functions/eia_data.py) files.

### Forecasting Models

The second component of the pipeline is setting up the forecasting models, this includes:
- Create a backtesting framework to test and evaluate models performance
- Set an experiment with MLflow. This includes the following steps:
    - Define models
    - Define backtesting settings
    - Run the models and Log their performance
    - Log for each series the best model
- For the demonstration, we will use the following two models from the [Darts](https://unit8co.github.io/darts/) library:
    - [Linear Regresion](https://unit8co.github.io/darts/generated_api/darts.models.forecasting.linear_regression_model.html#darts.models.forecasting.linear_regression_model.LinearRegressionModel)
    - [XGBoost](https://unit8co.github.io/darts/generated_api/darts.models.forecasting.xgboost.html)


We will use different flavors of those models, create a "horse race" between them, and select the one that performs best.

**Note:** We will run the backtesting process locally to avoid unnecessary compute time.

We will run an experiment with MLflow using different flavors of those models and evaluate which one performs best for each series. We will use the settings.json file to store the model's settings and backtesting parameters:

``` JSON

"models": {
            "model1": {
                "model": "LinearRegressionModel",
                "model_label": "model1",
                "comments": "LM model with lags, training with 2 years of history",
                "num_samples": 100,
                "lags": [
                    -24,
                    -168,
                    -8760
                ],
                "likelihood": "quantile",
                "train": 17520
            },
            "model2": {
                "model": "LinearRegressionModel",
                "model_label": "model2",
                "comments": "LM model with lags, training with 3 years of history",
                "num_samples": 100,
                "lags": [
                    -24,
                    -168,
                    -8760
                ],
                "likelihood": "quantile",
                "train": 26280
            },
            "model3": {
                "model": "LinearRegressionModel",
                "model_label": "model3",
                "comments": "Model 2 with lag 1",
                "num_samples": 100,
                "lags": [
                    -1,
                    -24,
                    -168,
                    -8760
                ],
                "likelihood": "quantile",
                "train": 26280
            },
           .
           .
           .
            "model6": {
                "model": "XGBModel",
                "model_label": "model6",
                "comments": "XGBoost with lags",
                "num_samples": 100,
                "lags": [
                    -1,
                    -2,
                    -3,
                    -24,
                    -48,
                    -168,
                    -336,
                    -8760
                ],
                "likelihood": "quantile",
                "train": 17520
            },
            "model7": {
                "model": "XGBModel",
                "model_label": "model7",
                "comments": "XGBoost with lags",
                "num_samples": 100,
                "lags": [
                    -1,
                    -2,
                    -3,
                    -24,
                    -48,
                    -168
                ],
                "likelihood": "quantile",
                "train": 17520
            }
```



We will use MLflow to track the backtesting results and compare between the models:

<figure>
 <img src="images/mlflow.png" width="100%" align="center"/></a>
<figcaption> The pipeline final design</figcaption>
</figure>
<br>
<br />
By default, the backtesting process logged the best model for each series by the MAPE error matric. We will use this log for the model selection during the deployment.

## Metadata
Setting logs and metadata collection enables us to monitor the health of the pipeline and identify problems when they occur. Here are some of the metrics we will collect:

- **Data refresh log:** Track the data refresh process and log critical metrics such as the time of the refresh, the time range of the data points, unit test results, etc.


<figure>
 <img src="images/data-log.png" width="100%" align="center"/></a>
<figcaption> The data pipeline log</figcaption>
</figure>
<br>
<br />

- **Forecasting models:** Define the selected model per series based on the backtesting evaluation results

<figure>
 <img src="images/models-log.png" width="100%" align="center"/></a>
<figcaption> The selected forecasting models</figcaption>
</figure>

<br>
<br />

- **Forecast refresh log:** Track the forecasting models refresh. This includes the time of refresh, forecast label and performance metrics
<figure>
 <img src="images/forecast-log.png" width="100%" align="center"/></a>
<figcaption> The forecasting models log</figcaption>
</figure>
<br>
<br />

## Dashboard

After we set the pipeline's data and forecast refresh functions, the last step is to set a dashboard that presents the outputs (e.g., data, forecast, metadata, etc.). For this task, we will use a [Quarto dashboard](https://quarto.org/docs/dashboards/) to set a simple dashboard that presents the most recent forecast and the pipeline metadata:

<figure>
 <img src="images/dashboard.png" width="100%" align="center"/></a>
<figcaption> The pipeline Quarto dashboard</figcaption>
</figure>
<br>
<br />

The dashboard is static, so we can deploy it on [GitHub Pages](https://pages.github.com/) as a static website. We will set the pipeline to rerender the dashboard and deploy it on GitHub Pages every time new data is available. The dashboard code and website are available [here](https://github.com/RamiKrispin/ai-dev-2024-ml-workshop/blob/main/functions/index.qmd) and [here](https://ramikrispin.github.io/ai-dev-2024-ml-workshop/), respectively.

## Deployment

The last step of this pipeline setting process is to deploy it to GitHub Actions. We will use the following workflow to deploy the pipeline:

`data_refresh.yml`
```yaml
name: Data Refresh  

on:
  schedule:
    - cron: "0 */1 * * *"
jobs:
  refresh-the-dashboard:
    runs-on: ubuntu-22.04
    container:
      image: docker.io/rkrispin/ai-dev:amd64.0.0.2
    steps:
      - name: checkout_repo
        uses: actions/checkout@v3
        with:
          ref: "main"
      - name: Data Refresh
        run: bash ./functions/data_refresh_py.sh
        env:
          EIA_API_KEY: ${{ secrets.EIA_API_KEY }}
          USER_EMAIL: ${{ secrets.USER_EMAIL }}
          USER_NAME: ${{ secrets.USER_NAME }}
```

This simple workflow is set to run every hour. It uses the project image - `docker.io/rkrispin/ai-dev:amd64.0.0.2` as the environment. We use the built-in action - `actions/checkout@v3`to check out the repo, access it, commit chnages and write it back to the repo.


Last but not least, we will execute the following bash script:

`data_refresh_py.sh`
``` bash
#!/usr/bin/env bash
source /opt/$VENV_NAME/bin/activate 

rm -rf ./functions/data_refresh_py_files
rm ./functions/data_refresh_py.html
quarto render ./functions/data_refresh_py.qmd --to html

rm -rf docs/data_refresh/
mkdir docs/data_refresh
cp ./functions/data_refresh_py.html ./docs/data_refresh/
cp -R ./functions/data_refresh_py_files ./docs/data_refresh/

echo "Finish"
p=$(pwd)
git config --global --add safe.directory $p


# Render the Quarto dashboard
if [[ "$(git status --porcelain)" != "" ]]; then
    quarto render functions/index.qmd
    cp functions/index.html docs/index.html
    rm -rf docs/index_files
    cp -R functions/index_files/ docs/
    rm functions/index.html
    rm -rf functions/index_files
    git config --global user.name $USER_NAME
    git config --global user.email $USER_EMAIL
    git add data/*
    git add docs/*
    git commit -m "Auto update of the data"
    git push origin main
else
echo "Nothing to commit..."
fi
```

This bash script render the quarto doc with the data and forecast refresh functions. It than check if new data points are available, and if so, it will render the dashboard and commit the chnages (e.g., append changes to the CSV files).

Note that you will need to set the following three secrets:
- `EIA_API_KEY` - the EIA API key
- `USER_EMAIL` - the email address that associated with the GitHub account
- `USER_NAME` - the GitHub account user name

## Resources

- Docker documentation: https://docs.docker.com/
- Dev Containers Extension: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
- GitHub Actions documentation: https://docs.github.com/en/actions

## License
This tutorial is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/) License.
