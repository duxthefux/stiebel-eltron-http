"""Show detailed analysis of the 3 real conflicts"""

print("=" * 80)
print("REAL CONFLICTS - DETAILED ANALYSIS")
print("=" * 80)

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONFLICT 1: "isttemperatur"                                                 │
│ Found in: ACTUAL_TEMPERATURE_1 and ACTUAL_TEMPERATURE                       │
└─────────────────────────────────────────────────────────────────────────────┘

PROBLEM:
  The German word "ISTTEMPERATUR" (actual temperature) appears in both:
  - ACTUAL_TEMPERATURE_1: Used for heating circuit 1 specific temperature
  - ACTUAL_TEMPERATURE: Used for general actual temperature
  
  This creates ambiguity when parsing German HTML pages.

EVIDENCE FROM TESTDATA:
  In s_1_0_de.html (System page):
    Table: HEIZUNG
      Row: "ISTTEMPERATUR HK 1" → This is ACTUAL_TEMPERATURE_1
    
    Table: WARMWASSER (DHW)
      Row: "ISTTEMPERATUR" → This is ACTUAL_TEMPERATURE

CURRENT ALIASES:
  ACTUAL_TEMPERATURE_1: [..., "ISTTEMPERATUR 1", "ISTTEMPERATUR", ...]
  ACTUAL_TEMPERATURE: [..., "ISTTEMPERATUR", ...]

FIX:
  Remove "ISTTEMPERATUR" from ACTUAL_TEMPERATURE_1
  Keep only specific forms: "ISTTEMPERATUR HK 1", "ISTTEMPERATUR 1"
  
  The bare "ISTTEMPERATUR" should only match ACTUAL_TEMPERATURE

IMPACT:
  - Heating circuit 1 will still be matched by "ISTTEMPERATUR HK 1"
  - DHW section will correctly match bare "ISTTEMPERATUR"
  - No ambiguity in German pages
""")

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONFLICT 2: "varmemængde"                                                   │
│ Found in: HEATING_SECTION and AMOUNT_OF_HEAT_SECTION                        │
└─────────────────────────────────────────────────────────────────────────────┘

PROBLEM:
  The Danish word "VARMEMÆNGDE" (heat amount) appears in both section aliases.
  This is actually TWO different section headers in Danish ISG pages.

EVIDENCE FROM TESTDATA:
  In s_1_0_da.html (System page):
    Table header: "VARME" → HEATING_SECTION (note: not "VARMEMÆNGDE"!)
  
  In s_1_1_da.html (Heat Pump page):
    Table header: "VARMEMÆNGDE" → AMOUNT_OF_HEAT_SECTION

CURRENT ALIASES:
  HEATING_SECTION: [..., (no "VARMEMÆNGDE" should be here)]
  AMOUNT_OF_HEAT_SECTION: [..., "VARMEMÆNGDE", "VARMEMAENGDE"]

DISCOVERY:
  The comment in HEATING_SECTION says:
  "NOTE: 'VARME' (Danish) removed - too generic, matches 'VARMEMÆNGDE'"
  
  But somehow "VARMEMÆNGDE" itself got added to HEATING_SECTION!

FIX:
  Remove "VARMEMÆNGDE" from HEATING_SECTION
  Keep it only in AMOUNT_OF_HEAT_SECTION where it belongs
  
  HEATING_SECTION should NOT have "VARMEMÆNGDE" at all.
  (Danish uses "VARME" for heating section, which was already removed as too generic)

IMPACT:
  - Danish Heat Pump page will correctly match "VARMEMÆNGDE" → AMOUNT_OF_HEAT_SECTION
  - No conflict with HEATING_SECTION
  - Danish System page heating section may need alternative alias if needed
""")

print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ CONFLICT 3: "vd heizen summe"                                               │
│ Found in: VD_HEATING_TOTAL and VD_HEATING_SUM                               │
└─────────────────────────────────────────────────────────────────────────────┘

PROBLEM:
  The German label "VD HEIZEN SUMME" appears in both energy row value aliases.
  These are two different canonical keys for different purposes.

EVIDENCE FROM TESTDATA:
  In s_1_1_de.html (Heat Pump page):
    Table: WÄRMEMENGE (Amount of Heat)
      Row: "VD HEIZEN SUMME" → This is VD_HEATING_SUM
    
    Same table also has:
      Row: "VD HEIZUNG GESAMT" → This could be VD_HEATING_TOTAL

CURRENT ALIASES:
  VD_HEATING_TOTAL: [..., "VD HEIZUNG GESAMT", "VD HEIZEN SUMME", ...]
  VD_HEATING_SUM: ["VD HEATING SUM", "VD HEIZEN SUMME", "VD HEIZUNG SUMME"]

ANALYSIS:
  VD_HEATING_SUM is meant for a specific label variant
  VD_HEATING_TOTAL is the main energy total
  
  "VD HEIZEN SUMME" is more specific to the SUM variant
  "VD HEIZUNG GESAMT" means "VD heating total" (GESAMT = total)

FIX:
  Remove "VD HEIZEN SUMME" from VD_HEATING_TOTAL
  Keep it only in VD_HEATING_SUM
  
  VD_HEATING_TOTAL should use "VD HEIZUNG GESAMT" for German

IMPACT:
  - Clear distinction between TOTAL and SUM variants
  - German pages will map correctly to the right canonical key
  - Both are mapped to the same const key anyway, so no functional change
""")

print("=" * 80)
print("CONTEXTUAL OVERLAPS (OK - DO NOT FIX)")
print("=" * 80)
print("""
The following overlaps are INTENTIONAL and CORRECT:

1. "lämminvesi" (Finnish for "hot water")
   - DHW_SECTION: Section header on System page
   - VD_DHW_DAY: Row label on Heat Pump page
   → Different contexts (header vs row), both correct

2. "lämmitys" (Finnish for "heating")
   - HEATING_SECTION: Section header on System page
   - VD_HEATING_DAY: Row label on Heat Pump page
   → Different contexts (header vs row), both correct

3. "topeni" (Czech for "heating")
   - HEATING_SECTION: Section header on System page
   - VD_HEATING_DAY: Row label on Heat Pump page
   → Different contexts (header vs row), both correct

These work because the scraper first matches section headers to find the table,
then matches row labels within that table. They never conflict.
""")

print("=" * 80)
print("SUMMARY OF REQUIRED FIXES")
print("=" * 80)
print("""
1. ACTUAL_TEMPERATURE_1: Remove "ISTTEMPERATUR" (keep only with suffix)
2. HEATING_SECTION: Remove "VARMEMÆNGDE" (wrong section)
3. VD_HEATING_TOTAL: Remove "VD HEIZEN SUMME" (belongs in VD_HEATING_SUM)

Total fixes needed: 3 alias removals
""")
