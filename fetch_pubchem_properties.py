import argparse
import logging
import os
import time

import pandas as pd
import requests

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

# Delay between requests to stay within PubChem's usage guidelines
REQUEST_DELAY_SECONDS = 0.5

# Retry settings for transient network/API failures
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2.0

# -----------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def _request_with_retry(url, timeout=10):
    """
    Perform a GET request with retry-with-backoff on network errors and
    on 5xx responses. Returns the response object, or None if all
    attempts fail.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code >= 500:
                log.warning(
                    "Server error %d on attempt %d/%d for %s",
                    response.status_code, attempt, MAX_RETRIES, url,
                )
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_BACKOFF_SECONDS * attempt)
                    continue
            return response
        except requests.exceptions.RequestException as e:
            log.warning(
                "Network error on attempt %d/%d for %s: %s",
                attempt, MAX_RETRIES, url, e,
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    log.error("All %d attempts failed for %s", MAX_RETRIES, url)
    return None


def fetch_cid_by_name(compound_name):
    """
    Resolve a compound name to a PubChem CID.
    Returns the CID (int) on success, or None if not found.

    If multiple CIDs are returned for the name (ambiguous match, e.g.
    salts, tautomers, stereoisomers), the top match is used but the
    ambiguity is logged so it can be reviewed.
    """
    url = f"{PUBCHEM_BASE}/compound/name/{requests.utils.quote(compound_name)}/cids/JSON"
    response = _request_with_retry(url)

    if response is None:
        return None

    if response.status_code == 200:
        cids = response.json().get("IdentifierList", {}).get("CID", [])
        if not cids:
            return None
        if len(cids) > 1:
            log.warning(
                "'%s' resolved to %d CIDs %s — using top match %d.",
                compound_name, len(cids), cids, cids[0],
            )
        return cids[0]
    elif response.status_code == 404:
        log.warning("'%s' not found in PubChem.", compound_name)
    else:
        log.warning(
            "Unexpected status %d for '%s'.", response.status_code, compound_name
        )
    return None


def fetch_properties_by_cid(cid):
    """
    Retrieve PROPERTIES for a given CID.
    Returns a dict of {property: value}, or an empty dict on failure.
    """
    props_str = ",".join(PROPERTIES)
    url = f"{PUBCHEM_BASE}/compound/cid/{cid}/property/{props_str}/JSON"
    response = _request_with_retry(url)

    if response is None:
        return {}

    if response.status_code == 200:
        prop_table = response.json().get("PropertyTable", {}).get("Properties", [])
        if prop_table:
            return prop_table[0]  # one compound → one row
    else:
        log.warning(
            "Could not fetch properties for CID %d (status %d).",
            cid, response.status_code,
        )
    return {}


def process_library(input_path, output_path):
    """
    Reads the compound library, queries PubChem for each entry, and writes
    a consolidated properties table to a CSV file.
    """
    df_library = pd.read_csv(input_path)

    if df_library.empty:
        raise ValueError(f"Input file '{input_path}' contains no rows.")

    required_col = "compound_name"
    if required_col not in df_library.columns:
        raise ValueError(f"Input CSV must contain a '{required_col}' column.")

    duplicates = df_library[required_col][df_library[required_col].duplicated()]
    if not duplicates.empty:
        log.warning(
            "Input contains %d duplicate compound name(s): %s",
            len(duplicates), sorted(set(duplicates)),
        )

    log.info("Loaded %d compounds from '%s'.", len(df_library), input_path)

    results = []

    for _, row in df_library.iterrows():
        name = row["compound_name"]
        log.info("Processing: %s", name)

        # Step 1: name → CID
        cid = fetch_cid_by_name(name)
        time.sleep(REQUEST_DELAY_SECONDS)

        if cid is None:
            results.append({"compound_name": name, "CID": None, "fetch_status": "not_found"})
            continue

        # Step 2: CID → properties
        props = fetch_properties_by_cid(cid)
        time.sleep(REQUEST_DELAY_SECONDS)

        if not props:
            results.append({"compound_name": name, "CID": cid, "fetch_status": "property_error"})
            continue

        # Merge compound name, library metadata, and retrieved properties
        record = {"compound_name": name, "CID": cid, "fetch_status": "ok"}
        for col in df_library.columns:
            if col != required_col:
                record[col] = row[col]
        record.update(props)
        results.append(record)

    df_results = pd.DataFrame(results)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_results.to_csv(output_path, index=False)

    ok_count = (df_results["fetch_status"] == "ok").sum()
    log.info(
        "Done. %d / %d compounds retrieved successfully. Output: '%s'",
        ok_count, len(df_library), output_path,
    )
    return df_results


def main():
    parser = argparse.ArgumentParser(
        description="Fetch physicochemical properties for a compound library from PubChem."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to input CSV. Must contain a 'compound_name' column.",
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to write the output properties CSV.",
    )
    args = parser.parse_args()
    process_library(args.input, args.output)


if __name__ == "__main__":
    main()
