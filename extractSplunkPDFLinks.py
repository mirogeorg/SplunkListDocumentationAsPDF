import requests
from bs4 import BeautifulSoup
import re
import sys

# Regex to find links matching the documentation structure
manual_link_regex = re.compile(r'^/Documentation/Splunk/([\d.]+)/([^/]+)/(.+)$')

# Target URL for the specific Splunk version
target_url = 'https://docs.splunk.com/Documentation/Splunk/9.1.4'
extracted_links = []

print(f"Attempting to fetch and parse: {target_url}")

try:
    response = requests.get(target_url, timeout=30, headers={'User-Agent': 'Link Extraction Script'})
    response.raise_for_status() # Check if the request was successful

    page = BeautifulSoup(response.text, 'html.parser')

    # Find all anchor (<a>) tags with an href attribute
    all_links = page.find_all('a', href=True)

    print(f"Found {len(all_links)} total links. Filtering for documentation manual links...")

    for link in all_links:
        href = link['href']
        match = manual_link_regex.match(href)
        if match:
            # Extract parts needed for the PDF URL construction
            version, section, docname = match.groups()
            # Construct the original href (which is what we want to list)
            full_href = f"https://docs.splunk.com{href}" # Prepend domain if needed, though original script just used relative path
            
            # Store the matched relative href and the extracted parts
            extracted_links.append({
                "relative_href": href,
                "version": version,
                "section": section,
                "docname": docname,
                "pdf_url_pattern": f"https://docs.splunk.com/index.php?title=Documentation:Splunk:{section}:{docname}:{version}&action=pdfbook"

            })
            print(f"  -> Matched: {href} (v={version}, s={section}, d={docname})")


except requests.exceptions.RequestException as e:
    print(f"Error fetching URL: {e}", file=sys.stderr)
except ImportError:
    print("Error: Please install 'requests' and 'beautifulsoup4'. `pip install requests beautifulsoup4`", file=sys.stderr)
except Exception as e:
    print(f"An error occurred during parsing: {e}", file=sys.stderr)

# --- Output the results ---
if not extracted_links:
    print("\nNo links matching the required pattern were found.")
    print("The website structure might have changed, or the target page doesn't contain such links.")
else:
    print(f"\n--- Extracted Relative Links Matching Pattern ---")
    unique_hrefs = sorted(list(set(link['relative_href'] for link in extracted_links)))
    for href in unique_hrefs:
         print(href)

    print(f"\n--- Corresponding PDF URL Patterns ---")
    unique_pdf_urls = sorted(list(set(link['pdf_url_pattern'] for link in extracted_links)))
    for url in unique_pdf_urls:
         print(url)
