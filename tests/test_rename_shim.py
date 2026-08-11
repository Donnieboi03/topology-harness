"""Shim package still imports after the topology-harness rename."""
from __future__ import annotations

import warnings


def test_deprecated_shim_imports_sticky():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from agent_topo_harness.sticky import StickyRegistry

        reg = StickyRegistry(host_session_id="shim")
        assert reg is not None
        assert any(issubclass(x.category, DeprecationWarning) for x in w)


def test_new_package_name():
    import topology_harness

    assert topology_harness.__version__ == "0.4.0"
    from topology_harness import StickyRegistry, TaskLedger

    assert StickyRegistry is not None
    assert TaskLedger is not None
