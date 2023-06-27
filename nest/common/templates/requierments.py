from nest import __version__ as version


def generate_requirements():
    template = f"""anyio==3.6.2
click==8.1.3
fastapi==0.95.1
fastapi-utils==0.2.1
greenlet==2.0.2
h11==0.14.0
idna==3.4
pydantic==1.10.7
python-dotenv==1.0.0
sniffio==1.3.0
SQLAlchemy==1.4.48
starlette==0.26.1
typing_extensions==4.5.0
uvicorn==0.22.0
pynest-api=={version}
    """
    return template
