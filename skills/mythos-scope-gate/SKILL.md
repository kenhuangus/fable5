---
name: mythos-scope-gate
description: Use before any approved Mythos-style defensive cybersecurity run, or when reviewing a Fable/Mythos security workflow. Requires authorization, bounded targets, private evidence handling, independent validation, and a patch/report owner before the model explores vulnerabilities.
---

# Mythos Scope Gate

Mythos 5 is not "Fable 5 but with fewer annoying refusals." It is the gated
Project Glasswing deployment of the same underlying capability class without
Fable's relevant dual-use classifier layer. Treat that as a stronger duty to
scope the work, not as permission to run broader tasks.

## Gate before prompting

Do not start a Mythos-style cyber run until the request has a scope packet with:

- authorization id and Glasswing scope id;
- exact repositories, products, or components in scope;
- allowed actions, limited to inspect, reproduce, patch, verify, and report;
- explicitly disallowed actions, including public proof-of-concept release,
  credential access, external targeting, persistence, and exfiltration;
- private evidence store for vulnerability artifacts;
- isolated reproduction sandbox for any reproduction work;
- independent validator who did not produce the finding;
- human patch or disclosure owner.

If any item is missing, stop and ask for the packet. Do not compensate with a
more careful prompt.

## Fable mode is different

For `claude-fable-5`, the control surface includes refusal logging and fallback
handling. For `claude-mythos-5`, do not treat the absence of a refusal as a
safety signal. The safety signal is scope provenance: what was authorized,
what target was touched, what artifact was produced, who validated it, and who
owns the patch or disclosure.

## Output rule

Reports should be patch-first and scope-bound. Describe exploitability only to
the level required for validation and remediation, keep artifacts private, and
never publish operational proof-of-concept details from the agent run.

The companion repo includes a runnable validator:

```bash
python mythos_scope/scope_gate.py mythos_scope/sample_mythos_scope.json
```
