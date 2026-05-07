import pytest
from nest.common.module import ModuleCompiler, ModuleTokenFactory, CompiledModule
from nest.common.provider import ProviderDescriptor, Scope
from nest.core.decorators.module import Module
from nest.core.decorators.injectable import Injectable


@Injectable
class ServiceA:
    pass


@Injectable
class ServiceB:
    def __init__(self, a: ServiceA):
        self.a = a


@Module(providers=[ServiceA])
class ModuleA:
    pass


@Module(providers=[ServiceB], imports=[ModuleA], exports=[ServiceB])
class ModuleB:
    pass


@Module(providers=[{"provide": "DB_URL", "useValue": "postgres://localhost/test"}])
class ConfigModule:
    pass


def test_compiled_module_has_token():
    compiler = ModuleCompiler(ModuleTokenFactory())
    result = compiler.compile(ModuleA)
    assert isinstance(result, CompiledModule)
    assert result.token is not None
    assert len(result.token) > 0


def test_compiled_module_has_metatype():
    compiler = ModuleCompiler(ModuleTokenFactory())
    result = compiler.compile(ModuleA)
    assert result.metatype is ModuleA


def test_compiled_module_providers_are_normalized():
    compiler = ModuleCompiler(ModuleTokenFactory())
    result = compiler.compile(ModuleA)
    assert len(result.provider_descriptors) == 1
    desc = result.provider_descriptors[0]
    assert isinstance(desc, ProviderDescriptor)
    assert desc.use_class is ServiceA


def test_compiled_module_dict_provider_is_normalized():
    compiler = ModuleCompiler(ModuleTokenFactory())
    result = compiler.compile(ConfigModule)
    assert len(result.provider_descriptors) == 1
    desc = result.provider_descriptors[0]
    assert desc.use_value == "postgres://localhost/test"
    assert desc.use_class is None


def test_compiled_module_imports():
    compiler = ModuleCompiler(ModuleTokenFactory())
    result = compiler.compile(ModuleB)
    assert ModuleA in result.imports


def test_compiled_module_exports():
    compiler = ModuleCompiler(ModuleTokenFactory())
    result = compiler.compile(ModuleB)
    assert ServiceB in result.exports


def test_same_module_gets_same_token():
    factory = ModuleTokenFactory()
    compiler = ModuleCompiler(factory)
    token1 = compiler.compile(ModuleA).token
    token2 = compiler.compile(ModuleA).token
    assert token1 == token2


def test_different_modules_get_different_tokens():
    factory = ModuleTokenFactory()
    compiler = ModuleCompiler(factory)
    token_a = compiler.compile(ModuleA).token
    token_b = compiler.compile(ModuleB).token
    assert token_a != token_b


def test_module_without_decorator_raises():
    class Bare:
        pass

    compiler = ModuleCompiler(ModuleTokenFactory())
    with pytest.raises(Exception, match="no metadata"):
        compiler.compile(Bare)
