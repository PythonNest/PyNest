import asyncio
import signal

from fastapi.testclient import TestClient

from nest.common.interfaces import (
    BeforeApplicationShutdown,
    OnApplicationBootstrap,
    OnApplicationShutdown,
    OnModuleDestroy,
    OnModuleInit,
)
from nest.core import Injectable, Module, PyNestFactory


def test_factory_runs_boot_hooks_in_import_order_before_bootstrap():
    events = []

    @Injectable
    class LeafService(OnModuleInit):
        def on_module_init(self):
            events.append("leaf-service:module-init")

    @Module(providers=[LeafService])
    class LeafModule:
        pass

    @Injectable
    class RootService(OnModuleInit, OnApplicationBootstrap):
        async def on_module_init(self):
            await asyncio.sleep(0)
            events.append("root-service:module-init")

        async def on_application_bootstrap(self):
            await asyncio.sleep(0)
            events.append("root-service:bootstrap")

    @Module(imports=[LeafModule], providers=[RootService])
    class RootModule(OnModuleInit, OnApplicationBootstrap):
        def on_module_init(self):
            events.append("root-module:module-init")

        def on_application_bootstrap(self):
            events.append("root-module:bootstrap")

    PyNestFactory.create(RootModule)

    assert set(events) == {
        "leaf-service:module-init",
        "root-service:module-init",
        "root-module:module-init",
        "root-service:bootstrap",
        "root-module:bootstrap",
    }
    assert events.index("leaf-service:module-init") < events.index(
        "root-service:module-init"
    )
    assert events.index("leaf-service:module-init") < events.index(
        "root-module:module-init"
    )

    module_init_indices = [
        index for index, event in enumerate(events) if event.endswith(":module-init")
    ]
    bootstrap_indices = [
        index for index, event in enumerate(events) if event.endswith(":bootstrap")
    ]
    assert max(module_init_indices) < min(bootstrap_indices)


def test_app_close_runs_shutdown_hooks_in_phase_order_and_reverse_module_order():
    events = []

    @Injectable
    class LeafService(
        BeforeApplicationShutdown, OnModuleDestroy, OnApplicationShutdown
    ):
        async def before_application_shutdown(self, signal):
            await asyncio.sleep(0)
            events.append(f"leaf-service:before:{signal}")

        def on_module_destroy(self):
            events.append("leaf-service:destroy")

        def on_application_shutdown(self, signal):
            events.append(f"leaf-service:shutdown:{signal}")

    @Module(providers=[LeafService])
    class LeafModule:
        pass

    @Injectable
    class RootService(
        BeforeApplicationShutdown, OnModuleDestroy, OnApplicationShutdown
    ):
        def before_application_shutdown(self, signal):
            events.append(f"root-service:before:{signal}")

        async def on_module_destroy(self):
            await asyncio.sleep(0)
            events.append("root-service:destroy")

        def on_application_shutdown(self, signal):
            events.append(f"root-service:shutdown:{signal}")

    @Module(imports=[LeafModule], providers=[RootService])
    class RootModule(BeforeApplicationShutdown, OnModuleDestroy, OnApplicationShutdown):
        def before_application_shutdown(self, signal):
            events.append(f"root-module:before:{signal}")

        def on_module_destroy(self):
            events.append("root-module:destroy")

        async def on_application_shutdown(self, signal):
            await asyncio.sleep(0)
            events.append(f"root-module:shutdown:{signal}")

    app = PyNestFactory.create(RootModule)

    asyncio.run(app.close("SIGINT"))
    asyncio.run(app.close("SIGTERM"))

    assert set(events) == {
        "root-service:before:SIGINT",
        "root-module:before:SIGINT",
        "leaf-service:before:SIGINT",
        "root-service:destroy",
        "root-module:destroy",
        "leaf-service:destroy",
        "root-service:shutdown:SIGINT",
        "root-module:shutdown:SIGINT",
        "leaf-service:shutdown:SIGINT",
    }
    assert all("SIGTERM" not in event for event in events)

    before_indices = [
        index for index, event in enumerate(events) if ":before:" in event
    ]
    destroy_indices = [
        index for index, event in enumerate(events) if event.endswith(":destroy")
    ]
    shutdown_indices = [
        index for index, event in enumerate(events) if ":shutdown:" in event
    ]
    assert max(before_indices) < min(destroy_indices)
    assert max(destroy_indices) < min(shutdown_indices)

    for phase in ("before:SIGINT", "destroy", "shutdown:SIGINT"):
        leaf_event = f"leaf-service:{phase}"
        root_events = [
            f"root-service:{phase}",
            f"root-module:{phase}",
        ]
        assert all(
            events.index(root_event) < events.index(leaf_event)
            for root_event in root_events
        )


def test_fastapi_lifespan_closes_database_style_provider():
    events = []

    @Injectable
    class DatabaseService(OnModuleInit, OnModuleDestroy):
        def __init__(self):
            self.connected = False

        async def on_module_init(self):
            await asyncio.sleep(0)
            self.connected = True
            events.append("connect")

        async def on_module_destroy(self):
            await asyncio.sleep(0)
            self.connected = False
            events.append("disconnect")

    @Module(providers=[DatabaseService])
    class DatabaseModule:
        pass

    app = PyNestFactory.create(DatabaseModule)
    database = app.container.get(DatabaseService)

    assert database.connected is True
    assert events == ["connect"]

    with TestClient(app.get_server()):
        assert database.connected is True

    assert database.connected is False
    assert events == ["connect", "disconnect"]


def test_enable_shutdown_hooks_wires_sigint_and_sigterm_to_app_close(monkeypatch):
    events = []

    @Injectable
    class CleanupService(OnModuleDestroy):
        def on_module_destroy(self):
            events.append("closed")

    @Module(providers=[CleanupService])
    class CleanupModule:
        pass

    registered_handlers = {}

    def fake_signal(signal_number, handler):
        registered_handlers[signal_number] = handler

    monkeypatch.setattr(signal, "signal", fake_signal)

    app = PyNestFactory.create(CleanupModule)
    result = app.enable_shutdown_hooks()

    assert result is app
    assert set(registered_handlers) == {signal.SIGTERM, signal.SIGINT}

    sigterm_handler = registered_handlers[signal.SIGTERM]
    sigterm_handler(signal.SIGTERM, None)
    sigterm_handler(signal.SIGTERM, None)

    assert events == ["closed"]
