# Hermes adapter — nest-orchestrator + apply helpers

This adapter plugs **Compound Topologies** into [Hermes](https://github.com/) via:

| Path | Role |
| :--- | :--- |
| `delegate_tool/` | Nest-orchestrator patch so Topic Owners can spawn leaves |
| `../scripts/apply_hermes_delegate_patch.sh` | Apply patch into Hermes site-packages |
| `../scripts/apply_agent_topo_harness.sh` | Prefill + hooks + models + `external_dirs` |

`delegate_task` remains a Hermes tool. This harness owns the **control-plane doctrine**; Hermes (or another host) owns spawn primitives.

```bash
cd ~/Developer/agent-topo-harness
./scripts/apply_hermes_delegate_patch.sh
VIRGIL_ROOT=/path/to/Virgil ./scripts/apply_agent_topo_harness.sh   # optional Virgil skills dir
```

See `delegate_tool/README.md` for patch behavior.
