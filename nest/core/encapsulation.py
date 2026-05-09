"""NestJS-style module encapsulation validation.

Enforces that a class can only inject providers visible to its owning module:
its own providers, providers exported by imported modules (transitively through
re-exports), and providers from globally-scoped modules.
"""
from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Dict, List, Set

from nest.common.exceptions import ProviderNotExportedException

if TYPE_CHECKING:
    from nest.core.pynest_container import ModuleRef


_PRIMITIVE_TYPES = {
    int, str, float, bool, bytes, bytearray, complex,
    list, dict, tuple, set, frozenset, type(None),
}


def validate_module_encapsulation(modules: Dict[str, "ModuleRef"]) -> None:
    """Validate that every cross-module dependency goes through proper imports/exports.

    Raises ProviderNotExportedException listing every violation with a suggested fix.
    """
    if not modules:
        return

    # Map every provider token (and controller class) to the module that owns it.
    provider_owner: Dict[Any, "ModuleRef"] = {}
    for mref in modules.values():
        for desc in mref.compiled.provider_descriptors:
            provider_owner[desc.provide] = mref
        for ctrl in mref.compiled.controllers:
            provider_owner[ctrl] = mref

    # Class → its ModuleRef (so we can look up imported modules by their metatype).
    metatype_to_ref: Dict[type, "ModuleRef"] = {
        mref.metatype: mref for mref in modules.values()
    }

    def resolved_exports(mref: "ModuleRef", _seen: Set[str] = None) -> Set[Any]:
        """Return the set of provider tokens that `mref` exposes to importers,
        following module re-exports recursively."""
        if _seen is None:
            _seen = set()
        if mref.token in _seen:
            return set()
        _seen = _seen | {mref.token}
        result: Set[Any] = set()
        for exp in mref.compiled.exports:
            # If the export is a Module class, re-export everything it exports.
            if isinstance(exp, type) and getattr(exp, "__is_module__", False):
                child = metatype_to_ref.get(exp)
                if child is not None:
                    result |= resolved_exports(child, _seen)
            else:
                result.add(exp)
        return result

    # Anything provided by an @Module(is_global=True) module is visible everywhere.
    global_providers: Set[Any] = set()
    for mref in modules.values():
        if getattr(mref.metatype, "__is_global__", False):
            for desc in mref.compiled.provider_descriptors:
                global_providers.add(desc.provide)

    # Per-module visibility set: own providers + imported exports + globals.
    visible: Dict[str, Set[Any]] = {}
    for mref in modules.values():
        s: Set[Any] = set()
        for desc in mref.compiled.provider_descriptors:
            s.add(desc.provide)
        for ctrl in mref.compiled.controllers:
            s.add(ctrl)
        for imp in mref.compiled.imports:
            child = metatype_to_ref.get(imp)
            if child is not None:
                s |= resolved_exports(child)
        s |= global_providers
        visible[mref.token] = s

    # Walk every consumer's __init__ signature and check each annotated dependency.
    errors: List[str] = []
    for mref in modules.values():
        consumers: List[type] = list(mref.compiled.controllers)
        for desc in mref.compiled.provider_descriptors:
            if desc.use_class is not None:
                consumers.append(desc.use_class)

        for consumer_cls in consumers:
            try:
                sig = inspect.signature(consumer_cls.__init__)
            except (ValueError, TypeError):
                continue

            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                ann = param.annotation
                if ann is inspect.Parameter.empty:
                    continue

                # Resolve string forward refs against known providers (best effort).
                if isinstance(ann, str):
                    matches = [
                        p for p in provider_owner
                        if isinstance(p, type) and p.__name__ == ann
                    ]
                    if len(matches) != 1:
                        continue
                    ann = matches[0]

                if ann in _PRIMITIVE_TYPES:
                    continue

                # Only check tokens that are actually registered somewhere — unknown
                # types are someone else's problem (FastAPI body params, externals, etc).
                if ann not in provider_owner:
                    continue

                if ann not in visible[mref.token]:
                    owner = provider_owner[ann]
                    errors.append(_format_violation(consumer_cls, mref, ann, owner))

    if errors:
        raise ProviderNotExportedException(
            "Module encapsulation violation(s) detected:\n\n"
            + "\n\n".join(errors)
        )


def _format_violation(consumer_cls: type, consumer_module, dep, owner_module) -> str:
    consumer_name = consumer_cls.__name__
    consumer_mod = consumer_module.metatype.__name__
    dep_name = getattr(dep, "__name__", str(dep))
    owner_mod = owner_module.metatype.__name__
    return (
        f"  ✗ {consumer_name} (in module {consumer_mod}) depends on {dep_name},\n"
        f"    but {dep_name} is provided by {owner_mod}.\n"
        f"\n"
        f"    To fix, do BOTH:\n"
        f"      1. add 'imports=[{owner_mod}]'   to {consumer_mod}\n"
        f"      2. add 'exports=[{dep_name}]'   to {owner_mod}\n"
        f"\n"
        f"    Or move {dep_name} into {consumer_mod} if it doesn't belong in {owner_mod}."
    )
