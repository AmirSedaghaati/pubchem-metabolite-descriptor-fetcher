# pubchem-natural-compound-fetcher

Retrieves physicochemical properties from the PubChem REST API for a list of natural compounds and produces drug-likeness summary plots.

## Context
This project was developed as part of my master's thesis in biochemistry at **[University Name]**, where I investigated a set of plant-derived secondary metabolites as potential inhibitors of **[target enzyme]**. The work presented here is a supporting computational component of a broader wet-lab study; it is not a standalone software package.

The original compound library used in the thesis cannot be shared because it is part of an ongoing research project. All files in `data/mock_data/` are fabricated examples that demonstrate the expected input format and allow the code to be run without access to the original data.

## The Problem
During the compound selection phase of the thesis, I worked with a library of approximately 80 natural compounds. For each compound, I needed to collect standard physicochemical descriptors — molecular weight, LogP, TPSA, H-bond donor and acceptor counts — to evaluate them against Lipinski's Rule of Five and oral bioavailability thresholds before prioritising candidates for in vitro assays.

The manual workflow was:
1. Search each compound by name on the PubChem website.
2. Copy the relevant property values into a spreadsheet row.
3. Repeat for every compound, and repeat again each time the library was revised.

This became a noticeable time sink as the library was updated multiple times during the project, and manual data entry introduced transcription errors.

## The Solution
`fetch_pubchem_properties.py` reads a CSV file of compound names, resolves each name to a PubChem CID using the PUG REST API, retrieves the requested properties in a second request, and writes a consolidated CSV to `results/`. A short delay between requests is included to comply with PubChem's usage guidelines.

`visualize_properties.R` reads that results file and produces two figures:
- A scatter plot of molecular weight vs. XLogP with Lipinski threshold lines overlaid.
- A bar chart of TPSA values across the library with the 140 Å² absorption threshold marked.

These figures were used directly in the thesis to justify compound prioritisation.

## Repository Structure

```text
pubchem-natural-compound-fetcher/
│
├── data/
│   └── mock_data/
│       └── compound_library_mock.csv   # Fabricated example — not the real library
│
├── results/                            # Generated outputs (not committed; see .gitignore)
│   ├── compound_properties.csv
│   ├── lipinski_scatter.pdf
│   └── tpsa_barplot.pdf
│
├── notebooks/                          # Exploratory Jupyter notebooks (not cleaned up)
│
├── fetch_pubchem_properties.py         # Main Python script
├── visualize_properties.R              # R script for figures
├── requirements.txt
├── .gitignore
└── README.md

How to Run

Tested with Python 3.10 and R 4.3. An active internet connection is required to query the PubChem API.

1. Clone the repository
git clone [https://github.com/](https://github.com/)<your-username>/pubchem-natural-compound-fetcher.git
cd pubchem-natural-compound-fetcher

2. Install Python dependencies
Bash
pip install -r requirements.txt

3. Run the data fetcher
Bash

python fetch_pubchem_properties.py

The script will print progress to the terminal and write results/compound_properties.csv when finished. With the mock data (6 compounds) this takes roughly 10–15 seconds due to the request delays.

Output PDFs will appear in results/.

Note: R packages required: ggplot2, dplyr, readr, tidyr. Install them via:
R
install.packages(c("ggplot2", "dplyr", "readr", "tidyr"))

Notes and Limitations

    The PubChem name-to-CID resolver works well for common compound names but can return unexpected matches for trivial or ambiguous names. It is advisable to verify CIDs for any compound that is central to the analysis.

    The script does not currently handle rate-limiting responses (HTTP 503) from PubChem gracefully. For libraries larger than ~200 compounds, adding retry logic or using the PubChem PUG-REST batch endpoint would be more appropriate.

    Property availability varies by compound; some entries in the output will have NaN for fields such as XLogP if PubChem does not report them.

Honest Skill Disclaimer

I am a biochemist who uses computational tools to advance my research and am still learning more advanced concepts.
 This code was written to solve a specific research problem encountered during my thesis — namely, the repetitive manual retrieval of physicochemical data from a public database — and not to serve as a general-purpose library or a publicly distributed software package.
 The scripts are functional and readable, but they reflect the work of a researcher rather than a software developer. Feedback or suggestions are welcome.
