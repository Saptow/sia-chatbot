# SIA Chatbot Code
This repository contains the openwebui-powered Chatbot codebase for POC. It also contains the backend code to deploy the chatbot in the form of an API endpoint. (under backend).

## Dependency Management
Currently, I am using uv to handle the dependencies for both the backend and the chatbot codebase. To install the dependencies, run the following command:

```bash
uv sync
```

This will install all the required packages listed in the `uv.lock` file.

## Running the Backend
The backend code is located within the `backend` directory and is mainly powered by FastAPI. 
To run the backend server, run the following command from the root directory:

```bash
uvicorn backend.main:app --reload --port 9000
```
This will start the FastAPI server on port 9000 with hot-reloading enabled. Swagger UI documentation will be available at `http://localhost:9000/docs`.

## Serving the POC Chatbot
To serve the POC chatbot through OpenWebUI, run the following command from the root directory:

```bash
docker compose up --build
```

This will build and start the Docker containers defined in the `docker-compose.yml` file, which includes the OpenWebUI server hosting the chatbot.

