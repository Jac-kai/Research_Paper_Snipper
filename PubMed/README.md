# PubMed Research Paper Collector

A command-line Python utility for collecting biomedical research paper metadata from PubMed through the NCBI E-utilities API.

This project searches PubMed by keyword, collects PubMed IDs (PMIDs), fetches detailed article records in XML format, parses useful metadata, and saves the final dataset as a CSV file.

## Project Purpose

This project is designed for literature review dataset collection and biomedical text mining practice.

It can be used as a data collection component for:

- Biomedical NLP projects
- Literature review datasets
- Research trend analysis
- Deep learning portfolio projects
- Paper abstract classification or clustering
- Topic modeling on biomedical research papers

## Features

- Search PubMed papers by keyword.
- Collect PMIDs through NCBI ESearch.
- Fetch article metadata through NCBI EFetch.
- Parse PubMed XML records.
- Extract title, abstract, DOI, journal, year, authors, keywords, MeSH terms, and publication types.
- Save results as a UTF-8 CSV file.
- Support command-line arguments.
- Include retry logic for temporary API or server errors.
- Include safe request delay to reduce API rate-limit risk.
- Support optional NCBI API key through environment variables.

## Data Source

This project uses the NCBI E-utilities API:

- **ESearch**: searches PubMed and returns PMIDs.
- **EFetch**: fetches detailed PubMed article records by PMID.

This project collects metadata and abstracts available in PubMed records. It does not download full-text papers.

## Project Structure

Example structure:

```text
Research_Paper_Snipper/
│
├── PubMed/
│   ├── PubMed_Paper_Crawling.py
│   └── Paper/
│       └── pubmed_papers.csv
│
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/pubmed-research-paper-collector.git
cd pubmed-research-paper-collector
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -3.11 -m venv .venv311
.\.venv311\Scripts\Activate.ps1
```

Windows CMD:

```cmd
py -3.11 -m venv .venv311
.\.venv311\Scripts\activate.bat
```

macOS / Linux:

```bash
python3 -m venv .venv311
source .venv311/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you do not have a `requirements.txt` file yet, install the required packages manually:

```bash
pip install requests pandas urllib3
```

## Requirements

```text
pandas
requests
urllib3
```

Python standard library modules used in this project:

- `os`
- `re`
- `time`
- `math`
- `argparse`
- `xml.etree.ElementTree`
- `typing`

## Usage

### Run with default settings

```bash
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py
```

Default configuration in the script:

```python
DEFAULT_QUERY = "brain tumor"
DEFAULT_MAX_RESULTS = 100
DEFAULT_BATCH_SIZE = 50
DEFAULT_OUTPUT_FILE = "Research_Paper_Snipper/PubMed/Paper/pubmed_papers.csv"
```

### Run with a custom query

```bash
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py --query "brain tumor"
```

### Run with query and maximum result count

macOS / Linux:

```bash
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py \
    --query "deep learning brain tumor MRI" \
    --max-results 50
```

Windows PowerShell:

```powershell
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py `
    --query "deep learning brain tumor MRI" `
    --max-results 50
```

Windows CMD:

```cmd
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py ^
    --query "deep learning brain tumor MRI" ^
    --max-results 50
```

### Run with a custom output CSV path

macOS / Linux:

```bash
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py \
    --query "deep learning brain tumor MRI" \
    --max-results 100 \
    --batch-size 50 \
    --output "Research_Paper_Snipper/PubMed/Paper/brain_tumor_dl_mri.csv"
```

Windows PowerShell:

```powershell
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py `
    --query "deep learning brain tumor MRI" `
    --max-results 100 `
    --batch-size 50 `
    --output "Research_Paper_Snipper/PubMed/Paper/brain_tumor_dl_mri.csv"
```

Windows CMD:

```cmd
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py ^
    --query "deep learning brain tumor MRI" ^
    --max-results 100 ^
    --batch-size 50 ^
    --output "Research_Paper_Snipper/PubMed/Paper/brain_tumor_dl_mri.csv"
```

### Run with an email parameter

```bash
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py ^
    --query "deep learning gene expression cancer" ^
    --max-results 100 ^
    --batch-size 50 ^
    --output "Research_Paper_Snipper/PubMed/Paper/gene_expression_dl.csv" ^
    --email "your_email@example.com"
```

## Command-Line Arguments

| Argument | Type | Default | Description |
|---|---:|---|---|
| `--query` | `str` | `"brain tumor"` | Search query for PubMed. |
| `--max-results` | `int` | `100` | Maximum number of PubMed records to collect. |
| `--batch-size` | `int` | `50` | Number of PMIDs to fetch per EFetch request. |
| `--output` | `str` | `"Research_Paper_Snipper/PubMed/Paper/pubmed_papers.csv"` | Output CSV file path. |
| `--email` | `str` | `"your_email@example.com"` | Email used for NCBI E-utilities identification. |

## Output Columns

The generated CSV contains the following columns:

| Column | Description |
|---|---|
| `pmid` | PubMed ID. |
| `doi` | Digital Object Identifier, if available. |
| `pmc_id` | PubMed Central ID, if available. |
| `title` | Article title. |
| `abstract` | Article abstract text. |
| `journal` | Full journal title. |
| `journal_iso` | ISO journal abbreviation. |
| `year` | Publication year. |
| `language` | Article language code. |
| `authors` | Semicolon-separated author names. |
| `keywords` | Semicolon-separated author keywords. |
| `mesh_terms` | Semicolon-separated MeSH descriptor terms. |
| `publication_types` | Article publication type labels. |
| `pubmed_url` | PubMed article URL. |
| `doi_url` | DOI resolver URL. |

## Example Output

Example CSV preview:

```text
pmid,doi,pmc_id,title,abstract,journal,year,authors,pubmed_url,doi_url
12345678,10.xxxx/example,PMC123456,Deep Learning for Brain Tumor MRI,...,Medical Imaging Journal,2024,Jane Smith; John Chen,https://pubmed.ncbi.nlm.nih.gov/12345678/,https://doi.org/10.xxxx/example
```

## Recommended Search Queries

For biomedical deep learning projects, specific queries usually produce better datasets than broad terms.

Examples:

```text
deep learning brain tumor MRI
brain tumor segmentation deep learning
glioma classification deep learning MRI
deep learning gene expression cancer
machine learning cancer genomics
natural language processing clinical notes cancer
```

## API Rate Limit Notes

NCBI E-utilities has request-rate limits.

This script includes a default sleep delay after each request:

```python
DEFAULT_SLEEP_SECONDS = 0.4
```

This delay keeps the script below approximately 3 requests per second.

You can provide an NCBI API key through an environment variable.

Windows PowerShell:

```powershell
$env:NCBI_API_KEY="your_api_key_here"
$env:NCBI_EMAIL="your_email@example.com"
```

Windows CMD:

```cmd
set NCBI_API_KEY=your_api_key_here
set NCBI_EMAIL=your_email@example.com
```

macOS / Linux:

```bash
export NCBI_API_KEY="your_api_key_here"
export NCBI_EMAIL="your_email@example.com"
```

## How It Works

### 1. Search PMIDs with ESearch

The script sends a request to:

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
```

Important parameters:

| Parameter | Meaning |
|---|---|
| `db="pubmed"` | Search the PubMed database. |
| `term=query` | Search keyword or query. |
| `retmode="json"` | Return JSON response. |
| `retmax` | Number of PMIDs to return in one page. |
| `retstart` | Starting index for pagination. |
| `sort` | Sorting method. |

### 2. Fetch XML records with EFetch

The script sends PMID batches to:

```text
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi
```

Important parameters:

| Parameter | Meaning |
|---|---|
| `db="pubmed"` | Fetch records from PubMed. |
| `id="pmid1,pmid2,pmid3"` | Comma-separated PMID list. |
| `retmode="xml"` | Return XML response. |

### 3. Parse XML

The script uses Python's built-in `xml.etree.ElementTree` module to parse XML records and extract useful metadata.

### 4. Save CSV

The parsed paper records are converted into a pandas DataFrame and saved as a CSV file:

```python
df.to_csv(output_file, index=False, encoding="utf-8-sig")
```

## Notes About CSV Overwriting

If the same output path is used repeatedly, the CSV file will be overwritten.

For example, this command overwrites the same file every time:

```bash
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py ^
    --output "Research_Paper_Snipper/PubMed/Paper/pubmed_papers.csv"
```

To avoid overwriting, use a different output file name:

```bash
python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py ^
    --query "brain tumor segmentation deep learning" ^
    --output "Research_Paper_Snipper/PubMed/Paper/brain_tumor_segmentation_dl.csv"
```

## Limitations

- This project does not download full-text papers.
- Not every PubMed record has a DOI.
- Not every PubMed record has an abstract.
- Some records may not include keywords or MeSH terms.
- Search quality depends on the query.
- Very broad queries may return mixed or noisy results.
- The script currently saves one CSV file per run.

## Possible Future Improvements

- Add automatic timestamped output file names.
- Add support for date-range filtering.
- Add support for publication type filtering.
- Add logging instead of print statements.
- Add unit tests for XML parser helpers.
- Add text preprocessing for NLP projects.
- Add abstract classification or clustering modules.
- Add duplicate detection by DOI and title.
- Add command-line support for API key.

## Disclaimer

This project is for educational and research portfolio purposes. Users should follow NCBI usage policies and respect publisher copyright restrictions when using metadata, abstracts, or external article links.

## License

This project can be released under the MIT License.

## Author

Zack Liu