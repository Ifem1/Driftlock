from datetime import datetime, timezone
import os
import tempfile
import sys
from pathlib import Path
from typing import Any, Callable
import pytest

# gltest 0.29.2 opens calldata through fd 0. On Windows an open tempfile cannot
# be immediately removed, so defer cleanup without changing contract behaviour.
try:
    import gltest.direct.loader as _loader

    def _windows_safe_inject_message_to_fd0(vm):
        from genlayer.py import calldata
        from genlayer.py.types import Address
        sender_addr = vm.sender if not isinstance(vm.sender, bytes) else Address(vm.sender)
        contract_addr = vm._contract_address if not isinstance(vm._contract_address, bytes) else Address(vm._contract_address)
        origin_addr = vm.origin if not isinstance(vm.origin, bytes) else Address(vm.origin)
        encoded = calldata.encode({
            "contract_address": contract_addr, "sender_address": sender_addr, "origin_address": origin_addr,
            "stack": [], "value": vm._value, "datetime": vm._datetime, "is_init": False,
            "chain_id": vm._chain_id, "entry_kind": 0, "entry_data": b"", "entry_stage_data": None,
        })
        fd, path = tempfile.mkstemp()
        os.write(fd, encoded); os.lseek(fd, 0, os.SEEK_SET)
        vm._original_stdin_fd = os.dup(0); os.dup2(fd, 0); os.close(fd)
        paths = getattr(vm, "_driftlock_calldata_paths", []); paths.append(path); vm._driftlock_calldata_paths = paths

    _loader._inject_message_to_fd0 = _windows_safe_inject_message_to_fd0
except ImportError:
    pass

from gltest.direct.loader import deploy_contract

@pytest.fixture
def direct_deploy(direct_vm) -> Callable[..., Any]:
    def _deploy(contract_path: str, *args: Any, **kwargs: Any) -> Any:
        path = Path(contract_path)
        if not path.is_absolute(): path = (Path.cwd() / path).resolve()
        return deploy_contract(path, direct_vm, *args, sdk_version="v0.2.12", **kwargs)
    return _deploy

NOW = 2_000_000_000
STAKE = 10 ** 15
BOND = 10 ** 14


def addr(value):
    raw = value.as_bytes if hasattr(value, "as_bytes") else value
    return "0x" + raw.hex() if isinstance(raw, bytes) else str(value)


def warp(vm, unix=NOW):
    value = datetime.fromtimestamp(unix, timezone.utc).isoformat()
    vm.warp(value)
    for name in ("_contract_drift_registry", "_contract_source_inspector", "_contract_breach_judge"):
        module = sys.modules.get(name)
        if module: module.gl.message_raw["datetime"] = value


def capture(vm):
    transfers, messages = [], []
    def hook(_vm, request):
        if "EthSend" in request:
            transfers.append(request["EthSend"]); return {"ok": None}
        if "PostMessage" in request:
            messages.append(request["PostMessage"]); return {"ok": None}
        return None
    vm._gl_call_hook = hook
    return transfers, messages
