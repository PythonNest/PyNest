# Provider

Providers play a crucial role in PyNest. In PyNest, numerous core classes can function as providers, including services,
repositories, factories, helpers, and more. The central principle of a provider lies in its ability to be injected as a
dependency. This enables objects to form diverse interconnections, allowing the task of integrating these objects to be
primarily managed by the PyNest runtime environment.

::: nest.core.decorators.injectable