# ----------------------------------------------------------------------------------------------------
"""
NCBI PubMed E-utilities API Notes
====================================================================================================

| Category | Item / Parameter | Used In | Required | Meaning | Example In This Script |
|---|---|---|---|---|---|
| Base URL | BASE_URL | ESearch / EFetch | Yes | Root URL of the NCBI E-utilities API. | https://eutils.ncbi.nlm.nih.gov/entrez/eutils |
| API Tool | ESearch | search_pmids() | Yes | Searches PubMed by keyword and returns PubMed IDs (PMIDs). | esearch.fcgi |
| API Tool | EFetch | fetch_articles_xml() | Yes | Fetches detailed PubMed article records by PMID. | efetch.fcgi |
| Database | db | ESearch / EFetch | Yes | Target NCBI database. For PubMed papers, use "pubmed". | "db": "pubmed" |
| Search Query | term | ESearch | Yes | Keyword or search expression used to search PubMed. | "term": query |
| Article IDs | id | EFetch | Yes | Comma-separated PMID list used to fetch article details. | "id": ",".join(pmids) |
| Response Format | retmode | ESearch / EFetch | Yes | Defines the API response format. JSON is useful for searching IDs; XML is useful for article metadata. | ESearch: "json", EFetch: "xml" |
| Page Size | retmax | ESearch | Optional | Maximum number of PMIDs returned in one request. Used for pagination. | "retmax": str(retmax) |
| Start Index | retstart | ESearch | Optional | Starting index of the current result page. Used to fetch the next page of PMIDs. | "retstart": "0", "100", "200" |
| Sort Method | sort | ESearch | Optional | Sorting strategy for PubMed search results. | "sort": "relevance" |
| Tool Name | tool | ESearch / EFetch | Recommended | Application/tool name sent to NCBI for identification. | "tool": self.tool |
| Email | email | ESearch / EFetch | Recommended | Contact email sent to NCBI for identification. | "email": self.email |
| API Key | api_key | ESearch / EFetch | Optional | NCBI API key. Increases allowed request rate. Usually stored in an environment variable. | os.getenv("NCBI_API_KEY") |
| PMID | pmid | ESearch result / XML parser | Yes | PubMed ID. A unique identifier for each PubMed article. | data["esearchresult"]["idlist"] |
| DOI | doi | XML parser | Optional | Digital Object Identifier. A permanent academic publication identifier. Not every paper has one. | ArticleId IdType="doi" |
| PMC ID | pmc_id | XML parser | Optional | PubMed Central ID. Indicates the article may have a PMC full-text record. | ArticleId IdType="pmc" |
| Total Count | count | ESearch result | Yes | Total number of PubMed records matching the query. | data["esearchresult"]["count"] |
| ID List | idlist | ESearch result | Yes | PMID list returned by the current ESearch request. | data["esearchresult"]["idlist"] |
| Pagination Target | target_count | search_pmids() | Internal | The actual number of PMIDs to collect. It is the smaller value between max_results and total_count. | min(max_results, total_count) |
| Total Pages | total_pages | search_pmids() | Internal | Number of ESearch pages needed to collect target_count PMIDs. | math.ceil(target_count / retmax) |
| Batch Size | batch_size | collect_pubmed_papers() | Internal | Number of PMIDs sent to EFetch per request. | DEFAULT_BATCH_SIZE = 50 |
| Chunk List | chunk_list() | collect_pubmed_papers() | Internal | Splits a long PMID list into smaller PMID batches before calling EFetch. | chunk_list(pmids, batch_size) |
| Request Delay | sleep_seconds | _safe_get() | Recommended | Delay after each request to avoid sending API requests too quickly. | DEFAULT_SLEEP_SECONDS = 0.4 |
| HTTP Method | GET | _safe_get() | Yes | This script sends API requests using HTTP GET. | self.session.get(...) |
| Retry Methods | allowed_methods | create_session() | Optional | Defines which HTTP methods can be retried after temporary failures. | allowed_methods=["GET"] |
| Retry Status Codes | status_forcelist | create_session() | Optional | HTTP status codes that should trigger retry behavior. | [429, 500, 502, 503, 504] |
| Retry Count | total | create_session() | Optional | Maximum number of retry attempts. | total=3 |
| Backoff Factor | backoff_factor | create_session() | Optional | Controls waiting time between retry attempts. | backoff_factor=1 |
| HTTP 429 | Too Many Requests | Retry logic | Optional | Usually means the API is being called too frequently. | status_forcelist includes 429 |
| HTTP 500 | Internal Server Error | Retry logic | Optional | Temporary server-side error. | status_forcelist includes 500 |
| HTTP 502 | Bad Gateway | Retry logic | Optional | Temporary gateway/server communication error. | status_forcelist includes 502 |
| HTTP 503 | Service Unavailable | Retry logic | Optional | Server is temporarily unavailable. | status_forcelist includes 503 |
| HTTP 504 | Gateway Timeout | Retry logic | Optional | Server timeout error. | status_forcelist includes 504 |
| XML Parser | ElementTree | parse_pubmed_xml() | Yes | Parses PubMed XML text into XML elements. | ET.fromstring(xml_text) |
| XML Search | .// | XML parser helpers | Yes | Searches all descendant levels under the current XML element. Similar to simplified XPath. | article.findall(".//ArticleId") |
| Text Extraction | itertext() | get_text() | Yes | Extracts text from an XML element, including nested text. | "".join(element.itertext()).strip() |
| Output Format | CSV | collect_pubmed_papers() | Yes | Final structured dataset format. | df.to_csv(output_file, index=False, encoding="utf-8-sig") |

Workflow Summary
----------------------------------------------------------------------------------------------------
1. ESearch searches PubMed with `term=query`.
2. ESearch returns JSON data containing `count` and `idlist`.
3. `idlist` provides PMIDs.
4. PMIDs are stored in `all_pmids`.
5. `chunk_list()` splits PMIDs into smaller batches.
6. EFetch receives each PMID batch through the `id` parameter.
7. EFetch returns XML article records.
8. ElementTree parses the XML.
9. Helper functions extract title, abstract, DOI, journal, year, authors, keywords, MeSH terms, etc.
10. Parsed records are converted into a pandas DataFrame.
11. The final DataFrame is saved as a CSV file.

Important Rule
----------------------------------------------------------------------------------------------------
ESearch is used to get PMIDs.
EFetch is used to get detailed article data from those PMIDs.

Rate Limit Note
----------------------------------------------------------------------------------------------------
Without an NCBI API key, keep requests below about 3 requests per second.
This script uses DEFAULT_SLEEP_SECONDS = 0.4, which is about 2.5 requests per second.

With an NCBI API key, the allowed request rate can be higher, but safe delay is still recommended.
"""
# ----------------------------------------------------------------------------------------------------