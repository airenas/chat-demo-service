[![Python](https://github.com/airenas/chat-demo-service/actions/workflows/python-app.yml/badge.svg)](https://github.com/airenas/chat-demo-service/actions/workflows/python-app.yml) [![docker](https://github.com/airenas/chat-demo-service/actions/workflows/docker.yml/badge.svg)](https://github.com/airenas/chat-demo-service/actions/workflows/docker.yml)

# chat-demo-service

Demo service for helping AI-chatbot communication with the backend.

## Running samples

### Prepare python env

#### init conda

```bash
conda create --name cds python=3.12
conda activate cds
```

#### requirements
```bash
pip install -r requirements.txt
```

### Run test

#### requirements
```bash
pip install -r requirements_test.txt
```

#### run
```bash
make test/unit
```
