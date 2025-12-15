# APEX SALES INTELLIGENCE — MASTER SPEC
## Version 1.0 | December 3, 2025

---

# SECTION 1: SYSTEM STATUS

## What's Working
- ✅ 1,226 contacts imported (filtered from HubSpot)
- ✅ EnhancedEnrichment 3-stage pipeline (Perplexity → GPT-4 → DB)
- ✅ ApexScoringEngine initialized and integrated
- ✅ Dashboard API URLs fixed (12 components)
- ✅ Today's Board endpoint and parsing
- ✅ Intelligence tab section extraction
- ✅ Theme system files created

## Do Not Modify Without Request
- `api.py` lines 85-380 (EnhancedEnrichment + scoring init)
- `dashboard_v1/src/components/TodaysBoard.tsx`
- `dashboard_v1/src/components/ContactDetailModal.tsx`
- `scripts/import_hubspot.py` (has filters)
- All files in `dashboard_v1/src/theme/`

---

# SECTION 2: DESIGN SYSTEM — "WARM MIDNIGHT"

## Color Palette (Dark Mode)

### Backgrounds
| Token | Hex | Usage |
|-------|-----|-------|
| `midnight-950` | `#0A0A0A` | Page background |
| `midnight-900` | `#141414` | Cards, panels |
| `midnight-800` | `#1C1C1C` | Elevated, hover |
| `midnight-600` | `#2A2A2A` | Borders |

### Primary Accent — Gold
| Token | Hex | Usage |
|-------|-----|-------|
| `gold` | `#E5B84C` | Buttons, hot scores, CTAs |
| `gold-hover` | `#D4A853` | Hover state |
| `gold-muted` | `rgba(229,184,76,0.15)` | Backgrounds |
| `gold-glow` | `rgba(229,184,76,0.25)` | Glow effects |

### Secondary Accent — Purple (AI)
| Token | Hex | Usage |
|-------|-----|-------|
| `violet` | `#A78BFA` | AI elements |
| `violet-muted` | `rgba(167,139,250,0.15)` | AI backgrounds |

### Status Colors
| Token | Hex | Usage |
|-------|-----|-------|
| `lime` | `#BFFF00` | Success, positive |
| `coral` | `#F97316` | Warning, at-risk |
| `red` | `#EF4444` | Urgent, errors |
| `magenta` | `#E879F9` | Special |

### Text
| Token | Hex | Usage |
|-------|-----|-------|
| `text-primary` | `#FAFAFA` | Headings |
| `text-secondary` | `#A3A3A3` | Body |
| `text-tertiary` | `#737373` | Metadata |

---

# SECTION 3: COMPONENT SPECS

## Cards
- Background: `midnight-900`
- Border: `1px solid midnight-600`
- Border radius: `16px` (large), `12px` (medium)
- Hover: border `midnight-500`, shadow `card-hover`
- Active/Focus: gold border glow

## Prospect Card
- Left border: 4px accent (gold=hot, coral=warm, red=urgent, violet=AI)
- Hover: translateX(4px), gold glow shadow
- AI Reason: italic, left border `violet`

## Buttons
- Primary: gold gradient, dark text
- Secondary: transparent, border, hover → gold
- Action (small): midnight-800 bg, hover → gold-muted

## Scores
- Hot (85+): `#E5B84C` with text-shadow glow
- Warm (60-84): `#F97316`
- Cold (<60): `#737373`

---

# SECTION 4: INTERACTION PRINCIPLES

## Graphical-First
- Direct manipulation (drag, tap, click)
- No chat/voice for primary actions
- Quick action buttons on hover

## Alive Interfaces
- Spring physics on card enter
- Breathing glow on AI processing
- Tactile button press (scale 0.97)
- Score tick animation on change

## Story Flows
- Morning Brief: auto-playing insight sequence
- Metric animations on load
- Section highlighting during onboarding

## Neo-Brutalist (Selective)
- Urgent alerts: hard shadow, slight rotation
- Hot scores (95+): oversized, glowing
- Empty states: bold typography

---

# SECTION 5: TAILWIND CONFIG

colors: {
midnight: {
950: '#0A0A0A',
900: '#141414',
800: '#1C1C1C',
700: '#262626',
600: '#2A2A2A',
500: '#3D3D3D',
},
gold: {
DEFAULT: '#E5B84C',
hover: '#D4A853',
muted: 'rgba(229, 184, 76, 0.15)',
},
violet: {
DEFAULT: '#A78BFA',
muted: 'rgba(167, 139, 250, 0.15)',
},
lime: '#BFFF00',
coral: '#F97316',
},
boxShadow: {
'gold-glow': '0 0 20px rgba(229, 184, 76, 0.15)',
'card-hover': '0 8px 24px rgba(0, 0, 0, 0.4)',
},

text

---

# SECTION 6: NEXT PRIORITIES

1. Implement Warm Midnight theme in `tailwind.config.js`
2. Update existing theme files to match new palette
3. Build KPI cards with new styling
4. Build Prospect cards with gold/purple accents
5. Add Framer Motion for card animations
6. Implement Morning Brief story flow

