"""Debug script to understand IT Jobs Watch HTML structure."""

import requests
from bs4 import BeautifulSoup

# URL to debug
url = "https://www.itjobswatch.co.uk/default.aspx?q=&ql=&ll=London&id=0&p=6&e=0&sortby=5&orderby=0"

# Headers
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"Fetching: {url}")
response = requests.get(url, headers=headers)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Try to find tables
    tables = soup.find_all('table')
    print(f"\nFound {len(tables)} tables")
    
    # Look for results table
    for i, table in enumerate(tables):
        print(f"\nTable {i}:")
        # Check class or id
        print(f"  Class: {table.get('class')}")
        print(f"  ID: {table.get('id')}")
        
        # Get first few rows
        rows = table.find_all('tr')[:3]
        for j, row in enumerate(rows):
            print(f"  Row {j}:")
            cells = row.find_all(['td', 'th'])
            for k, cell in enumerate(cells):
                text = cell.text.strip()[:50]
                print(f"    Cell {k}: {text}")
    
    # Look for any div with results
    print("\n\nLooking for result divs...")
    
    # Try finding by class names that might contain results
    for class_name in ['results', 'result', 'listing', 'job', 'skill']:
        elements = soup.find_all(class_=lambda x: x and class_name in x.lower() if isinstance(x, str) else False)
        if elements:
            print(f"\nFound {len(elements)} elements with class containing '{class_name}'")
            # Show first element structure
            if elements:
                elem = elements[0]
                print(f"  Tag: {elem.name}")
                print(f"  Classes: {elem.get('class')}")
                print(f"  Text preview: {elem.text.strip()[:100]}...")
    
    # Save full HTML for inspection
    with open('debug_output.html', 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))
    print("\nFull HTML saved to debug_output.html")