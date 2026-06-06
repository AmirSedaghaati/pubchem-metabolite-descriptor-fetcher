import requests
import pandas as pd
import time
import logging
import os

INPUT_FILE  = "data/mock_data/compound_library_mock.csv"
OUTPUT_FILE = "results/compound_properties.csv"

# PubChem PUG REST base URL
PUBCHEM_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

# Properties to retrieve — chosen for Lipinski / drug-likeness screening
PROPERTIES = [
    "MolecularFormula",
    "MolecularWeight",
    "XLogP",
    "HBondDonorCount",
    "HBondAcceptorCount",
    "TPSA",
    "RotatableBondCount",
    "InChIKey",
    "CanonicalSMILES",
]

# Small delay between requests to stay within PubChem's usage guidelines
REQUEST_DELAY_SECONDS = 0.5

# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def fetch_cid_by_name(compound_name):
    """
    Resolve a compound name to a PubChem CID.
    Returns the CID (int) on success, or None if not found.
    """
    url = f"{PUBCHEM_BASE}/compound/name/{requests.utils.quote(compound_name)}/cids/JSON"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            cids = response.json().get("IdentifierList", {}).get("CID", [])
            if cids:
                return cids[0]   # take the top (most relevant) match
        elif response.status_code == 404:
            log.warning("'%s' not found in PubChem.", compound_name)
        else:
            log.warning("Unexpected status %d for '%s'.", response.status_code, compound_name)
    except requests.exceptions.RequestException as e:
        log.error("Network error for '%s': %s", compound_name, e)
    return None


def fetch_properties_by_cid(cid, properties):
    """
    Retrieve a set of physicochemical properties for a given CID.
    Returns a dict of {property: value}, or an empty dict on failure.
    """
    props_str = ",".join(properties)
    url = f"{PUBCHEM_BASE}/compound/cid/{cid}/property/{props_str}/JSON"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            prop_table = response.json().get("PropertyTable", {}).get("Properties", [])
            if prop_table:
                return prop_table[0]   # one compound → one row
        else:
            log.warning("Could not fetch properties for CID %d (status %d).", cid, response.status_code)
    except requests.exceptions.RequestException as e:
        log.error("Network error fetching CID %d: %s", cid, e)
    return {}


def process_library(input_path, output_path):
    """
    Main function: reads the compound library, queries PubChem for each entry,
    and writes a consolidated properties table to a CSV file.
    """
    # Load the library. 'compound_name' is the only column we strictly need.
    df_library = pd.read_csv(input_path)
    required_col = "compound_name"
    if required_col not in df_library.columns:
        raise ValueError(f"Input CSV must contain a '{required_col}' column.")

    log.info("Loaded %d compounds from '%s'.", len(df_library), input_path)

    results = []

    for _, row in df_library.iterrows():
        name = row["compound_name"]
        log.info("Processing: %s", name)

        # Step 1: name → CID
        cid = fetch_cid_by_name(name)
        time.sleep(REQUEST_DELAY_SECONDS)

        if cid is None:
            # Record the compound with empty properties so it is visible in output
            results.append({"compound_name": name, "CID": None, "fetch_status": "not_found"})
            continue

        # Step 2: CID → properties
        props = fetch_properties_by_cid(cid, PROPERTIES)
        time.sleep(REQUEST_DELAY_SECONDS)

        if not props:
            results.append({"compound_name": name, "CID": cid, "fetch_status": "property_error"})
            continue

        # Merge compound name and library metadata with the retrieved properties
        record = {"compound_name": name, "CID": cid, "fetch_status": "ok"}
        # Carry over any extra columns from the library (source organism, notes, etc.)
        for col in df_library.columns:
            if col != required_col:
                record[col] = row[col]
        record.update(props)
        results.append(record)

    df_results = pd.DataFrame(results)

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_results.to_csv(output_path, index=False)

    # Summary
    ok_count = (df_results["fetch_status"] == "ok").sum()
    log.info(
        "Done. %d / %d compounds retrieved successfully. Output: '%s'",
        ok_count, len(df_library), output_path,
    )
    return df_results


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    process_library(INPUT_FILE, OUTPUT_FILE)
