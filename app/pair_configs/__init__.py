"""Pair-specific content modules for the AIG-RLIC+ portal.

Under Rule APP-PT1 (page-template abstraction), each pair's Story /
Evidence / Strategy / Methodology pages are thin wrappers that call the
corresponding template function from `app.components.page_templates` with
content read from this package.

Layout:
    app/pair_configs/
    ├── __init__.py                 # this file
    ├── indpro_xlp_config.py        # INDPRO × XLP pair
    └── {pair_id}_config.py         # one module per pair

Each pair module exports:
    - STORY_CONFIG        -- object with narrative strings for Story page
    - EVIDENCE_METHOD_BLOCKS -- dict of Level-1 / Level-2 method blocks
    - STRATEGY_CONFIG     -- object with strategy-page narrative strings
    - METHODOLOGY_CONFIG  -- MethodologyConfig dataclass instance

Anything derivable from `winner_summary.json`, `signal_scope.json`,
`interpretation_metadata.json`, `stationarity_tests_*.csv`, or
`analyst_suggestions.json` MUST be read dynamically by the template —
NOT hardcoded here. The config contains only content that cannot be
derived from those producer artifacts.
"""
