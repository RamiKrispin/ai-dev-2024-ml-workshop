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


## Data Pipeline

Once we have a clear scope, we can move to the design process step. I typically start with drafting the process using paper and pencil (or the electronic version using iPad and Apple Pencil 😎). This helps me to understand better what functions I need to build:

<figure>
 <img src="images/pipeline-draft.jpg" width="100%" align="center"/></a>
<figcaption> The data pipeline draft</figcaption>
</figure>

<br>
<br />

We can use the draft to derive the pipeline's components and required functions. For automating the data, we will build the following subprocess:
- **Backfill function -** to initiate or reset the pipeline. This function should run locally.
- **Refresh function -** manage the refresh process of the data once deployed on GitHub Actions

In addition, we will use a `JSON` file to define the pipeline settings. The settings file should include all the pipeline parameters we want to avoid hard coding. This will enable us to make changes in the pipeline seamlessly.

Last but not least, we will create two `CSV` files to store the data and the metadata. 

## Forecasting Models
## Metadata
## Dashboard
## Deployment
## Resources

- Docker documentation: https://docs.docker.com/
- Dev Containers Extension: https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers
- GitHub Actions documentation: https://docs.github.com/en/actions

## License
This tutorial is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/) License.
