"""
PubMed Research Paper Collector
===============================

A command-line Python utility for collecting biomedical research paper metadata
from PubMed through the NCBI E-utilities API.

This script performs the following workflow:

1. Search PubMed by keyword using ESearch.
2. Collect PubMed IDs (PMIDs) from the ESearch JSON response.
3. Fetch detailed PubMed records by PMID using EFetch.
4. Parse PubMed XML records into structured Python dictionaries.
5. Convert the extracted records into a pandas DataFrame.
6. Save the final dataset as a UTF-8 CSV file.

Main use cases
--------------
- Building literature review datasets.
- Collecting paper metadata for NLP preprocessing.
- Exploring biomedical research trends.
- Preparing portfolio projects related to biomedical text mining.
- Creating biomedical research paper datasets for machine learning projects.

Data source
-----------
NCBI E-utilities API:
- ESearch: searches PubMed and returns PMIDs.
- EFetch: fetches detailed article records by PMID.

Notes
-----
This script collects metadata and abstracts available from PubMed records.
It does not download full-text papers.

NCBI recommends identifying API tools with `tool` and `email` parameters.
An API key can be provided through the `NCBI_API_KEY` environment variable.

Example
-------
Run with default settings:

    python PubMed_Paper_Crawling.py

Run with custom query and output path:

    python PubMed_Paper_Crawling.py ^
        --query "deep learning brain tumor MRI" ^
        --max-results 100 ^
        --batch-size 50 ^
        --output "Research_Paper_Snipper/PubMed/Paper/brain_tumor_dl_mri.csv" ^
        --email "your_email@example.com"
"""
# ----------------------------------------------------------------------------------------------------
import os
import re
import time
import math
import argparse
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional

import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
# ----------------------------------------------------------------------------------------------------
# Hyperparameters

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

DEFAULT_QUERY = "brain tumor"
DEFAULT_MAX_RESULTS = 100
DEFAULT_BATCH_SIZE = 50
DEFAULT_OUTPUT_FILE = "Research_Paper_Snipper/PubMed/Paper/pubmed_papers.csv"

# Without NCBI API key: keep requests below 3 requests / second.
# With NCBI API key: limit can be higher, but this script still uses a safe delay.
DEFAULT_SLEEP_SECONDS = 0.4

# Optional environment variables
NCBI_API_KEY = os.getenv("NCBI_API_KEY")
NCBI_EMAIL = os.getenv("NCBI_EMAIL", "your_email@example.com")
NCBI_TOOL = "pubmed_research_collector"
# ----------------------------------------------------------------------------------------------------
# HTTP session with retry
def create_session() -> requests.Session:
    """
    PubMed Research Paper Collector
    ===============================

    A command-line Python utility for collecting biomedical research paper metadata
    from PubMed through the NCBI E-utilities API.

    This script performs the following workflow:

    1. Search PubMed by keyword using ESearch.
    2. Collect PubMed IDs (PMIDs) from the ESearch JSON response.
    3. Fetch detailed PubMed records by PMID using EFetch.
    4. Parse PubMed XML records into structured Python dictionaries.
    5. Convert the extracted records into a pandas DataFrame.
    6. Save the final dataset as a UTF-8 CSV file.

    Main use cases
    --------------
    - Building literature review datasets.
    - Collecting paper metadata for NLP preprocessing.
    - Exploring biomedical research trends.
    - Preparing portfolio projects related to biomedical text mining.
    - Creating biomedical research paper datasets for machine learning projects.

    Data source
    -----------
    NCBI E-utilities API:
    - ESearch: searches PubMed and returns PMIDs.
    - EFetch: fetches detailed article records by PMID.

    Notes
    -----
    This script collects metadata and abstracts available from PubMed records.
    It does not download full-text papers.

    NCBI recommends identifying API tools with `tool` and `email` parameters.
    An API key can be provided through the `NCBI_API_KEY` environment variable.

    Example
    -------
    Run with default settings:

        python PubMed_Paper_Crawling.py

    Run with custom query and output path:

        python PubMed_Paper_Crawling.py ^
            --query "deep learning brain tumor MRI" ^
            --max-results 100 ^
            --batch-size 50 ^
            --output "Research_Paper_Snipper/PubMed/Paper/brain_tumor_dl_mri.csv" ^
            --email "your_email@example.com"
    """
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


# ----------------------------------------------------------------------------------------------------
# PubMed API Client
class PubMedClient:
    """
    PubMed Research Paper Collector
    ===============================

    A command-line Python utility for collecting biomedical research paper metadata
    from PubMed through the NCBI E-utilities API.

    This script performs the following workflow:

    1. Search PubMed by keyword using ESearch.
    2. Collect PubMed IDs (PMIDs) from the ESearch JSON response.
    3. Fetch detailed PubMed records by PMID using EFetch.
    4. Parse PubMed XML records into structured Python dictionaries.
    5. Convert the extracted records into a pandas DataFrame.
    6. Save the final dataset as a UTF-8 CSV file.

    Main use cases
    --------------
    - Building literature review datasets.
    - Collecting paper metadata for NLP preprocessing.
    - Exploring biomedical research trends.
    - Preparing portfolio projects related to biomedical text mining.
    - Creating biomedical research paper datasets for machine learning projects.

    Data source
    -----------
    NCBI E-utilities API:
    - ESearch: searches PubMed and returns PMIDs.
    - EFetch: fetches detailed article records by PMID.

    Notes
    -----
    This script collects metadata and abstracts available from PubMed records.
    It does not download full-text papers.

    NCBI recommends identifying API tools with `tool` and `email` parameters.
    An API key can be provided through the `NCBI_API_KEY` environment variable.

    Example
    -------
    Run with default settings:

        python PubMed_Paper_Crawling.py

    Run with custom query and output path:

        python PubMed_Paper_Crawling.py ^
            --query "deep learning brain tumor MRI" ^
            --max-results 100 ^
            --batch-size 50 ^
            --output "Research_Paper_Snipper/PubMed/Paper/brain_tumor_dl_mri.csv" ^
            --email "your_email@example.com"
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        email: Optional[str] = None,
        tool: str = NCBI_TOOL,
        sleep_seconds: float = DEFAULT_SLEEP_SECONDS
    ):
        """
        Initialize the PubMed API client.

        Parameters
        ----------
        api_key : Optional[str], default=None
            NCBI API key used to increase allowed request rate.

        email : Optional[str], default=None
            Contact email sent with API requests.

        tool : str, default=NCBI_TOOL
            Name of the software tool sent with API requests.

        sleep_seconds : float, default=DEFAULT_SLEEP_SECONDS
            Delay in seconds after each request.
        """
        self.api_key = api_key
        self.email = email
        self.tool = tool
        self.sleep_seconds = sleep_seconds
        self.session = create_session()

    def _base_params(self) -> Dict[str, str]:
        """
        Build common NCBI E-utilities query parameters.

        These parameters are shared by ESearch and EFetch requests. The `tool`
        parameter is always included. The `email` and `api_key` parameters are
        included only when available.

        Returns
        -------
        Dict[str, str]
            Dictionary of common API parameters.

        Examples
        --------
        >>> client = PubMedClient(email="your_email@example.com")
        >>> client._base_params()
        {'tool': 'pubmed_research_collector', 'email': 'your_email@example.com'}
        """
        params = {
            "tool": self.tool,
        }

        if self.email:
            params["email"] = self.email

        if self.api_key:
            params["api_key"] = self.api_key

        return params

    def _safe_get(self, endpoint: str, params: Dict[str, str]) -> requests.Response:
        """
        Send a GET request to an NCBI E-utilities endpoint safely.

        This method combines the base E-utilities URL with a specific endpoint,
        sends a GET request using the configured session, raises an exception
        for failed HTTP responses, and sleeps briefly after each request.

        Parameters
        ----------
        endpoint : str
            E-utilities endpoint filename, such as `"esearch.fcgi"` or
            `"efetch.fcgi"`.

        params : Dict[str, str]
            Query parameters sent with the request.

        Returns
        -------
        requests.Response
            The successful HTTP response object.

        Raises
        ------
        requests.HTTPError
            Raised when the server returns an unsuccessful HTTP status code.

        requests.RequestException
            Raised for network-related request failures.

        Examples
        --------
        >>> client = PubMedClient()
        >>> response = client._safe_get(
        ...     "esearch.fcgi",
        ...     {"db": "pubmed", "term": "brain tumor", "retmode": "json"}
        ... )
        """
        url = f"{BASE_URL}/{endpoint}"

        response = self.session.get(url, params=params, timeout=20)
        response.raise_for_status()

        time.sleep(self.sleep_seconds)

        return response

    def search_pmids(
        self,
        query: str,
        max_results: int = DEFAULT_MAX_RESULTS,
        sort: str = "relevance"
    ) -> List[str]:
        """
        Search PubMed and return a list of PubMed IDs.

        This method uses the NCBI ESearch endpoint to search PubMed by keyword.
        The ESearch response is requested in JSON format. PMIDs are extracted
        from `esearchresult.idlist`.

        Pagination
        ----------
        ESearch can return results in pages. This method uses:
        - `retstart`: the starting index of the current page.
        - `retmax`: the maximum number of records to return in one request.

        The method first requests page 0, then continues requesting additional
        pages until it reaches the smaller value between `max_results` and the
        total number of matched records.

        Parameters
        ----------
        query : str
            PubMed search query, for example `"brain tumor"` or
            `"deep learning brain tumor MRI"`.

        max_results : int, default=DEFAULT_MAX_RESULTS
            Maximum number of PMIDs to collect.

        sort : str, default="relevance"
            PubMed sorting strategy. Common values include `"relevance"` and
            `"pub date"`.

        Returns
        -------
        List[str]
            List of PMID strings.

        Raises
        ------
        requests.HTTPError
            Raised when an ESearch request fails.

        Key response fields
        -------------------
        data["esearchresult"]["count"]
            Total number of PubMed records matching the query.

        data["esearchresult"]["idlist"]
            PMID list returned for the current page.

        Examples
        --------
        >>> client = PubMedClient(email="your_email@example.com")
        >>> pmids = client.search_pmids("brain tumor", max_results=5)
        >>> print(pmids)
        ['12345678', '23456789', '34567890']
        """
        search_url = "esearch.fcgi"

        all_pmids = []
        retmax = min(max_results, 100)

        # First request: get total count and first page of IDs
        params = {
            **self._base_params(),
            "db": "pubmed",
            "term": query,
            "retmode": "json",
            "retmax": str(retmax),
            "retstart": "0",
            "sort": sort
        }

        print(f"🔎 [INFO] Searching PubMed query: {query}")

        response = self._safe_get(search_url, params)
        data = response.json()

        total_count = int(data["esearchresult"]["count"])
        first_ids = data["esearchresult"]["idlist"]

        all_pmids.extend(first_ids)

        print(f"💡 [INFO] Total matched records in PubMed: {total_count}")
        print(f"💡 [INFO] First batch PMIDs: {len(first_ids)}")

        # If max_results is larger than first page, continue pagination
        target_count = min(max_results, total_count)
        total_pages = math.ceil(target_count / retmax)

        for page in range(1, total_pages):
            retstart = page * retmax

            params["retstart"] = str(retstart)
            params["retmax"] = str(min(retmax, target_count - len(all_pmids)))

            print(f"🔎 [INFO] Fetching PMID page {page + 1}/{total_pages}...")

            response = self._safe_get(search_url, params)
            data = response.json()

            ids = data["esearchresult"]["idlist"]
            all_pmids.extend(ids)

            if len(all_pmids) >= target_count:
                break

        return all_pmids[:target_count]

    def fetch_articles_xml(self, pmids: List[str]) -> str:
        """
        Fetch detailed PubMed article records as XML by PMID list.

        This method uses the NCBI EFetch endpoint. PMIDs are joined into a
        comma-separated string and passed through the `id` parameter.

        Parameters
        ----------
        pmids : List[str]
            List of PMID strings. Example: `["12345678", "23456789"]`.

        Returns
        -------
        str
            Raw XML text returned by EFetch.

        Raises
        ------
        ValueError
            Raised when `pmids` is empty.

        requests.HTTPError
            Raised when the EFetch request fails.

        Examples
        --------
        >>> client = PubMedClient(email="your_email@example.com")
        >>> xml_text = client.fetch_articles_xml(["12345678", "23456789"])
        >>> print(xml_text[:100])
        """
        if not pmids:
            raise ValueError("⚠️ PMID list is empty. Cannot fetch article details.")

        fetch_url = "efetch.fcgi"

        params = {
            **self._base_params(),
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml"
        }

        response = self._safe_get(fetch_url, params)

        return response.text
    
# ----------------------------------------------------------------------------------------------------
# XML Parsing Helpers
def get_text(element: Optional[ET.Element]) -> Optional[str]:
    """
    Safely extract all text from an XML element.

    This helper uses `element.itertext()` instead of `element.text` so it can
    handle nested XML tags more reliably. If the element is missing or contains
    only whitespace, the function returns None.

    Parameters
    ----------
    element : Optional[ET.Element]
        XML element from which text should be extracted.

    Returns
    -------
    Optional[str]
        Cleaned text content, or None if no text is available.

    Examples
    --------
    >>> title = get_text(article.find(".//ArticleTitle"))
    """
    if element is None:
        return None

    text = "".join(element.itertext()).strip()

    return text if text else None


# ----------------------------------------------------------------------------------------------------
def get_article_id(article: ET.Element, id_type: str) -> Optional[str]:
    """
    Extract a specific article identifier from a PubMed XML article.

    PubMed records may contain multiple article identifiers, such as DOI, PMC,
    or PII. This function searches all `ArticleId` elements and returns the one
    whose `IdType` attribute matches `id_type`.

    Parameters
    ----------
    article : ET.Element
        XML element representing one `PubmedArticle`.

    id_type : str
        Identifier type to extract, such as `"doi"`, `"pmc"`, or `"pii"`.

    Returns
    -------
    Optional[str]
        Matching article identifier text, or None if not found.

    Examples
    --------
    >>> doi = get_article_id(article, "doi")
    >>> pmc_id = get_article_id(article, "pmc")
    """
    for article_id in article.findall(".//ArticleId"):
        if article_id.attrib.get("IdType") == id_type:
            return get_text(article_id)

    return None


# ----------------------------------------------------------------------------------------------------
def get_publication_year(article: ET.Element) -> Optional[str]:
    """
    Extract the publication year from a PubMed XML article.

    PubMed records can store publication dates in multiple locations. This
    function checks common locations in the following order:

    1. `.//JournalIssue/PubDate/Year`
    2. `.//JournalIssue/PubDate/MedlineDate`
    3. `.//ArticleDate/Year`

    If a MedlineDate is used, the function extracts the first four-digit year
    with a regular expression.

    Parameters
    ----------
    article : ET.Element
        XML element representing one `PubmedArticle`.

    Returns
    -------
    Optional[str]
        Publication year as a string, or None if no year is found.

    Examples
    --------
    >>> year = get_publication_year(article)
    >>> print(year)
    '2024'
    """
    year_elem = article.find(".//JournalIssue/PubDate/Year")

    if year_elem is not None and year_elem.text:
        return year_elem.text.strip()

    # Some records use MedlineDate instead of Year
    medline_date_elem = article.find(".//JournalIssue/PubDate/MedlineDate")
    medline_date = get_text(medline_date_elem)

    if medline_date:
        match = re.search(r"\d{4}", medline_date)
        if match:
            return match.group(0)

    # Fallback
    article_date_year = article.find(".//ArticleDate/Year")
    if article_date_year is not None and article_date_year.text:
        return article_date_year.text.strip()

    return None


# ----------------------------------------------------------------------------------------------------
def get_abstract(article: ET.Element) -> Optional[str]:
    """
    Extract and combine abstract text from a PubMed XML article.

    Some PubMed abstracts are stored as a single text block, while others are
    structured into sections such as BACKGROUND, METHODS, RESULTS, or
    CONCLUSIONS. This function preserves section labels when available and
    joins all abstract parts into one string.

    Parameters
    ----------
    article : ET.Element
        XML element representing one `PubmedArticle`.

    Returns
    -------
    Optional[str]
        Combined abstract text, or None if no abstract is available.

    Examples
    --------
    >>> abstract = get_abstract(article)
    """
    abstract_parts = []

    for abstract_text in article.findall(".//Abstract/AbstractText"):
        label = abstract_text.attrib.get("Label")
        text = get_text(abstract_text)

        if not text:
            continue

        if label:
            abstract_parts.append(f"{label}: {text}")
        else:
            abstract_parts.append(text)

    if not abstract_parts:
        return None

    return " ".join(abstract_parts)


# ----------------------------------------------------------------------------------------------------
def get_authors(article: ET.Element) -> Optional[str]:
    """
    Extract author names from a PubMed XML article.

    The function supports both individual authors and collective/group authors.
    Individual names are formatted as `"ForeName LastName"` when both fields
    are available.

    Parameters
    ----------
    article : ET.Element
        XML element representing one `PubmedArticle`.

    Returns
    -------
    Optional[str]
        Semicolon-separated author names, or None if no authors are found.

    Examples
    --------
    >>> authors = get_authors(article)
    >>> print(authors)
    'Jane Smith; John Chen'
    """
    authors = []

    for author in article.findall(".//AuthorList/Author"):
        last_name = get_text(author.find("LastName"))
        fore_name = get_text(author.find("ForeName"))
        collective_name = get_text(author.find("CollectiveName"))

        if collective_name:
            authors.append(collective_name)
        elif last_name and fore_name:
            authors.append(f"{fore_name} {last_name}")
        elif last_name:
            authors.append(last_name)

    return "; ".join(authors) if authors else None


# ----------------------------------------------------------------------------------------------------
def get_keywords(article: ET.Element) -> Optional[str]:
    """
    Extract author-provided keywords from a PubMed XML article.

    Parameters
    ----------
    article : ET.Element
        XML element representing one `PubmedArticle`.

    Returns
    -------
    Optional[str]
        Semicolon-separated keyword string, or None if no keywords are found.

    Examples
    --------
    >>> keywords = get_keywords(article)
    """
    keywords = []

    for keyword in article.findall(".//KeywordList/Keyword"):
        text = get_text(keyword)
        if text:
            keywords.append(text)

    return "; ".join(keywords) if keywords else None


# ----------------------------------------------------------------------------------------------------
def get_mesh_terms(article: ET.Element) -> Optional[str]:
    """
    Extract MeSH descriptor terms from a PubMed XML article.

    MeSH terms are controlled vocabulary terms assigned to biomedical articles.
    They are useful for topic analysis, metadata filtering, and biomedical NLP.

    Parameters
    ----------
    article : ET.Element
        XML element representing one `PubmedArticle`.

    Returns
    -------
    Optional[str]
        Semicolon-separated MeSH descriptor names, or None if unavailable.

    Examples
    --------
    >>> mesh_terms = get_mesh_terms(article)
    """
    mesh_terms = []

    for descriptor in article.findall(".//MeshHeading/DescriptorName"):
        text = get_text(descriptor)
        if text:
            mesh_terms.append(text)

    return "; ".join(mesh_terms) if mesh_terms else None


# ----------------------------------------------------------------------------------------------------
def get_publication_types(article: ET.Element) -> Optional[str]:
    """
    Extract publication type labels from a PubMed XML article.

    Publication types describe the article category, such as Journal Article,
    Review, Clinical Trial, Meta-Analysis, or Systematic Review.

    Parameters
    ----------
    article : ET.Element
        XML element representing one `PubmedArticle`.

    Returns
    -------
    Optional[str]
        Semicolon-separated publication type names, or None if unavailable.

    Examples
    --------
    >>> publication_types = get_publication_types(article)
    """
    publication_types = []

    for pub_type in article.findall(".//PublicationTypeList/PublicationType"):
        text = get_text(pub_type)
        if text:
            publication_types.append(text)

    return "; ".join(publication_types) if publication_types else None


# ----------------------------------------------------------------------------------------------------
def parse_pubmed_xml(xml_text: str) -> List[Dict[str, Optional[str]]]:
    """
    Parse PubMed XML text and extract structured article metadata.

    This function converts raw EFetch XML into a list of dictionaries. Each
    dictionary represents one PubMed article and contains identifiers, title,
    abstract, journal metadata, publication year, author names, keywords, MeSH
    terms, publication types, and useful URLs.

    Parameters
    ----------
    xml_text : str
        Raw XML string returned by the NCBI EFetch endpoint.

    Returns
    -------
    List[Dict[str, Optional[str]]]
        List of article metadata dictionaries.

    Output fields
    -------------
    pmid : Optional[str]
        PubMed ID.

    doi : Optional[str]
        Digital Object Identifier.

    pmc_id : Optional[str]
        PubMed Central ID, if available.

    title : Optional[str]
        Article title.

    abstract : Optional[str]
        Article abstract text.

    journal : Optional[str]
        Full journal title.

    journal_iso : Optional[str]
        ISO journal abbreviation.

    year : Optional[str]
        Publication year.

    language : Optional[str]
        Article language code.

    authors : Optional[str]
        Semicolon-separated author names.

    keywords : Optional[str]
        Semicolon-separated author keywords.

    mesh_terms : Optional[str]
        Semicolon-separated MeSH terms.

    publication_types : Optional[str]
        Semicolon-separated publication type labels.

    pubmed_url : Optional[str]
        PubMed article URL.

    doi_url : Optional[str]
        DOI resolver URL.

    Raises
    ------
    xml.etree.ElementTree.ParseError
        Raised if `xml_text` is not valid XML.

    Examples
    --------
    >>> papers = parse_pubmed_xml(xml_text)
    >>> print(papers[0]["title"])
    """
    root = ET.fromstring(xml_text)

    papers = []

    for article in root.findall(".//PubmedArticle"):
        pmid = get_text(article.find(".//MedlineCitation/PMID"))
        doi = get_article_id(article, "doi")
        pmc_id = get_article_id(article, "pmc")

        title = get_text(article.find(".//ArticleTitle"))
        abstract = get_abstract(article)

        journal = get_text(article.find(".//Journal/Title"))
        journal_iso = get_text(article.find(".//Journal/ISOAbbreviation"))

        year = get_publication_year(article)
        language = get_text(article.find(".//Language"))

        authors = get_authors(article)
        keywords = get_keywords(article)
        mesh_terms = get_mesh_terms(article)
        publication_types = get_publication_types(article)

        paper = {
            "pmid": pmid,
            "doi": doi,
            "pmc_id": pmc_id,
            "title": title,
            "abstract": abstract,
            "journal": journal,
            "journal_iso": journal_iso,
            "year": year,
            "language": language,
            "authors": authors,
            "keywords": keywords,
            "mesh_terms": mesh_terms,
            "publication_types": publication_types,
            "pubmed_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else None,
            "doi_url": f"https://doi.org/{doi}" if doi else None
        }

        papers.append(paper)

    return papers


# ----------------------------------------------------------------------------------------------------
# Data Collection Pipeline
def chunk_list(items: List[str], batch_size: int) -> List[List[str]]:
    """
    Split a list into smaller batches.

    This helper is used to divide a PMID list into smaller groups before
    sending EFetch requests. Batching keeps individual API requests manageable
    and makes progress messages easier to interpret.

    Parameters
    ----------
    items : List[str]
        Input list to split.

    batch_size : int
        Maximum number of items in each batch.

    Returns
    -------
    List[List[str]]
        List of smaller lists.

    Raises
    ------
    ValueError
        Raised when `batch_size` is less than or equal to zero.

    Examples
    --------
    >>> chunk_list(["1", "2", "3", "4", "5"], batch_size=2)
    [['1', '2'], ['3', '4'], ['5']]
    """
    return [
        items[i:i + batch_size]
        for i in range(0, len(items), batch_size)
    ]


# ----------------------------------------------------------------------------------------------------
def collect_pubmed_papers(
    query: str,
    max_results: int,
    batch_size: int,
    output_file: str,
    api_key: Optional[str] = None,
    email: Optional[str] = None
) -> pd.DataFrame:
    """
    Run the complete PubMed data collection pipeline.

    This function orchestrates the full workflow:

    1. Create a PubMed API client.
    2. Search PubMed and collect PMIDs.
    3. Split PMIDs into smaller batches.
    4. Fetch XML article records for each batch.
    5. Parse XML into structured article dictionaries.
    6. Build a pandas DataFrame.
    7. Remove duplicated PMIDs.
    8. Save the final dataset as a CSV file.

    Parameters
    ----------
    query : str
        PubMed search query.

    max_results : int
        Maximum number of papers to collect.

    batch_size : int
        Number of PMIDs to fetch per EFetch request.

    output_file : str
        Output CSV file path.

    api_key : Optional[str], default=None
        Optional NCBI API key.

    email : Optional[str], default=None
        Optional contact email sent to NCBI.

    Returns
    -------
    pd.DataFrame
        DataFrame containing collected PubMed article metadata.

    Raises
    ------
    ValueError
        Raised if input values are invalid.

    requests.HTTPError
        Raised if an API request fails.

    xml.etree.ElementTree.ParseError
        Raised if EFetch returns invalid XML.

    Examples
    --------
    >>> df = collect_pubmed_papers(
    ...     query="deep learning brain tumor MRI",
    ...     max_results=50,
    ...     batch_size=25,
    ...     output_file="data/brain_tumor_dl_mri.csv",
    ...     email="your_email@example.com",
    ... )
    >>> print(df.head())
    """
    client = PubMedClient(
        api_key=api_key,
        email=email,
        sleep_seconds=DEFAULT_SLEEP_SECONDS
    )

    pmids = client.search_pmids(query=query, max_results=max_results)

    print(f"💡 [INFO] Collected PMIDs: {len(pmids)}")

    all_papers = []

    pmid_batches = chunk_list(pmids, batch_size)

    for batch_index, pmid_batch in enumerate(pmid_batches, start=1):
        print(f"📜 [INFO] Fetching article batch {batch_index}/{len(pmid_batches)}...")
        print(f"📜 [INFO] Batch size: {len(pmid_batch)}")

        xml_text = client.fetch_articles_xml(pmid_batch)
        papers = parse_pubmed_xml(xml_text)

        print(f"📜 [INFO] Parsed papers from this batch: {len(papers)}")

        all_papers.extend(papers)

    df = pd.DataFrame(all_papers)

    # Remove duplicated papers if any
    if "pmid" in df.columns:
        df = df.drop_duplicates(subset=["pmid"])

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print(f"🎊 [SUCCESS] Saved {len(df)} papers to {output_file}")

    return df


# ----------------------------------------------------------------------------------------------------
# Command Line Interface
def parse_args():
    """
    Parse command-line arguments for the PubMed collector.

    The command-line interface allows users to change the search query,
    maximum result count, EFetch batch size, output CSV path, and contact email
    without modifying the source code.

    Returns
    -------
    argparse.Namespace
        Parsed command-line arguments with the following attributes:

        - query
        - max_results
        - batch_size
        - output
        - email

    Examples
    --------
    Show help message:

        python PubMed_Paper_Crawling.py --help

    Run with custom options:

        python PubMed_Paper_Crawling.py ^
            --query "deep learning brain tumor MRI" ^
            --max-results 100 ^
            --batch-size 50 ^
            --output "data/brain_tumor_dl_mri.csv" ^
            --email "your_email@example.com"
    """
    parser = argparse.ArgumentParser(
        description="Collect PubMed research papers by keyword."
    )

    parser.add_argument(
        "--query",
        type=str,
        default=DEFAULT_QUERY,
        help="Search query for PubMed."
    )

    parser.add_argument(
        "--max-results",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help="Maximum number of PubMed papers to collect."
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=DEFAULT_BATCH_SIZE,
        help="Number of PMIDs to fetch per EFetch request."
    )

    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_FILE,
        help="Output CSV file name."
    )

    parser.add_argument(
        "--email",
        type=str,
        default=NCBI_EMAIL,
        help="Your email for NCBI E-utilities identification."
    )

    return parser.parse_args()


# ----------------------------------------------------------------------------------------------------
def main():
    """
    Execute the PubMed research paper collection workflow.

    This is the main entry point of the script. It parses command-line
    arguments, prints a short configuration summary, runs the collection
    pipeline, and previews the first few rows of the resulting DataFrame.

    Returns
    -------
    None

    Examples
    --------
    Run the script directly:

        python PubMed_Paper_Crawling.py

    Run with a custom query:

        python PubMed_Paper_Crawling.py --query "brain tumor segmentation deep learning"
    """
    args = parse_args()

    print(f"\n{'='*80}\nPubMed Research Paper Collector\n{'='*80}")
    print(f"Query       : {args.query}")
    print(f"Max results : {args.max_results}")
    print(f"Batch size  : {args.batch_size}")
    print(f"Output file : {args.output}\n{'='*80}")

    df = collect_pubmed_papers(
        query=args.query,
        max_results=args.max_results,
        batch_size=args.batch_size,
        output_file=args.output,
        api_key=NCBI_API_KEY,
        email=args.email
    )

    print("\n👁️ Preview:")
    print(df.head())


# ----------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()

# python Research_Paper_Snipper/PubMed/PubMed_Paper_Crawling.py 
# --query "key word" --max-results "searching amount" --batch-size "batch size" --output "output file.csv" --email "email"
# ----------------------------------------------------------------------------------------------------