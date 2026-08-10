# Durable memory (optional)

Not a topology. When Main sets `persist: durable` (host alias `vault`):

1. **TO is the sole agent writer.**
2. Main never writes.
3. TTs are read-only (if allowlisted).
4. Prefer retrieve → reconcile in the brief → selective upsert.
5. Human corrects the store offline when needed.

Gate: `assert_can_write("orchestrator")` (`topic_owner` alias accepted).

Telemetry: `durable_writer` — always TO when writes occur.

## Host mapping

The host maps `persist: durable` to its backend (files, DB, vault). See also
[vault-write-policy.md](vault-write-policy.md).

**Virgil:** Topic work that should compound in Obsidian should open with
`persist: vault` (doctrine + nest patch default for TO when omitted).
Throwaway Main→leaf paths stay `persist: none`.
