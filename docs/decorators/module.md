## Module Decorator

The `Module` decorator is used to define a module. A module is a class that contains the controllers and services that
are used in the application. The module is used to register the controllers and services in the application.

Every application contains a minimum of one module, known as the root module. This module serves as the foundation for
PyNest to construct the application graph, a crucial internal framework that determines how modules and provider
relationships, as well as dependencies, are interlinked. Although it's possible for very small applications to consist
solely of the root module, this scenario is uncommon. It's important to highlight the significance of using modules to
systematically arrange your components. Therefore, in the majority of cases, the architectural design will incorporate
several modules, with each one encompassing a group of closely connected functionalities.

::: nest.core.decorators.module



