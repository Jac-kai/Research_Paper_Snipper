"""
Package / Syntax / Parameter Notes
====================================================

1. requests
----------------------------------------------------
Purpose:
    Send HTTP requests to web APIs.

Common syntax:
    response = requests.get(url, params=params, timeout=20)

Important parameters:
    url:
        The API endpoint URL.
    params:
        A dictionary of query string parameters.
        Example:
            {"db": "pubmed", "term": query, "retmode": "json"}
    timeout:
        Maximum waiting time for the server response.
    response.json():
        Convert a JSON API response into a Python dictionary.
    response.text:
        Get the raw text response, useful for XML or HTML.
    response.raise_for_status():
        Raise an error if the HTTP status code means failure.

2. requests.Session
----------------------------------------------------
Purpose:
    Reuse HTTP connections and shared settings across many requests.

Common syntax:
    session = requests.Session()
    response = session.get(url, params=params, timeout=20)

Why use it:
    Better performance and cleaner API client design when calling
    the same server many times.

3. HTTPAdapter
----------------------------------------------------
Purpose:
    Customize how a Session handles HTTP/HTTPS requests.

Common syntax:
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

Important parameters:
    max_retries:
        A Retry object that controls automatic retry behavior.

When to use:
    Use HTTPAdapter when you call an API many times and want retry logic.

4. urllib3.util.retry.Retry
----------------------------------------------------
Purpose:
    Define automatic retry rules for failed HTTP requests.

Common syntax:
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )

Important parameters:
    total:
        Maximum number of retry attempts.
    backoff_factor:
        Waiting time multiplier between retry attempts.
    status_forcelist:
        HTTP status codes that should trigger a retry.
        429 = Too Many Requests
        500 = Internal Server Error
        502 = Bad Gateway
        503 = Service Unavailable
        504 = Gateway Timeout
    allowed_methods:
        HTTP methods allowed to retry.
        Example:
            ["GET"] means only GET requests can be retried.

5. xml.etree.ElementTree as ET
----------------------------------------------------
Purpose:
    Parse XML text into a tree structure and extract elements.

Common syntax:
    root = ET.fromstring(xml_text)
    article_nodes = root.findall(".//PubmedArticle")
    title = article.find(".//ArticleTitle")

Important methods:
    ET.fromstring(xml_text):
        Parse an XML string into the root Element.
    element.find(path):
        Find the first matching child element.
    element.findall(path):
        Find all matching child elements.
    element.itertext():
        Extract all text inside an element, including nested text.
    element.attrib:
        Get XML attributes as a dictionary.
        Example:
            article_id.attrib.get("IdType")

XPath-like syntax:
    ".":
        Current element.
    "//":
        Search all descendant levels.
    ".//ArticleId":
        Find all ArticleId elements under the current element.

6. argparse
----------------------------------------------------
Purpose:
    Read command-line arguments.

Common syntax:
    parser = argparse.ArgumentParser(description="...")
    parser.add_argument("--query", type=str, default="deep learning")
    args = parser.parse_args()

Important parameters:
    "--query":
        Command-line option name.
    type:
        Convert input into a Python type.
    default:
        Value used when the user does not provide this argument.
    help:
        Explanation shown in command-line help.

7. PubMed E-utilities Parameters
----------------------------------------------------
Purpose:
    Control what PubMed API searches or fetches.

Common ESearch parameters:
    db:
        Target database. Example: "pubmed"
    term:
        Search keyword or query.
    retmode:
        Response format. Example: "json"
    retmax:
        Number of records to return in this request.
    retstart:
        Starting index for pagination.
    sort:
        Sorting method. Example: "relevance"

Common EFetch parameters:
    db:
        Target database. Example: "pubmed"
    id:
        Comma-separated PMID list.
    retmode:
        Response format. Example: "xml"

Pagination idea:
    First request:
        retstart = 0
        retmax = 100

    Second request:
        retstart = 100
        retmax = 100

    Third request:
        retstart = 200
        retmax = remaining_count
"""