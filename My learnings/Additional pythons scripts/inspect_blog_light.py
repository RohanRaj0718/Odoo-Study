"""Inspect Infintor blog styles in light mode."""
import asyncio
from playwright.async_api import async_playwright

URLS = [
    "https://www.infintor.com/make-to-order-and-make-to-stock-odoo-19/",
    "https://www.infintor.com/manage-sales-orders-odoo-19-multi-warehouses/",
]

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(color_scheme="light")
        page = await context.new_page()

        for url in URLS:
            print(f"\n{'='*60}")
            print(f"URL: {url}")
            print('='*60)
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(3000)

            styles = await page.evaluate("""() => {
                const results = {};
                const contentArea = document.querySelector('.entry-content, .post-content, article, .blog-content, main');

                // H1
                const h1 = document.querySelector('h1');
                if (h1) {
                    const s = getComputedStyle(h1);
                    results.h1 = {
                        text: h1.textContent.trim().substring(0, 50),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        fontWeight: s.fontWeight,
                        color: s.color,
                    };
                }

                // H2
                const h2s = contentArea ? contentArea.querySelectorAll('h2') : document.querySelectorAll('h2');
                for (const h2 of h2s) {
                    const s = getComputedStyle(h2);
                    results.h2 = {
                        text: h2.textContent.trim().substring(0, 50),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        fontWeight: s.fontWeight,
                        color: s.color,
                    };
                    break;
                }

                // H3
                const h3s = contentArea ? contentArea.querySelectorAll('h3') : document.querySelectorAll('h3');
                for (const h3 of h3s) {
                    if (h3.closest('.sidebar, footer, .widget')) continue;
                    const s = getComputedStyle(h3);
                    results.h3 = {
                        text: h3.textContent.trim().substring(0, 50),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        fontWeight: s.fontWeight,
                        color: s.color,
                    };
                    break;
                }

                // Paragraphs
                const paras = contentArea ? contentArea.querySelectorAll('p') : document.querySelectorAll('p');
                for (const p of paras) {
                    if (p.textContent.trim().length > 50) {
                        const s = getComputedStyle(p);
                        results.paragraph = {
                            text: p.textContent.trim().substring(0, 60),
                            fontFamily: s.fontFamily,
                            fontSize: s.fontSize,
                            fontWeight: s.fontWeight,
                            color: s.color,
                        };
                        break;
                    }
                }

                // Bold
                const bolds = contentArea ? contentArea.querySelectorAll('strong, b') : document.querySelectorAll('strong, b');
                for (const b of bolds) {
                    if (b.textContent.trim().length > 3 && !b.closest('h1, h2, h3')) {
                        const s = getComputedStyle(b);
                        results.boldInParagraph = {
                            text: b.textContent.trim().substring(0, 50),
                            fontFamily: s.fontFamily,
                            fontSize: s.fontSize,
                            fontWeight: s.fontWeight,
                            color: s.color,
                        };
                        break;
                    }
                }

                // Author
                // Look for the byline text
                const allEls = document.querySelectorAll('*');
                for (const el of allEls) {
                    const txt = el.textContent.trim();
                    if ((txt.includes('Aishwarya') || txt.includes('Arun')) && txt.length < 80 && el.children.length === 0) {
                        const s = getComputedStyle(el);
                        results.authorByline = {
                            text: txt.substring(0, 50),
                            fontFamily: s.fontFamily,
                            fontSize: s.fontSize,
                            fontWeight: s.fontWeight,
                            color: s.color,
                        };
                        break;
                    }
                }

                // List items
                const lis = contentArea ? contentArea.querySelectorAll('li') : [];
                for (const li of lis) {
                    if (li.textContent.trim().length > 20) {
                        const s = getComputedStyle(li);
                        results.listItem = {
                            text: li.textContent.trim().substring(0, 60),
                            fontFamily: s.fontFamily,
                            fontSize: s.fontSize,
                            fontWeight: s.fontWeight,
                            color: s.color,
                        };
                        break;
                    }
                }

                // Table header & cell
                const ths = contentArea ? contentArea.querySelectorAll('th') : [];
                if (ths.length > 0) {
                    const s = getComputedStyle(ths[0]);
                    results.tableHeader = {
                        text: ths[0].textContent.trim().substring(0, 30),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        fontWeight: s.fontWeight,
                        color: s.color,
                        backgroundColor: s.backgroundColor,
                    };
                }
                const tds = contentArea ? contentArea.querySelectorAll('td') : [];
                if (tds.length > 0) {
                    const s = getComputedStyle(tds[0]);
                    results.tableCell = {
                        text: tds[0].textContent.trim().substring(0, 30),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        color: s.color,
                        backgroundColor: s.backgroundColor,
                        borderColor: s.borderColor,
                    };
                }

                // Background of body
                results.pageBackground = {
                    bodyBg: getComputedStyle(document.body).backgroundColor,
                };

                return results;
            }""")

            for element, props in styles.items():
                print(f"\n  {element.upper()}:")
                for k, v in props.items():
                    print(f"    {k}: {v}")

        await browser.close()

asyncio.run(main())
