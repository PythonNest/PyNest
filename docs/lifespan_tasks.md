# Lifaspan tasks in PyNest

## Introduction

Lifespan tasks - coroutines, which run while app is working. 

## Defining a lifespan task
As example of lifespan task will use coroutine, which print time every hour. In real user cases can be everything else.

```python
import asyncio
from datetime import datetime

async def print_current_time():
    while True:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"Current time: {current_time}")
        await asyncio.sleep(3600)
```

## Implement a lifespan task
In `app_module.py` we can define a startup handler, and run lifespan inside it

```python
from nest.core import PyNestFactory

app = PyNestFactory.create(
    AppModule,
    description="This is my FastAPI app with lifespan task",
    title="My App",
    version="1.0.0",
    debug=True,
)

http_server = app.get_server()

@http_server.on_event("startup")
async def startup():
    await print_current_time()
```

Now `print_current_time` will work in lifespan after startup.
