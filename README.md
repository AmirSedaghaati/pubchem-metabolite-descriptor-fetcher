# PubChem Natural Compound Fetcher

> An automated data retrieval and visualization pipeline to extract physicochemical properties from the PubChem REST API for drug-likeness assessment.

---

## Background
The task of evaluating the drug-likeness of the libraries compounds involves fetching standard physicochemical properties (Mol. Weight, Log P, TPSA, H-bond donors/acceptors) to check Lipinski's Rule of Five and orally bioavailability. Querying public databases manually to obtain these parameters on successive library updates will prove to be an extremely tedious task prone to transcription errors and bottleneck in the compound prioritizing stage.

---

## Implementation
This repository automates the retrieval and preliminary analysis of compound properties. The core Python script (`fetch_pubchem_properties.py`) interfaces with the PubChem PUG REST API to resolve common compound names to CIDs and fetch the targeted physicochemical data. It handles API requests with built-in delays to comply with PubChem's usage policies. An accompanying R script processes the output to generate publication-ready visualizations mapping the library against established bioavailability thresholds.

---

## Technical Stack

| Component | Function |
| :--- | :--- |
| **Python 3.10+ / requests & pandas** | API communication, data parsing, and tabular formatting |
| **R 4.3+ / ggplot2 & dplyr** | Statistical visualization of chemical space |
| **PubChem PUG REST API** | Primary data source for physicochemical properties |

---

## File Structure

```text
pubchem-natural-compound-fetcher/
│
├── data/
│   └── mock_data/
│       └── compound_library_mock.csv       # Fabricated example list for testing
│
├── results/                                # Output directory (generated on execution)
│   ├── compound_properties.csv
│   ├── lipinski_scatter.pdf
│   └── tpsa_barplot.pdf
│
├── fetch_pubchem_properties.py             # Main data retrieval script
├── visualize_properties.R                  # R script for visualization
├── requirements.txt
├── .gitignore
└── README.md
