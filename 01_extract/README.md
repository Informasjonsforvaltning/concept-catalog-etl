# 01_extract

Extracts concepts from concept-catalouge API (by GET /begreper) and writes to file.

## Requirements
- python3


./cloud_sql_proxy -instances=fdk-dev:europe-north1:fdk-sql-test=tcp:5432

## To work in a virtual environment

```
python3 -m venv .venv
source .venv/bin/activate
```

## Install and run locally

```
pip install --no-cache-dir -r requirements.txt
python3 01_extract.py
```
