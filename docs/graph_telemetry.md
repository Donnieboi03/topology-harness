# Graph telemetry

Suggested fields for host traces / cost attribution:

- **topology_urn**: `topology:<paradigm>:<workflow-slug>:<ulid>`
- **control_plane**: `main | orchestrator | tt`  
  (`topic_owner` / `leaf` accepted as aliases when ingesting)
- **composition** / **pattern_composition**: compound id or freeform
- **topic**: kebab slug
- **durable_writer**: always `orchestrator` when writes occur
- **sticky**: whether the worker resumed a prior session id

Helpers: `make_topology_urn`.
