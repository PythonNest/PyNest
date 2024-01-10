<p align="center">
  <img src="docs/imgs/pynest-logo.png" title="pynest logo" width="300">
</p>
<p align="center">
    <em>PyNest is a Python framework built on top of FastAPI that follows the modular architecture of NestJS</em>
</p>
<p align="center">
    <a href="https://pypi.org/project/pynest-api">
        <img src="https://img.shields.io/pypi/v/pynest-api?color=%2334D058&label=pypi%20package" alt="Version">
    </a>
    <a href="https://pypi.org/project/pynest-api">
        <img src="https://img.shields.io/pypi/pyversions/pynest-api.svg?color=%2334D058" alt="Python">
    </a>
    <a href="https://pepy.tech/project/pynest-api">
        <img src="https://static.pepy.tech/personalized-badge/pynest-api?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads" alt="Downloads">
    </a>
    <a href="https://github.com/PythonNest/PyNest/blob/main/LICENSE">
        <img src="https://img.shields.io/github/license/PythonNest/Pynest" alt="License">
    </a>
</p>


# Description

PyNest is designed to help structure your APIs in an intuitive, easy to understand, and enjoyable way.

With PyNest, you can build scalable and maintainable APIs with ease. The framework supports dependency injection, type annotations, decorators, and code generation, making it easy to write clean and testable code.

This framework is not a direct port of NestJS to Python but rather a re-imagining of the framework specifically for Python developers, including backend engineers and ML engineers. It aims to assist them in building better and faster APIs for their data applications.

## Getting Started
To get started with PyNest, you'll need to install it using pip:

```bash
pip install pynest-api
```

### Start with cli
```bash
pynest create-nest-app -n my_app_name
```

this command will create a new project with the following structure:

```text
├── app.py
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
├── src
│    ├── __init__.py
```

once you have created your app, get into the folder and run the following command:

```bash
cd my_app_name
```

run the server with the following command:

```bash
uvicorn "app:app" --host "0.0.0.0" --port "8000" --reload
```

Now you can visit [OpenAPI](http://localhost:8000/docs) in your browser to see the default API documentation.

### Adding modules

To add a new module to your application, you can use the pynest generate module command:

```bash
pynest g module -n users
```

This will create a new module called ```users``` in your application with the following structure under the ```src``` folder:

```text
├── users
│    ├── __init__.py
│    ├── users_controller.py
│    ├── users_service.py
│    ├── users_model.py
│    ├── users_entity.py
│    ├── users_module.py
```

The users module will immediately register itself with the application and will be available for use.

You can then start defining routes and other application components using decorators and other PyNest constructs.

For more information on how to use PyNest, check out the official documentation at https://pythonnest.github.io/PyNest/.

## PyNest CLI Usage Guide

This document provides a guide on how to use the PyNest Command Line Interface (CLI). Below are the available commands and their descriptions:

### `pynest` Command

- **Description**: The main command group for PyNest CLI.

#### `create-nest-app` Subcommand

- **Description**: Create a new nest app.
- **Options**:
  - `--app-name`/`-n`: The name of the nest app (required).
  - `--db-type`/`-db`: The type of the database (optional). You can specify PostgreSQL, MySQL, SQLite, or MongoDB.
  - `--is-async`: Whether the project should be asynchronous (optional, default is False).

### `g` command group

- **Description**: Group command for generating boilerplate code.

#### `module` Subcommand

- **Description**: Generate a new module (controller, service, entity, model, module).
- **Options**:
  - `--name`/`-n`: The name of the module (required).


#### CLI Examples
* create a blank nest application - 
`pynest create-nest-app -n my_app_name`

* create a nest application with postgres database and async connection -
`pynest create-nest-app -n my_app_name -db postgresql --is-async`

* create new module - 
`pynest g module -n users`


## Key Features
### Modular Architecture

PyNest follows the modular architecture of NestJS, which allows for easy separation of concerns and code organization. Each module contains a collection of related controllers, services, and providers.

### Dependency Injection
PyNest supports dependency injection, which makes it easy to manage dependencies and write testable code. You can easily inject services and providers into your controllers using decorators.


### Decorators

PyNest makes extensive use of decorators to define routes, middleware, and other application components. This helps keep the code concise and easy to read.

### Type Annotations

PyNest leverages Python's type annotations to provide better tooling and help prevent errors. You can annotate your controllers, services, and providers with types to make your code more robust.

### Code Generation

PyNest includes a code generation tool that can create boilerplate code for modules, controllers, and other components. This saves you time and helps you focus on writing the code that matters.

## Future Plans

- [ ] Create plugins Marketplace for modules where developers can share their modules and download modules created by others.
- [ ] Implement IOC mechanism and introduce Module decorator
- [ ] Add support for new databases
- [ ] Create out-of-the-box authentication module that can be easily integrated into any application.
- [ ] Add support for other testing frameworks and create testing templates.
- [ ] Add support for other web frameworks (Flask, Django, etc.) - Same Architecture, different engine.


## Contributing

Contributions are welcome! Please feel free to grab one of the open issues,
or open a new one if you have an idea for a new feature or improvement.

This would bring a huge impact to the project and the community.

## License

PyNest is [MIT licensed](LICENSE).

## Credits

PyNest is inspired by [NestJS](https://nestjs.com/).
