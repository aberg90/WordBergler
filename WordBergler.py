#!/usr/bin/env python3
"""
WordBergler – realistic password **and username** word‑list generator
"""

import sys, re # Provides regular expression support for pattern matching and string manipulation.
from datetime import datetime # Allows working with dates and times.
from collections import OrderedDict # Creates dictionaries that preserve the order of items as they are inserted.
from tqdm import tqdm  # pip install tqdm (Displays a progress bar during long loops for better visibility.)

# --------------------------------------------------------------------------- #
#  HELP                                                                       #
# --------------------------------------------------------------------------- #
HELP_MESSAGE = """
====================================================================
WORDBERGLER PASSWORD & USERNAME WORDLIST GENERATOR – HELP & USAGE
====================================================================

DESCRIPTION
-----------
WordBergler generates realistic, human-like password and username
wordlists based on user-supplied input. It leverages personal info,
common formatting patterns, and behavioral trends to create prioritized
lists that reflect how real people form their credentials.

This can be useful for penetration testing, red teaming, or security
auditing in a responsible and authorized context.

FEATURES
--------
✔ Creates a prioritized password list using:
    - Last names
    - First initial + last name (e.g., jsmith, JSmith)
    - Brand, TV, actor, or hobby names
    - Full names and two-word combinations
    - Important dates, PINs, phone fragments, and symbols
    - Common casing variations (lowercase, UPPERCASE, Capitalized)

✔ Also generates likely usernames using:
    - first + last
    - first.last
    - first initial + last (e.g., jdoe, j.doe)
    - Variants with birth years (e.g., jdoe1990)

✔ Saves output to two files:
    - custom_wordlist.txt     → Password candidates
    - likely_usernames.txt    → Username candidates

USAGE
-----
Run the script and answer the prompts. Comma-separated input is accepted
for most fields. You can skip fields by leaving them blank.

$ python3 wordbergler.py

When prompted, enter data such as:
    Victim name(s): John Smith, Jane Doe
    Relative name(s): Mike Smith
    Other notable name(s): Jenny Johnson
    Favorite brand(s): Nike, Apple
    Favorite TV show(s): Breaking Bad, Friends
    Favorite actor(s): Tom Hanks
    Favorite hobby/activities: Hiking, Gaming
    Important date(s): 1990, 0423, 2001
    Phone number(s): 123-456-7890, (555) 321-6543
    PIN / short number(s) or symbols: 1234, 9876, @!, !1
    Extra base words: Pass, Secret, letmein

You will also be asked for:
    - Victim’s birth year (optional)
    - Min and max password length (default 6–16)

STRUCTURE
---------
        ┌──────────────────────────────┐
        │  #!/usr/bin/env python3      │
        └────────────┬─────────────────┘
                     │
            ┌────────▼────────┐
            │  wordbergler    │
            └────────┬────────┘
     ┌───────────────┼───────────────────┐
     │               │                   │
┌────▼────┐   ┌──────▼──────┐     ┌──────▼──────┐
│ Imports │   │ Helper Funcs│     │ User Input  │
└────┬────┘   └──────┬──────┘     └──────┬──────┘
     │               │                   │
     │       + ask_csv()                 │
     │       + case_variants()          │
     │       + phone_chunks(), etc.     │
     └───────────────┬──────────────────┘
                     │
               ┌─────▼─────┐
               │ Main Logic│
               └─────┬─────┘
                     │
     ┌───────────────┼────────────────────────────┐
     │               │                            │
┌────▼────┐   ┌──────▼───────┐           ┌────────▼────────┐
│ Clean & │   │ Build Variant│           │   Generate Files │
│ Process │   │     Pools    │           └────────┬────────┘
│  Input  │   └──────┬───────┘                    │
└─────────┘          │                      ┌─────▼──────┐
                     │                      │ Generate   │
        ┌────────────▼────────────┐         │ Usernames  │
        │ + Names: first, last    │         └─────┬──────┘
        │ + Brand, hobbies, etc. │               │
        │ + Symbols, numbers     │         ┌─────▼──────┐
        └────────────────────────┘         │ Generate   │
                                           │ Passwords  │
                                           └────────────┘


HELP OPTIONS
------------
Use any of the following to show this help message:
    -h        --help        help

EXAMPLES
--------
$ python3 wordbergler.py
... [follow prompts] ...

Output:
    custom_wordlist.txt      → password list
    likely_usernames.txt     → username list

NOTES
-----
✓ Spaces and tabs are removed for password safety
✓ Duplicates are filtered automatically
✓ Do not use this tool against systems you don’t own or have permission to test

AUTHOR
------
Aaron Berg
====================================================================
"""


if any(arg in sys.argv for arg in ("-h", "--help", "help")):
    print(HELP_MESSAGE)
    sys.exit()

# --------------------------------------------------------------------------- #
#  HELPER FUNCTIONS                                                           #
# --------------------------------------------------------------------------- #
def ask_csv(prompt_msg: str) -> list[str]:
    """Prompt for comma‑separated values → list (trimmed, may be empty)."""
    raw = input(prompt_msg).strip()
    return [p.strip() for p in raw.split(',')] if raw else []

def strip_spaces(words: list[str]) -> list[str]:
    """Remove *all* spaces/tabs from each string (password friendliness)."""
    return [re.sub(r'\s+', '', w) for w in words if w.strip()]

def split_first_last(full: str) -> tuple[str, str]:
    """Return (first, last) or (first, '') if only one word."""
    parts = full.split()
    return (parts[0], parts[-1]) if len(parts) >= 2 else (parts[0], '')

def case_variants(word: str) -> list[str]:
    """lower, Capitalised, UPPER variants (duplicates removed later)."""
    w = re.sub(r'\s+', '', word)
    return [w.lower(), w.capitalize(), w.upper()]

def initial_last_variants(first: str, last: str) -> list[str]:
    if not (first and last):
        return []
    root = f"{first[0]}{last}"
    return [root.capitalize(), root.lower(), (first[0] + last).upper()]

def fused_initial_last(first: str, last: str) -> list[str]:
    return [*(initial_last_variants(first, last))]   # identical logic

def brand_title_variants(title: str) -> list[str]:
    parts = title.split()
    if len(parts) >= 2:
        first, last = parts[0], parts[-1]
        return list(OrderedDict.fromkeys(
            case_variants(last) +
            initial_last_variants(first, last) +
            case_variants(first + last)
        ))
    return case_variants(title)

def double_word_variants(list1: list[str], list2: list[str]) -> list[str]:
    combos = [
        case_variants(w1 + w2)
        for w1 in list1 for w2 in list2
        if w1 != w2
    ]
    # flatten & dedupe while preserving order
    return list(OrderedDict.fromkeys([v for sub in combos for v in sub]))

def phone_chunks(phones: list[str]) -> list[str]:
    """Return last‑4, last‑7, area code, prefix etc."""
    out: set[str] = set()
    for p in phones:
        nums = re.sub(r'\D', '', p)
        if len(nums) >= 4:
            out.add(nums[-4:])
        if len(nums) >= 7:
            out.add(nums[-7:])
        if len(nums) >= 10:
            out.update({nums[:3], nums[:6], nums})
    return list(out)

def clean_username(word: str) -> str:
    """Keep only lowercase letters, numbers, dots, and underscores."""
    return re.sub(r'[^a-z0-9._]', '', word.lower())

# --------------------------------------------------------------------------- #
#  USER INPUT (single pass; keep raw + stripped)                              #
# --------------------------------------------------------------------------- #
victim_raw      = ask_csv("Victim name(s): ")
relative_raw    = ask_csv("Relative name(s): ")
other_raw       = ask_csv("Other notable name(s): ")

fav_brands      = ask_csv("Favorite brand(s): ")
fav_tv          = ask_csv("Favorite TV show(s)/Genres: ")
fav_actors      = ask_csv("Favorite actor(s): ")
fav_hobbies     = ask_csv("Favorite hobby/activities: ")

important_dates = ask_csv("Important date(s) (YYYY / DDMM): ")
phones_raw      = ask_csv("Phone number(s): ")
pin_or_symbols  = ask_csv("PIN / short number(s) or symbols: ")
extra_bases_raw = ask_csv("Extra base words (e.g., Pass, Secret): ")

try:
    birth_year = int(input("Victim's birth year (blank if unknown): ") or 0)
except ValueError:
    birth_year = 0

try:
    min_len = int(input("Minimum password length (default 6): ") or 6)
    max_len = int(input("Maximum password length (default 16): ") or 16)
except ValueError:
    min_len, max_len = 6, 16

# versions with spaces stripped – ** passwords only**
victim_clean   = strip_spaces(victim_raw)
relative_clean = strip_spaces(relative_raw)
other_clean    = strip_spaces(other_raw)
extra_bases    = strip_spaces(extra_bases_raw)

all_clean_names = victim_clean + relative_clean + other_clean
all_titles      = strip_spaces(fav_brands + fav_tv + fav_actors + fav_hobbies)

# --------------------------------------------------------------------------- #
#  BUILD VARIANT POOLS                                                        #
# --------------------------------------------------------------------------- #
last_pool, init_last_pool, full_pool, brand_pool = [], [], [], []

for full in all_clean_names:                   # works but last name lost…
    first, last = split_first_last(full)       # <-- cannot split! handled later
    # Because clean names lost spaces we *only* take them for password bases.
    full_pool.extend(case_variants(full))

# We need first/last *with* spaces for username variants and extra pools
for full in victim_raw + relative_raw + other_raw:
    first, last = map(clean_username, split_first_last(full))


    if last:
        last_pool.extend([v for v in case_variants(last) if v not in last_pool])
        init_last_pool.extend([v for v in initial_last_variants(first, last)
                               if v not in init_last_pool])
        init_last_pool.extend([v for v in fused_initial_last(first, last)
                               if v not in init_last_pool])

    full_pool.extend([v for v in case_variants(full) if v not in full_pool])

for title in all_titles:
    brand_pool.extend([v for v in brand_title_variants(title) if v not in brand_pool])

double_pool = double_word_variants(all_clean_names, all_titles)

# --------------------------------------------------------------------------- #
#  NUMBERS / YEARS                                                            #
# --------------------------------------------------------------------------- #
pin_nums   = [p for p in pin_or_symbols if re.fullmatch(r"\d{1,6}", p)]
extra_syms = [s for s in pin_or_symbols if not re.fullmatch(r"\d{1,6}", s)]

year_now = datetime.now().year
if 1900 <= birth_year <= year_now:
    years = [str(y) for y in range(year_now, birth_year - 1, -1)]
else:
    years = [str(y) for y in range(year_now, 1980, -1)]

numbers = list(OrderedDict.fromkeys(important_dates + pin_nums + phone_chunks(phones_raw) + years))
symbols = ["!", "@", "@!", "1", "!!", "!!!"] + extra_syms

# --------------------------------------------------------------------------- #
#  USERNAME GENERATION                                                        #
# --------------------------------------------------------------------------- #
def leetspeak(word: str) -> str:
    """Convert to simple leetspeak (optional variants)."""
    return (
        word.replace("a", "4").replace("A", "4")
            .replace("e", "3").replace("E", "3")
            .replace("i", "1").replace("I", "1")
            .replace("o", "0").replace("O", "0")
            .replace("s", "5").replace("S", "5")
    )

username_set: set[str] = set()
yy = str(birth_year)[-2:] if birth_year else ""

for full in victim_raw + relative_raw + other_raw:
    first, last = map(str.lower, split_first_last(full))

    # Skip empty names
    if not first and not last:
        continue

    base_combos = set()

    # Basic combos
    base_combos.update({first, last})
    if first and last:
        base_combos.update({
            f"{first}{last}",
            f"{first}.{last}",
            f"{first}_{last}",
            f"{first[0]}{last}",
            f"{first[0]}.{last}",
            f"{first[0]}_{last}",
            f"{last}{first}",
            f"{last}.{first}",
            f"{last}_{first}",
            f"{last}{first[0]}",
        })

        # Birth year combos
        if birth_year:
            base_combos.update({
                f"{first}{last}{birth_year}",
                f"{first[0]}{last}{birth_year}",
                f"{last}{yy}",
                f"{first[0]}{last}{yy}",
                f"{first}{yy}",
                f"{first}{birth_year}",
                f"{last}{birth_year}",
            })

        # Gamertag-style suffixes
        base_combos.update({
            f"{first}{last}123",
            f"{first}{last}007",
            f"{first}{last}420",
            f"{first}{last}69",
            # f"{first}{last}_x",
            # f"x_{first}{last}",
            # f"{first}{last}_xx",
        })

        # Leetspeak version
        base_combos.add(leetspeak(f"{first}{last}"))

    # Add hobby/brand nicknames
    for fav in fav_brands + fav_hobbies:
        fav_clean = fav.lower().replace(" ", "")
        if first:
            base_combos.update({
                f"{first}{fav_clean}",
                f"{fav_clean}{first}"
            })
        if last:
            base_combos.update({
                f"{last}{fav_clean}",
                f"{fav_clean}{last}"
            })

        # Save variants with cleaning and capitalization
    for u in base_combos:
        u = clean_username(u.strip())
        if not u:
            continue
        username_set.add(u)
        if u[0].isalpha():
            cap = u[0].upper() + u[1:]
            if cap != u:
                username_set.add(cap)

with open("likely_usernames.txt", "w") as f:
    for u in sorted(username_set):
        u = clean_username(u)
        if not u:
            continue
        f.write(u + "\n")
        if u[0].isalpha():
            cap = u[0].upper() + u[1:]
            if cap != u:
                f.write(cap + "\n")

# --------------------------------------------------------------------------- #
#  PASSWORD GENERATION                                                        #
# --------------------------------------------------------------------------- #
def add_passwords(outfile, base: str):
    base_clean = re.sub(r'\s+', '', base)
    if min_len <= len(base_clean) <= max_len:
        outfile.write(base_clean + "\n")

    for year in years:
        ycombo = base_clean + year
        if min_len <= len(ycombo) <= max_len:
            outfile.write(ycombo + "\n")
        for sym in symbols:
            ys = ycombo + sym
            if min_len <= len(ys) <= max_len:
                outfile.write(ys + "\n")

    for num in numbers:
        ncombo = base_clean + num
        if min_len <= len(ncombo) <= max_len:
            outfile.write(ncombo + "\n")
        for sym in symbols:
            ns = ncombo + sym
            if min_len <= len(ns) <= max_len:
                outfile.write(ns + "\n")

with open("custom_wordlist.txt", "w") as out:
    for pool_name, pool in [
        ("Last names", last_pool),
        ("Initial+Last", init_last_pool),
        ("Brand/Title", brand_pool),
        ("Full names", full_pool),
        ("Extra bases", extra_bases),
        ("Double words", double_pool),
    ]:
        for base in tqdm(pool, desc=f"{pool_name:17}", unit="word"):
            add_passwords(out, base)

print("\n[+] custom_wordlist.txt created.")
print("[+] likely_usernames.txt created.")
