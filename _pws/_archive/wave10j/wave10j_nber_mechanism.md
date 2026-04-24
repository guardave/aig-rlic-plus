# Wave 10J — NBER Shading Mechanism Audit

Date: 2026-04-24
Agent: App Dev Ace
Purpose: Inform Vera's VIZ-NBER1 rule

---

## Finding: NBER Shading is Baked into Vera's JSON Files

### Evidence

1. `app/components/charts.py` — `load_plotly_chart()` does the following:
   - Reads the Plotly JSON file from disk (`pio.from_json(f.read())`).
   - Calls `st.plotly_chart(fig, ...)` to render it.
   - Does NOT modify the figure object in any way before rendering.
   - No `add_vrect`, `add_shape`, or NBER date logic exists anywhere in `charts.py`.

2. `app/components/page_templates.py` — calls `load_plotly_chart(...)` as a
   pass-through. No post-processing of the figure. No NBER shading added.

3. Search across all component files confirms no programmatic NBER shading:
   - `grep -rn "NBER\|nber\|vrect\|recession" app/components/` returns only
     one match: a comment in `charts.py` line 44 referencing "VIZ-V2 NBER
     shading rules" as a documentation cross-reference, not code.

### Conclusion

NBER shading is entirely baked into Vera's JSON files at chart-generation time.
The portal's chart loader is a pure JSON renderer — it deserialises the Plotly
JSON and renders it verbatim. Any recession-period shading visible in a chart
was added by Vera's `generate_charts_*.py` script (using `fig.add_vrect(...)`
or similar) before the JSON was written to disk.

### Implications for VIZ-NBER1

- Vera owns the NBER shading contract completely. If shading is missing or
  incorrectly dated in a chart, the fix is in the chart-generation script —
  not in the portal renderer.
- The portal cannot retroactively add or remove NBER shading to charts it
  did not generate. There is no "NBER overlay" toggle or injection point in
  `load_plotly_chart()`.
- VIZ-NBER1 should therefore specify:
  (a) Which chart types must include NBER shading (e.g., time-series overlays,
      regime charts, rolling metric charts).
  (b) The canonical NBER recession dates Vera should use (e.g., from FRED
      USREC series or a pinned CSV in `docs/schemas/`).
  (c) The visual specification (fill colour, opacity, layer order) so all
      charts are visually consistent.
- There is no app-dev work needed to implement VIZ-NBER1. Ace's only
  responsibility is ensuring `load_plotly_chart()` does not strip shading
  from the JSON — which it does not.

### Chart rendering stack (for Vera's reference)

```
Vera's generate_charts script
  ├─ fig.add_vrect(x0=start, x1=end, fillcolor="grey", opacity=0.15, ...)
  └─ fig.write_json(f"output/charts/{pair_id}/plotly/{chart_name}.json")

Portal render path
  └─ load_plotly_chart(chart_name, pair_id=pair_id)
       └─ pio.from_json(f.read())       # deserialise — vrects preserved
            └─ st.plotly_chart(fig)     # render — vrects visible
```

No intermediate step modifies the figure. NBER shading is safe end-to-end.
