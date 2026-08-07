"""Canonical indicator/target display-name maps (DUP-1 consolidation).

Before fix260531 the same maps were duplicated in three places — pair_registry,
page_templates, and sidebar (with a different short-form scheme). The three
had already drifted: page_templates was missing 4 entries.

This module is the single source of truth. Every consumer that needs to
render an indicator or target as human-readable text should import from here.

Adding a new pair: append one entry to ``INDICATOR_NAMES`` keyed by either
the canonical short name (``indpro``) or the full pair_id (``indpro_spy``).
Target tickers (lowercase) go in ``TARGET_NAMES``.

Short-form labels for navigation chrome (sidebar dropdown) live in
``SHORT_INDICATOR_LABELS`` — kept separate because the audience differs:
long-form for body prose, short-form for nav and chart axes.
"""

from __future__ import annotations

# ─── Long-form display names (canonical) ──────────────────────────────────

INDICATOR_NAMES: dict[str, str] = {
    "indpro": "Industrial Production",
    "indpro_spy": "Industrial Production",
    "indpro_xlp": "Industrial Production",
    "permit_spy": "Building Permits",
    "vix_vix3m_spy": "VIX/VIX3M Ratio",
    "hy_ig_spy": "HY-IG Credit Spread",
    "umcsent_xlv": "University of Michigan Consumer Sentiment",
    "gold_copper_xli": "Gold/Copper Ratio",
    "busloans": "Commercial & Industrial Loans",
    "busloans_spy": "Commercial & Industrial Loans",
    "petrol_inv": "Petroleum Inventories",
    "petrol_inv_spy": "Petroleum Inventories",
    "ism_services": "ISM Services PMI",
    "ism_services_spy": "ISM Services PMI",
    "m2sl_yoy": "M2 Money Supply (YoY)",
    "m2sl_yoy_spy": "M2 Money Supply (YoY)",
    "phlxsox": "PHLX Semiconductor Index",
    "phlxsox_spy": "PHLX Semiconductor Index",
    "t10y3m": "10Y-3M Treasury Spread",
    "t10y3m_spy": "10Y-3M Treasury Spread",
    "nhs": "New Home Sales (NHS)",
    "nhs_spy": "New Home Sales (NHS)",
    "nhs_saar": "New Home Sales (SAAR)",
    "nhs_saar_spy": "New Home Sales (SAAR)",
    "cass_freight": "Cass Freight Index (Shipments)",
    "cass_freight_spy": "Cass Freight Index (Shipments)",
    "eci_total_comp": "Employment Cost Index (ECI, Total Compensation)",
    "eci_total_comp_spy": "Employment Cost Index (ECI, Total Compensation)",
    "wells_fargo_housing": "NAHB/Wells Fargo Housing Market Index (HMI)",
    "wells_fargo_housing_spy": "NAHB/Wells Fargo Housing Market Index (HMI)",
    }

TARGET_NAMES: dict[str, str] = {
    # DPS-LF1 (2026-06-10): long form + (abbreviation) on dashboard surfaces.
    "spy": "S&P 500 (SPY)",
    "xlv": "Health Care Select Sector (XLV)",
    "xlp": "Consumer Staples Select Sector (XLP)",
    "xli": "Industrial Select Sector (XLI)",
}


# ─── DPS-LF1 / VIZ-NS1: ticker-style abbreviations for first-mention form ──
#
# Only pairs whose indicator has a TRUE ticker/abbreviation distinct from its
# long-form name. Pairs whose long form already embeds the short form
# ("VIX/VIX3M Ratio", "HY-IG Credit Spread", "Gold/Copper Ratio",
# "Building Permits") are intentionally absent — appending a bracket there
# would produce redundant noise ("Building Permits (Building Permits)").
INDICATOR_ABBREV: dict[str, str] = {
    "indpro": "INDPRO",
    "indpro_spy": "INDPRO",
    "indpro_xlp": "INDPRO",
    "umcsent_xlv": "UMCSENT",
    # DPS-LF1 first-mention: "Commercial & Industrial Loans (C&I Loans)".
    # "C&I Loans" is the conventional abbreviation (FRED ticker BUSLOANS is
    # a pipeline token, not a reader-facing abbreviation).
    "busloans": "C&I Loans",
    "busloans_spy": "C&I Loans",
    "petrol_inv": "PETROL",
    "petrol_inv_spy": "PETROL",
    # "SOX" is the conventional ticker abbreviation for the PHLX Semiconductor
    # Index; the long form does not embed it, so first-mention renders
    # "PHLX Semiconductor Index (SOX)".
    "phlxsox": "SOX",
    "phlxsox_spy": "SOX",
    # 'NHS' is the conventional short form; long form "New Home Sales" does not embed it, so first-mention renders
    # "New Home Sales (NHS)".
    "nhs": "NHS",
    "nhs_spy": "NHS",
    # "Cass Freight" is the conventional short form; the long form
    # "Cass Freight Index (Shipments)" already embeds it, so this abbrev is
    # only used where a compact ticker-style label is wanted.
    "cass_freight": "Cass Freight",
    "cass_freight_spy": "Cass Freight",
    # "ECI" is the conventional BLS abbreviation. The long form
    # "Employment Cost Index (ECI, Total Compensation)" already embeds it,
    # so long_form_with_abbrev's substring check suppresses a redundant
    # second bracket; this abbrev is only used where a compact
    # ticker-style label is wanted.
    "eci_total_comp": "ECI",
    "eci_total_comp_spy": "ECI",
    # wells_fargo_housing / wells_fargo_housing_spy intentionally ABSENT:
    # the long form "NAHB/Wells Fargo Housing Market Index (HMI)" already
    # embeds the short form's tokens, but "NAHB HMI" is not a contiguous
    # substring, so long_form_with_abbrev would render a redundant second
    # bracket "... (HMI) (NAHB HMI)". Compact surfaces get "NAHB HMI" via
    # SHORT_INDICATOR_LABELS below (per this dict's intentionally-absent
    # policy for embeds).
}


# ─── Short-form labels for nav chrome (sidebar dropdown, chart axes) ──────
#
# Kept separate from INDICATOR_NAMES because the audience differs: the
# sidebar wants ``INDPRO`` while the body prose wants ``Industrial
# Production``. Charts (axes/legends/titles) use SHORT_INDICATOR_LABELS
# (this matches what BL-VIZ-NS1 will codify as the naming standard).

SHORT_INDICATOR_LABELS: dict[str, str] = {
    "indpro_spy": "INDPRO",
    "indpro_xlp": "INDPRO",
    "permit_spy": "Building Permits",
    "vix_vix3m_spy": "VIX/VIX3M",
    "hy_ig_spy": "HY-IG Credit Spread",
    "umcsent_xlv": "UMCSENT",
    "gold_copper_xli": "Gold/Copper",
    "busloans_spy": "C&I Loans",
    "petrol_inv_spy": "Petroleum Inventories",
    "t10y3m_spy": "10Y-3M Spread",
    "nhs_spy": "NHS",
    "nhs_saar_spy": "NHS (SAAR)",
    "cass_freight_spy": "Cass Freight",
    "eci_total_comp_spy": "ECI",
    "wells_fargo_housing": "NAHB HMI",
    "wells_fargo_housing_spy": "NAHB HMI",
}


# ─── Resolvers ────────────────────────────────────────────────────────────


def resolve_indicator(pair_id: str, interp_indicator: str = "") -> str:
    """Return the long-form indicator display name for ``pair_id``.

    Falls back to ``INDICATOR_NAMES[interp_indicator]`` then to the raw
    ``interp_indicator`` then to ``pair_id`` itself — matching the legacy
    fallback chain in pair_registry / page_templates.
    """
    return (
        INDICATOR_NAMES.get(pair_id)
        or INDICATOR_NAMES.get(interp_indicator, interp_indicator)
        or pair_id
    )


def long_form_with_abbrev(pair_id: str, interp_indicator: str = "") -> str:
    """DPS-LF1 / VIZ-NS1 first-mention form: "Long Form (ABBREV)".

    Composes the long-form indicator name with its ticker abbreviation in
    brackets — e.g. ``"Industrial Production (INDPRO)"``. Pairs without a
    distinct ticker abbreviation (or whose long form already contains the
    short form) return just the long form. Use this on dashboard surfaces
    and on the first mention per page; subsequent mentions may use
    ``SHORT_INDICATOR_LABELS``.
    """
    long = resolve_indicator(pair_id, interp_indicator)
    abbrev = INDICATOR_ABBREV.get(pair_id)
    if abbrev and abbrev.lower() not in long.lower():
        return f"{long} ({abbrev})"
    return long


def resolve_target(interp_target: str) -> str:
    """Return the long-form target display name for an ``interp_target``
    ticker (lowercase). Falls back to the raw ticker."""
    return TARGET_NAMES.get(interp_target, interp_target or "")


def resolve_short_indicator(pair_id: str, target_ticker: str = "") -> str:
    """Return the short-form indicator label (for nav chrome / chart axes).

    Falls back to uppercased pair_id prefix with target suffix stripped —
    e.g. ``unknown_xyz`` → ``UNKNOWN`` when target_ticker is ``xyz``.
    """
    if pair_id in SHORT_INDICATOR_LABELS:
        return SHORT_INDICATOR_LABELS[pair_id]
    suffix = f"_{(target_ticker or '').lower()}"
    base = pair_id[: -len(suffix)] if suffix and pair_id.endswith(suffix) else pair_id
    return base.upper().replace("_", "-")


__all__ = [
    "INDICATOR_NAMES",
    "TARGET_NAMES",
    "SHORT_INDICATOR_LABELS",
    "resolve_indicator",
    "resolve_target",
    "resolve_short_indicator",
]
