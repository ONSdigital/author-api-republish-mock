# author-api-republish-mock

Small API mock to support the process of creating the CIMS Management UI. This mocks the 
real Author republish functionality. This repository should be used in conjunction with 
running instances of the CIMS Management UI and the CIR FastAPI app.


## Prerequisites

- CIR FastAPI app running locally/in Docker
- CIMS Management UI running locally/in Docker
- Ensure you have Docker installed
- Ensure you have Python & Poetry installed
- Run the command to install dependencies:

```shell
poetry install
```

## To Run Locally:

- Run using `main.py`
- Ensure you set the `CIR_HOST` environment variable in the run configuration


## To Run in Docker:

- Run the following commands:

```shell
docker compose build
docker compose up
```

