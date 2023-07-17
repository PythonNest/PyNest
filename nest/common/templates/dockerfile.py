def generate_dockerfile() -> str:
    template = f"""FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
"""
    return template