from nest.common.interfaces import (
    BeforeApplicationShutdown,
    OnApplicationBootstrap,
    OnApplicationShutdown,
    OnModuleDestroy,
    OnModuleInit,
)


def test_lifecycle_interfaces_are_runtime_checkable():
    class HookedProvider:
        def on_module_init(self):
            pass

        def on_application_bootstrap(self):
            pass

        def before_application_shutdown(self, signal):
            pass

        def on_module_destroy(self):
            pass

        def on_application_shutdown(self, signal):
            pass

    provider = HookedProvider()

    assert isinstance(provider, OnModuleInit)
    assert isinstance(provider, OnApplicationBootstrap)
    assert isinstance(provider, BeforeApplicationShutdown)
    assert isinstance(provider, OnModuleDestroy)
    assert isinstance(provider, OnApplicationShutdown)
