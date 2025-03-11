import re

def debug_nwpw_extraction(nwinput_str):
    # Locate "nwpw" block (Improved regex for robustness)
    match = re.search(r"nwpw\s*\n(.*?)\n\s*end", nwinput_str, re.DOTALL | re.IGNORECASE)
    if not match:
        print("❌ ERROR: No 'nwpw' block found.")
        return

    nwpw_block = match.group(1).strip()

    # Print the extracted block for verification
    print("🔍 Corrected Extracted 'nwpw' Block:\n", nwpw_block, "\n")

    # Extract specific values
    patterns = {
        "xc": r"\bxc\s+(\S+)",
        "mult": r"\bmult\s+(\d+)",
        "cutoff": r"\bcutoff\s+([\d\.]+)"
    }

    extracted = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, nwpw_block, re.IGNORECASE)
        extracted[key] = match.group(1).strip() if match else None

    # Print extracted key values
    for key, value in extracted.items():
        if value:
            print(f"✅ Found {key.upper()}: {value}")
        else:
            print(f"❌ MISSING: {key.upper()}")

    # Capture full `pspspin up/down` values
    pspspin_up_match = re.search(r"pspspin\s+up\s+d\s+([-\d\s]+)", nwpw_block, re.IGNORECASE)
    pspspin_down_match = re.search(r"pspspin\s+down\s+d\s+([-\d\s]+)", nwpw_block, re.IGNORECASE)

    if pspspin_up_match:
        print("✅ Found pspspin UP:", " ".join(pspspin_up_match.group(1).split()))
    else:
        print("❌ MISSING: pspspin UP")

    if pspspin_down_match:
        print("✅ Found pspspin DOWN:", " ".join(pspspin_down_match.group(1).split()))
    else:
        print("❌ MISSING: pspspin DOWN")

    # Extract "set nwpw:" values
    set_values = re.findall(r"set\s+nwpw:(\S+)\s+(\S+)", nwinput_str, re.IGNORECASE)
    if set_values:
        print("\n✅ Found SET values:")
        for key, value in set_values:
            print(f"   - {key}: {value}")
    else:
        print("❌ MISSING: No 'set nwpw:' values found.")

# Load `test.nw` and analyze it
with open("test.nw", "r") as ff:
    nw_content = ff.read()

debug_nwpw_extraction(nw_content)

