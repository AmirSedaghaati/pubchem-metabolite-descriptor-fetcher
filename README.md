# pubchem-natural-compound-fetcher

Fetches physicochemical properties of a given set of natural compounds using PubChem REST API and generates summary plot for drug-likeness.

## The Problem
In the compound selection part of the thesis, a library of around 80 natural compounds was used. Standard physicochemical parameters (molecular weight, LogP, TPSA, and number of H-bond donors and acceptors) were extracted for each compound, which were then used in the assessment of Lipinski's rule of five and the oral bioavailability criteria to prioritize them for the in vitro tests.

Manual procedure was as follows:
1. Search each compound name on PubChem website.
2. Transcribe appropriate property values to a single row in a spreadsheet.
3. Perform this for each compound, then perform for each compound again whenever the library was modified.

This turned out to be a significant time sink when the library had to be updated several times during the project and transcription errors occurred.

## The Solution
Fetchpubchemproperties.py takes a CSV file with compound names as input, translates the names into PubChem CIDs via PUG REST API and makes a second call to fetch desired properties. Then, all results were saved in a new CSV in results/. A small delay between the requests is added in order to follow the PubChem usage policy.

Visualize_properties.R takes this results file and generates two plots:
- A plot of molecular weight against XLogP, with lines for Lipinski's threshold added.
- A plot of TPSA values across the library, with a 140 absorption threshold marked.
These figures are what I used directly in my thesis in order to argue why a certain set of compounds should be chosen over another.

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

This script will print progress to the terminal and will save the results to compound_properties.csv once it has finished. For 6 compounds with mock data this should take between 10-15 seconds due to the request delays.

Generated PDFs can be found in the results/ directory.

NB. Required R packages: ggplot2, dplyr, readr, tidyr.Install them using:
R
install.packages(c("ggplot2", "dplyr", "readr", "tidyr"))

Notes & Caveats

    The PubChem name-to-CID resolver works quite well for most common compounds, but may have surprises in the output for very trivial names or names that are ambiguous. It is always a good idea to confirm the CIDs for any compound which is critical to the analysis.

 This script does not currently cope gracefully with rate-limiting (HTTP 503) responses from PubChem. For libraries with more than ~200 compounds, you would probably want to implement a retry mechanism or the PubChem PUG-REST batch endpoint.

 Properties will not be available for all compounds: for any given compound, fields like XLogP will report as NaN if PubChem does not supply them.

Honest Skill Disclaimer

I'm a biochemist who utilize computers to conduct research and I am currently trying to learn about more advanced topics.
 This code was written to resolve a particular research issue during my thesis (which is the manual fetch of physico-chemical information from a public database, over and over). It is NOT a library nor a public software release.
 It is readable and runnable code from a research point of view but certainly not from a software developer's perspective. Any suggestion/critique would be highly appreciated.
