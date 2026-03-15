"""Inspect font, color, size of Infintor blog pages."""
import asyncio
from playwright.async_api import async_playwright

URLS = [
    "https://www.infintor.com/make-to-order-and-make-to-stock-odoo-19/",
    "https://www.infintor.com/manage-sales-orders-odoo-19-multi-warehouses/",
]

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()

        for url in URLS:
            print(f"\n{'='*60}")
            print(f"URL: {url}")
            print('='*60)
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(2000)

            # Extract computed styles for key elements
            styles = await page.evaluate("""() => {
                const results = {};
                
                // Blog title (h1)
                const h1 = document.querySelector('h1');
                if (h1) {
                    const s = getComputedStyle(h1);
                    results.h1 = {
                        text: h1.textContent.trim().substring(0, 60),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        fontWeight: s.fontWeight,
                        color: s.color,
                        lineHeight: s.lineHeight,
                        letterSpacing: s.letterSpacing,
                    };
                }

                // H2 headings
                const h2s = document.querySelectorAll('h2');
                if (h2s.length > 0) {
                    const s = getComputedStyle(h2s[0]);
                    results.h2 = {
                        text: h2s[0].textContent.trim().substring(0, 60),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        fontWeight: s.fontWeight,
                        color: s.color,
                        lineHeight: s.lineHeight,
                    };
                }

                // H3 headings
                const h3s = document.querySelectorAll('h3');
                for (const h3 of h3s) {
                    // Skip sidebar/footer h3s
                    if (h3.closest('.sidebar, footer, .widget')) continue;
                    const s = getComputedStyle(h3);
                    results.h3 = {
                        text: h3.textContent.trim().substring(0, 60),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        fontWeight: s.fontWeight,
                        color: s.color,
                    };
                    break;
                }
                
                // H5 headings (used in credit blog)
                const h5s = document.querySelectorAll('h5');
                if (h5s.length > 0) {
                    const s = getComputedStyle(h5s[0]);
                    results.h5 = {
                        text: h5s[0].textContent.trim().substring(0, 60),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        fontWeight: s.fontWeight,
                        color: s.color,
                    };
                }

                // Body paragraphs (inside main content)
                const contentArea = document.querySelector('.entry-content, .post-content, article, .blog-content, main');
                const paras = contentArea ? contentArea.querySelectorAll('p') : document.querySelectorAll('p');
                for (const p of paras) {
                    if (p.textContent.trim().length > 50) {
                        const s = getComputedStyle(p);
                        results.paragraph = {
                            text: p.textContent.trim().substring(0, 80),
                            fontFamily: s.fontFamily,
                            fontSize: s.fontSize,
                            fontWeight: s.fontWeight,
                            color: s.color,
                            lineHeight: s.lineHeight,
                        };
                        break;
                    }
                }

                // Bold text inside paragraphs
                const bolds = contentArea ? contentArea.querySelectorAll('strong, b') : document.querySelectorAll('strong, b');
                for (const b of bolds) {
                    if (b.textContent.trim().length > 3) {
                        const s = getComputedStyle(b);
                        results.bold = {
                            text: b.textContent.trim().substring(0, 60),
                            fontFamily: s.fontFamily,
                            fontSize: s.fontSize,
                            fontWeight: s.fontWeight,
                            color: s.color,
                        };
                        break;
                    }
                }

                // List items
                const lis = contentArea ? contentArea.querySelectorAll('li') : document.querySelectorAll('li');
                for (const li of lis) {
                    if (li.textContent.trim().length > 20 && !li.closest('nav, .sidebar, footer, .widget')) {
                        const s = getComputedStyle(li);
                        results.listItem = {
                            text: li.textContent.trim().substring(0, 80),
                            fontFamily: s.fontFamily,
                            fontSize: s.fontSize,
                            fontWeight: s.fontWeight,
                            color: s.color,
                            lineHeight: s.lineHeight,
                        };
                        break;
                    }
                }

                // Author/date line
                const authorEls = document.querySelectorAll('.author, .post-meta, .entry-meta, .blog-meta, time');
                for (const el of authorEls) {
                    if (el.textContent.trim().length > 5) {
                        const s = getComputedStyle(el);
                        results.authorMeta = {
                            text: el.textContent.trim().substring(0, 60),
                            fontFamily: s.fontFamily,
                            fontSize: s.fontSize,
                            color: s.color,
                        };
                        break;
                    }
                }

                // Table cells (if any)
                const tds = contentArea ? contentArea.querySelectorAll('td') : [];
                if (tds.length > 0) {
                    const s = getComputedStyle(tds[0]);
                    results.tableCell = {
                        text: tds[0].textContent.trim().substring(0, 40),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        color: s.color,
                        borderColor: s.borderColor,
                    };
                }

                // Table headers
                const ths = contentArea ? contentArea.querySelectorAll('th') : [];
                if (ths.length > 0) {
                    const s = getComputedStyle(ths[0]);
                    results.tableHeader = {
                        text: ths[0].textContent.trim().substring(0, 40),
                        fontFamily: s.fontFamily,
                        fontSize: s.fontSize,
                        fontWeight: s.fontWeight,
                        color: s.color,
                        backgroundColor: s.backgroundColor,
                    };
                }

                // CTA / call-to-action section
                const ctas = document.querySelectorAll('.cta, .call-to-action, blockquote');
                for (const cta of ctas) {
                    if (cta.textContent.trim().length > 10) {
                        const s = getComputedStyle(cta);
                        results.cta = {
                            text: cta.textContent.trim().substring(0, 80),
                            fontFamily: s.fontFamily,
                            fontSize: s.fontSize,
                            color: s.color,
                            backgroundColor: s.backgroundColor,
                        };
                        break;
                    }
                }

                return results;
            }""")

            for element, props in styles.items():
                print(f"\n  {element.upper()}:")
                for k, v in props.items():
                    print(f"    {k}: {v}")

        await browser.close()

asyncio.run(main())
