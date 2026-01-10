import requests, urllib.parse, asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

_browser = None
_playwright = None

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/118.0.5993.117 Safari/537.36"
    )
}

async def initBrowser():
    global _browser
    global _playwright
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)
    return _browser


async def closeBrowser():
    global _browser
    global _playwright

    if _browser is not None:
        await _browser.close()
        _browser = None
    if _playwright is not None:
        await _playwright.stop()
        _playwright = None


async def search(query):
    urls = await lookUp(query)
    results=[]
    for url in urls:
        results.append(await visitSite(url, False))
    await closeBrowser()
    
    output=""
    
    numb=0
    for result in results:
        numb+=1
        output += f'\nResult Number {numb}\nURL: {result["url"]}\n'
        try:
            output += f'Content: {result["content"]}\n'
        except:
            output += f'Error: {result["error"]}\n\n'
    
    
    
    return output




async def lookUp(query):
    """Perform a DuckDuckGo search and return a list of result URLs."""
    query_string = urllib.parse.quote_plus(query)
    url = f"https://duckduckgo.com/html/?q={query_string}"
    
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    links = []
    # DuckDuckGo search results links are in <a class="result__a" href="...">
    for a in soup.select("a.result__a"):
        href = a.get("href")
        if href:
            # Some links may be redirected through /l/?kh=-1&uddg=<encoded URL>
            if "uddg=" in href:
                href = urllib.parse.unquote(href.split("uddg=")[1])
            links.append(href)
    linksNew=[]

    for link in links:
        linksNew += [link.split("&rut=")[0]]
        

    return linksNew[:8]


async def visitSite(url, manageBrowser=True):
    browser = await initBrowser()
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=15000)


        text = await page.evaluate("""
() => {
    const walker = document.createTreeWalker(
        document.body,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: node =>
                node.parentElement &&
                !['SCRIPT','STYLE','NOSCRIPT','HEADER','FOOTER','NAV'].includes(
                    node.parentElement.tagName
                ) &&
                node.textContent.trim().length > 40
                    ? NodeFilter.FILTER_ACCEPT
                    : NodeFilter.FILTER_REJECT
        }
    );

    let out = [];
    while (walker.nextNode()) {
        out.push(walker.currentNode.textContent.trim());
    }
    return out.join("\\n");
}
""")


        result = {
            "url": url,
            "content": text
        }

    except Exception as e:
        result = {
            "url": url,
            "error": str(e)
        }
    finally:
        await page.close()
        if manageBrowser:
            await closeBrowser()

    return result

async def main():
    results = await search(input("Search: "))
    
    print(results)



    
if __name__ == "__main__":
    asyncio.run(main())

