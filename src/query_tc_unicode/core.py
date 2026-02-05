import re
import asyncio
from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions

async def get_character_attributes(char_or_uni):
    """
    Queries CNS11643 for attributes of a given character or Unicode hex string using Pydoll.
    
    Args:
        char_or_uni (str): A single character or a Unicode hex string (e.g., '6578' or '2A838').
        
    Returns:
        dict: A dictionary containing character attributes.
    """
    if len(char_or_uni) == 1:
        # It's a character, convert to hex
        uni_hex = f"{ord(char_or_uni):X}"
    else:
        # Assume it's already a hex string
        uni_hex = char_or_uni.upper().replace("U+", "").strip()

    url = f"https://www.cns11643.gov.tw/search.jsp?ID=12&UNI={uni_hex}"
    
    # Configure options
    options = ChromiumOptions()
    options.headless = True

    # Launch browser with options
    browser = Chrome(options=options)
    # browser.start() returns the initial Tab (page)
    page = await browser.start()
    
    try:
        await page.go_to(url)
        # Wait for some content to load. 
        # await page.wait_for_selector("footer") - wait_for_selector not available, use wait_until or find_or_wait_element
        await page.find_or_wait_element(by=None, value="footer", timeout=10) # Using find_or_wait implicitly via query might be easier but let's try explicit

        # Check for cnsCode figure which indicates detail page
        try:
             cns_code_element = await page.query("figure[cnsCode]", timeout=2, raise_exc=False)
        except Exception:
             cns_code_element = None
        
        if not cns_code_element:
            # Maybe it's a list page?
            # Try to find a link with wordView.jsp
            try:
                first_link = await page.query("a[href*='wordView.jsp']", raise_exc=False)
                if first_link:
                    await first_link.click()
                    await page.query("figure[cnsCode]", timeout=10)
            except Exception:
                pass # Proceed to scrape what we can or return empty

        results = {}
        results['unicode'] = f"U+{uni_hex}"

        # Get Description from meta tag
        try:
            meta_desc = await page.query("meta[name='Description']", raise_exc=False)
            if meta_desc:
                 content = await meta_desc.get_attribute("content")
                 if content:
                    results['description'] = content
                    parts = [p.strip() for p in content.split(',')]
                    if len(parts) > 0:
                        results['char'] = parts[0]
                    for part in parts:
                        if ':' in part:
                            key, value = part.split(':', 1)
                            results[key.strip()] = value.strip()
        except Exception:
            pass

        # Extract CNS Code
        try:
            cns_fig = await page.query("figure[cnsCode]", raise_exc=False)
            if cns_fig:
                cns_text = await cns_fig.text
                match = re.search(r'(\d+-[0-9A-F]+)', cns_text)
                if match:
                    results['cns'] = match.group(1)
        except Exception:
            pass
        
        # Fallback for CNS if not found in figure
        if 'cns' not in results:
             try:
                 title_element = await page.query("title", raise_exc=False)
                 if title_element:
                     title_text = await title_element.text
                     match = re.search(r'(\d+-[0-9A-F]+)', title_text)
                     if match:
                         results['cns'] = match.group(1)
             except Exception:
                 pass

        # Extract IDS
        try:
            # Need to find the div inside figure[ids]
            # pydoll query doesn't support nested query on page directly, but we can query element
            ids_fig = await page.query("figure[ids] div", raise_exc=False)
            if ids_fig:
                results['ids'] = (await ids_fig.text).strip()
        except Exception:
            pass

        # Extract Components
        try:
            comp_fig = await page.query("figure[component]", raise_exc=False)
            if comp_fig:
                results['components'] = (await comp_fig.text).strip()
        except Exception:
            pass

        # Extract Stroke Order
        try:
            stroke_fig = await page.query("figure[strokeOrder]", raise_exc=False)
            if stroke_fig:
                results['stroke_order'] = (await stroke_fig.text).strip()
        except Exception:
            pass

        return results

    finally:
        await browser.stop()