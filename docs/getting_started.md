# Getting Started

This guide will help you get started with setting up a new PyNest project, creating the essential modules, and running your application.

## Installation

To install PyNest, ensure you have Python 3.10+ installed. Then, install PyNest using your preferred package manager:

=== "pip"
    ```bash
    pip install pynest-api
    ```

=== "Poetry"
    ```bash
    poetry add pynest-api
    ```

## Creating a New Project 📂

Start by creating a new directory for your project and navigating into it:

```bash
mkdir my_pynest_project
cd my_pynest_project
```

You can simply use the pynest-cli to create the project structure:

=== "pip"
    ```bash
    pynest generate application -n .
    ```

=== "Poetry"
    ```bash
    poetry run pynest generate application -n .
    ```

Or you can create the file structure manually.

## Creating the Application Structure 🏗️

We'll create the basic structure of a PyNest application. Here's what it will look like:

```text
my_pynest_project/
├── src/
│   ├── __init__.py
│   ├── app_module.py
│   ├── app_controller.py
│   ├── app_service.py
├── main.py
├── requirements.txt
└── README.md
```

### Step 1: Create app_module.py

The app_module.py file is where we define our main application module. Create the file and add the following code:

```python
# src/app_module.py

from nest.core import Module
from nest.web import PyNestWebFactory
from .app_controller import AppController
from .app_service import AppService

@Module(
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass

app = PyNestWebFactory.create(
    AppModule,
    description="This is my PyNest app",
    title="My App",
    version="1.0.0",
    # here you can add more of the fastapi kwargs as describe here -         
    # https://fastapi.tiangolo.com/reference/fastapi/#fastapi.FastAPI
)

http_server = app.get_server()
```

### Step 2: Create app_service.py

The app_service.py file will contain the logic for our service. Create the file and add the following code:

```python
# src/app_service.py

from nest.core import Injectable

@Injectable
class AppService:
    def __init__(self):
        self.app_name = "MyApp"
        self.app_version = "1.0.0"

    def get_app_info(self):
        return {"app_name": self.app_name, "app_version": self.app_version}
```

### Step 3: Create app_controller.py

The app_controller.py file will handle the routing and responses. Create the file and add the following code:

```python
# src/app_controller.py

from nest.web import Controller, Get
from .app_service import AppService

@Controller("/")
class AppController:
    def __init__(self, service: AppService):
        self.service = service

    @Get("/")
    def get_app_info(self):
        return self.service.get_app_info()
```

### Step 4: Create main.py

The main.py file will run our PyNest application. Create the file and add the following code:

```python
# main.py

import uvicorn

if __name__ == "__main__":
    uvicorn.run("src.app_module:http_server", host="0.0.0.0", port=8000, reload=True)
```

### File Structure 🗂️

Here's the file structure of your PyNest application after following the steps:

```text
my_pynest_project/
├── src/
│   ├── __init__.py
│   ├── app_module.py
│   ├── app_controller.py
│   ├── app_service.py
├── main.py
├── requirements.txt
└── README.md
```

### Running the Application ▶️

To run your application, execute the following command:

```bash
python main.py
```

You should see the Uvicorn server starting, and you can access your API at <http://localhost:8000>.

---
<nav class="md-footer-nav">
  <a href="/PyNest/introduction" class="md-footer-nav__link">
    <span>&larr; Introduction</span>
  </a>
  <a href="/PyNest/cli" class="md-footer-nav__link">
    <span>CLI Usage &rarr;</span>
  </a>
</nav>