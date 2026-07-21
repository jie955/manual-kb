# TOPENS domain pack
#
# Holds product registry, index bindings, routing rules, and CS policies.
# Core engine must not import TOPENS constants from here by name — load via
# `domains.loader.load_domain("topens")`.
#
# Layout:
#   domain.yaml / products.yaml / indices.yaml / routing.yaml / policies.yaml
#   presales_playbooks.yaml — structured presales business rules (not per-cs_id eval patches)
#   terminology.yaml — stub for future term rules
#   styles/ — family router, principles, skeleton exemplars (StylePack)
#   prompts/ — CS email + QA system prompts (PromptPack)
#   evals/ — gates.yaml + EvalPack YAML (see evals/README.md)
#   ../eval_pack.py — retrieval_boost, presales_brief, pinned_reference, etc.
