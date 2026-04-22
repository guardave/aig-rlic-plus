
### Wave 10H.1 (2026-04-22) — APP-PT2 Exploratory Insights

- Helper owns its trailing `st.markdown("---")` separator. Call-site has no separator. This keeps the legacy render path byte-identical: if no entries, zero `st.*` calls emitted.
- Chart-key pre-keyed as `exploratory_{pair_id}_{chart_name}_{idx}` to survive repeated `load_plotly_chart` invocations on the same Methodology page across reruns — Streamlit requires unique widget keys.
- APP-CC1 canonical prefix `"What this shows:"` applied to ELI5 caption per registry; APP-PT2 §3b text said "rendered verbatim" but §3b still allows the canonical leading bold — verified against other helpers (same pattern used in render_signal_universe).
- Smoke tests only exercise the backward-compat branch until Vera ships `exploratory_charts` entries. The fully-populated branch is covered by the mocked dry-run harness under `temp/260422_app_pt2/` — same pattern as my earlier schema-consumer mocks.
