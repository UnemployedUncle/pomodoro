# Pure Focus Stitch Integration

## Summary

This document compares the current MVP with the `stitch_pure_focus` reference screens and defines the integrated shell now implemented in the app.

- Scope includes only internal app screens.
- Authentication remains in the current flow.
- `stitch_pure_focus/0_Start` is excluded from this integration pass.
- Global shell rules:
  - Top-left keeps only `Pure Focus`
  - Top-right header icons are removed
  - Bottom navigation contains only `Timer`, `Dashboard`, `Setting`

## Current MVP vs Stitch Reference

| Area | Current MVP before integration | Stitch reference | Integrated result |
| --- | --- | --- | --- |
| App structure | Single page with multiple stacked panels | Separate, atmosphere-first screens | Single SPA kept, but reorganized into 3 top-level views |
| Header | Title plus right-side user/logout action area | Minimal brand-led top bar | Fixed header with only `Pure Focus` |
| Bottom navigation | No true app navigation | Multiple bottom-nav variants, often 4 items | Exactly 3 tabs: `Timer`, `Dashboard`, `Setting` |
| Timer | Functional timer panel with quote, photo, progress, task lists | Cinematic timer canvases with circular focus expression | Existing timer logic preserved, wrapped in Stitch-inspired immersive presentation |
| Dashboard | Summary and collection split into separate panels | Unified dashboard with stats, calendar, collections | Summary and collection merged into one Dashboard view |
| Cycle setup | Cycles, builder, and run setup split across separate panels | One setting-oriented setup screen | Combined into one Setting view |

## Panel Mapping

| Previous panel | New home |
| --- | --- |
| `summary-panel` | `Dashboard` |
| `collection-panel` | `Dashboard` |
| `timer-panel` | `Timer` |
| `cycles-panel` | `Setting` |
| `builder-panel` | `Setting` |
| `run-setup-panel` | `Setting` |
| `logout` control from header area | `Setting` session block |

## Adopted Elements From Stitch

### Timer

Reference sources:
- `stitch_pure_focus/1_timer_default`
- `stitch_pure_focus/3_timer_progress`

Adopted:
- Full-bleed photographic timer stage
- Serif-led timer typography
- Circular progress emphasis
- Reduced chrome around focus content
- Quote and source placed inside the timer atmosphere

Not adopted:
- Extra top-right icons
- Four-item bottom menus
- Additional menu destinations such as `Collection`, `Zen`, or `Stats`

### Dashboard

Reference source:
- `stitch_pure_focus/4_dashboard`

Adopted:
- Unified reflective dashboard feeling
- Glass-card summary sections
- Collection folded into the same screen as metrics

Not adopted:
- Additional CTA-only flow
- Expanded analytics sections not backed by current data contracts

### Setting

Reference source:
- `stitch_pure_focus/5_set_new_cycle`

Adopted:
- Single setup-oriented screen
- Clear separation between cycle selection, custom builder, and run preparation
- More editorial heading structure for setup tasks

Not adopted:
- Separate settings icon in the header
- Additional bottom-nav items beyond the agreed 3
- New account/settings surfaces outside current MVP scope

## Functional Preservation

The integration is a structural and visual shell rewrite, but it preserves the current backend/API contracts and core MVP behavior:

- Demo login still works
- Existing cycle list and ownership rules stay intact
- Custom cycle creation stays intact
- Run setup still captures todo and nottodo inputs
- Starting a run still creates a server-side run and launches the timer
- Triple-click stop behavior remains intact
- Reward and collection flows remain intact

## Files Affected

- `app/templates/index.html`
- `app/static/css/app.css`
- `app/static/js/app.js`
- `tests/test_app.py`

## Validation Checklist

- Internal shell shows only `Timer`, `Dashboard`, `Setting`
- Header keeps only `Pure Focus`
- Dashboard contains summary plus collection
- Setting contains cycle list, builder, and run setup
- Starting a run moves the user from Setting to Timer
- Existing backend tests continue to pass
