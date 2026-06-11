"""
PyNest testing utilities.

Build real DI containers for tests without booting an HTTP server, override
providers and guards with mocks, and drive in-process HTTP requests —
inspired by @nestjs/testing and Suites.
"""

from nest.testing.test_bed import (
    MockChain,
    TestBed,
    TestBedBuilder,
    UnitRef,
    UnitTestBed,
)
from nest.testing.testing_module import (
    GuardOverrideBy,
    OverrideBy,
    PyNestTestingModule,
    Test,
    TestingModule,
    TestingModuleBuilder,
    create_auto_mock,
)

__all__ = [
    "PyNestTestingModule",
    "Test",
    "TestingModule",
    "TestingModuleBuilder",
    "OverrideBy",
    "GuardOverrideBy",
    "create_auto_mock",
    "TestBed",
    "TestBedBuilder",
    "MockChain",
    "UnitRef",
    "UnitTestBed",
]
