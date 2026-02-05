import re
import asyncio
from pydoll.browser import Chrome
from pydoll.browser.options import ChromiumOptions

async def get_character_attributes(char_or_uni):
    """
    Queries CNS11643 for attributes of a given character or Unicode hex string using Pydoll.
    """
    if len(char_or_uni) == 1:
        uni_hex = f"{ord(char_or_uni):X}"
    else:
        uni_hex = char_or_uni.upper().replace("U+", "").strip()

    url = f"https://www.cns11643.gov.tw/search.jsp?ID=12&UNI={uni_hex}"
    
    options = ChromiumOptions()
    options.headless = True
    browser = Chrome(options=options)
    page = await browser.start()
    
    try:
        await page.go_to(url)
        await page.find_or_wait_element(by=None, value="footer", timeout=10)

        try:
             cns_code_element = await page.query("figure[cnsCode]", timeout=2, raise_exc=False)
        except Exception:
             cns_code_element = None
        
        if not cns_code_element:
            try:
                first_link = await page.query("a[href*='wordView.jsp']", raise_exc=False)
                if first_link:
                    await first_link.click()
                    await page.query("figure[cnsCode]", timeout=10)
            except Exception:
                pass

        results = {}
        results['unicode'] = f"U+{uni_hex}"

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

        try:
            cns_fig = await page.query("figure[cnsCode]", raise_exc=False)
            if cns_fig:
                cns_text = await cns_fig.text
                match = re.search(r'(\d+-[0-9A-F]+)', cns_text)
                if match:
                    results['cns'] = match.group(1)
        except Exception:
            pass
        
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

        try:
            ids_fig = await page.query("figure[ids] div", raise_exc=False)
            if ids_fig:
                results['ids'] = (await ids_fig.text).strip()
        except Exception:
            pass

        try:
            comp_fig = await page.query("figure[component]", raise_exc=False)
            if comp_fig:
                results['components'] = (await comp_fig.text).strip()
        except Exception:
            pass

        try:
            stroke_fig = await page.query("figure[strokeOrder]", raise_exc=False)
            if stroke_fig:
                results['stroke_order'] = (await stroke_fig.text).strip()
        except Exception:
            pass

        return results

    finally:
        await browser.stop()

async def get_character_meaning(char):
    """
    Fetches the meaning of a character from Zdic (zdic.net).
    """
    url = f"https://www.zdic.net/hant/{char}"
    
    options = ChromiumOptions()
    options.headless = True
    browser = Chrome(options=options)
    page = await browser.start()
    
    try:
        await page.go_to(url, timeout=20)
        
        definition = await page.execute_script(
            """
            let containers = document.querySelectorAll('.z_it, .shiyi, .tab-page, .content, #z_i_nr');
            for (let el of containers) {
                let text = el.innerText.trim();
                if (text.length > 20) return text;
            }
            return document.body.innerText;
            """,
            return_by_value=True
        )
        
        text = definition.get('result', {}).get('result', {}).get('value')
        if not text:
            return "Meaning not found."

        final_meaning = ""
        # Process the text to find the basic explanation
        if '基本解釋' in text:
            # Look for character followed by 基本解釋
            pattern = re.escape(char) + r'\s+基本解釋'
            match = re.search(pattern, text)
            if match:
                start_index = match.end()
                content = text[start_index:]
                # Cut off at next section
                for marker in ['詳細解釋', '國語辭典', '康熙字典', '說文解字', '【漢典】']:
                    if marker in content:
                        content = content.split(marker)[0]
                final_meaning = content.strip()
        
        if not final_meaning:
            # Fallback snippet
            char_idx = text.find(char)
            if char_idx != -1:
                final_meaning = text[char_idx:char_idx+300].strip()
            else:
                final_meaning = text[:300].strip()

        # Clean up: remove "●", the character itself, and redundant whitespace
        final_meaning = final_meaning.replace('●', '').strip()
        # Remove the character if it's at the very beginning (header style)
        if final_meaning.startswith(char):
            final_meaning = final_meaning[len(char):].strip()
            
        return final_meaning

    finally:
        await browser.stop()
