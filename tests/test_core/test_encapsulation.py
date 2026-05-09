"""Tests for NestJS-style module encapsulation enforcement."""
import pytest

from nest.common.exceptions import ProviderNotExportedException
from nest.core.decorators.injectable import Injectable
from nest.core.decorators.module import Module
from nest.core.pynest_container import PyNestContainer


# ── Legal scenarios (should build cleanly) ──────────────────────────────────


def test_same_module_dependency_is_legal():
    @Injectable
    class Repo:
        pass

    @Injectable
    class Service:
        def __init__(self, repo: Repo):
            self.repo = repo

    @Module(providers=[Repo, Service])
    class M:
        pass

    container = PyNestContainer()
    container.add_module(M)
    container.build()  # no raise


def test_imported_and_exported_dependency_is_legal():
    @Injectable
    class Repo:
        pass

    @Injectable
    class Service:
        def __init__(self, repo: Repo):
            self.repo = repo

    @Module(providers=[Repo], exports=[Repo])
    class RepoMod:
        pass

    @Module(providers=[Service], imports=[RepoMod])
    class ServiceMod:
        pass

    container = PyNestContainer()
    container.add_module(ServiceMod)
    container.build()  # no raise


def test_global_module_provider_is_visible_everywhere():
    @Injectable
    class Logger:
        pass

    @Injectable
    class Service:
        def __init__(self, logger: Logger):
            self.logger = logger

    # is_global=True → Logger visible to every module without explicit import
    @Module(providers=[Logger], is_global=True)
    class LoggingMod:
        pass

    @Module(providers=[Service])
    class ServiceMod:
        pass

    @Module(imports=[LoggingMod, ServiceMod])
    class AppMod:
        pass

    container = PyNestContainer()
    container.add_module(AppMod)
    container.build()  # no raise


def test_re_exported_module_chains_through():
    @Injectable
    class Repo:
        pass

    @Injectable
    class Service:
        def __init__(self, repo: Repo):
            self.repo = repo

    @Module(providers=[Repo], exports=[Repo])
    class RepoMod:
        pass

    # CoreMod imports RepoMod and re-exports the whole module
    @Module(imports=[RepoMod], exports=[RepoMod])
    class CoreMod:
        pass

    # ServiceMod only imports CoreMod, not RepoMod — must still see Repo
    @Module(providers=[Service], imports=[CoreMod])
    class ServiceMod:
        pass

    container = PyNestContainer()
    container.add_module(ServiceMod)
    container.build()  # no raise


# ── Illegal scenarios (should raise) ────────────────────────────────────────


def test_missing_import_raises():
    @Injectable
    class Repo:
        pass

    @Injectable
    class Service:
        def __init__(self, repo: Repo):
            self.repo = repo

    @Module(providers=[Repo], exports=[Repo])
    class RepoMod:
        pass

    # ServiceMod uses Repo but does NOT import RepoMod
    @Module(providers=[Service])
    class ServiceMod:
        pass

    @Module(imports=[ServiceMod, RepoMod])
    class AppMod:
        pass

    container = PyNestContainer()
    container.add_module(AppMod)
    with pytest.raises(ProviderNotExportedException) as exc:
        container.build()
    assert "Service" in str(exc.value)
    assert "Repo" in str(exc.value)
    assert "RepoMod" in str(exc.value)


def test_imported_but_not_exported_raises():
    @Injectable
    class Repo:
        pass

    @Injectable
    class Service:
        def __init__(self, repo: Repo):
            self.repo = repo

    # RepoMod imports Repo as provider but does NOT export it
    @Module(providers=[Repo])
    class RepoMod:
        pass

    @Module(providers=[Service], imports=[RepoMod])
    class ServiceMod:
        pass

    container = PyNestContainer()
    container.add_module(ServiceMod)
    with pytest.raises(ProviderNotExportedException) as exc:
        container.build()
    msg = str(exc.value)
    assert "exports=[Repo]" in msg  # actionable suggestion in the error


def test_controller_cross_module_violation_raises():
    @Injectable
    class Repo:
        pass

    from nest.core.decorators.controller import Controller

    @Controller("/x")
    class Ctrl:
        def __init__(self, repo: Repo):
            self.repo = repo

    @Module(providers=[Repo])  # not exported
    class RepoMod:
        pass

    @Module(controllers=[Ctrl], imports=[RepoMod])
    class WebMod:
        pass

    container = PyNestContainer()
    container.add_module(WebMod)
    with pytest.raises(ProviderNotExportedException):
        container.build()


def test_unrelated_modules_do_not_share_providers():
    @Injectable
    class Repo:
        pass

    @Injectable
    class Service:
        def __init__(self, repo: Repo):
            self.repo = repo

    # Two siblings with no import relation between them
    @Module(providers=[Repo])
    class RepoMod:
        pass

    @Module(providers=[Service])
    class ServiceMod:
        pass

    @Module(imports=[RepoMod, ServiceMod])
    class AppMod:
        pass

    container = PyNestContainer()
    container.add_module(AppMod)
    with pytest.raises(ProviderNotExportedException):
        container.build()
