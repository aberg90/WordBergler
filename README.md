# WordBergler

**Realistic Password and Username Wordlist Generator for Penetration Testing**

WordBergler is a smart and customizable wordlist generator designed to mimic how real people form passwords and usernames. It's ideal for ethical hacking, red teaming, and security auditing in authorized environments.
The attacker will use this script after enumerating information from the target from publically available data and/or social engineering. This tool is a baseline and improvements could be made to generate a better output.
Feel free to fork this repo and adjust for your own unique penetration testing environment.

NOTE: This is a penetration tool used only with the written and verbal consent of the targetted individual. Using this tool without the targets consent is illegal. 

---

## Features

Generates highly targeted **passwords** using:
- First/Last Names (e.g., JohnSmith, smithJ)
- Brand, TV show, actor, and hobby names
- Common patterns with years, symbols, phone chunks, PINs
- Casing variants: `lower`, `UPPER`, `Capitalized`
- Combined base words and common suffixes

Also creates **username** candidates:
- first + last (e.g., johnsmith)
- first.last, j.smith, john_smith
- Variants with years, symbols, and gamertag styles
- Leetspeak variants (e.g., j0hnsm1th)

saves output to:
- `custom_wordlist.txt` → Passwords
- `likely_usernames.txt` → Usernames

---

## Why Use WordBergler?

Unlike generic tools like `crunch` or `cupp`, WordBergler generates **realistic** and **personalized** credential guesses using behavioral patterns and context clues (like hobbies, phone fragments, and common casing).

It's perfect for:
- Targeted credential stuffing
- Brute-force attacks during pen tests
    - Suggested programs to use with this: Hydra, Hashcat
- OSINT-informed enumeration
- Training and red teaming scenarios

---

## Installation

WordBergler is a standalone Python script.

### Requirements

- Python 3.6+
- `tqdm` library (for progress bars)

Install tqdm if you haven't:

```bash
pip install tqdm
