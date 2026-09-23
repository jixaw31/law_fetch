from playwright.async_api import async_playwright
import json
import asyncio

from .preprocess_law import parse_law


URLS = [
    ("madani", "https://qavanin.ir/Law/TreeText/?IDS=12021850837713548188"),
    ("tejarat", "https://qavanin.ir/Law/TreeText/?IDS=12145533825531226090"),
    ("mojazat_eslami", "https://qavanin.ir/Law/TreeText/?IDS=4693937366938194803"),
    ("ghanon_ayeen_dadrasi_madani", "https://qavanin.ir/Law/TreeText/?IDS=3143604737427044382"),
    ("ghanon_divan_edalat_edari", "https://qavanin.ir/Law/TreeText/?IDS=13973452648109452691"),
    ("ghanon_jarayem_rayanei", "https://qavanin.ir/Law/TreeText/?IDS=16280957826877252349"),
    ("ghanon_tejarat_electronic", "https://qavanin.ir/Law/TreeText/?IDS=16288520601852272206"),
    ("ghanon_mobareze_ba_ghachagh_va_arz", "https://qavanin.ir/Law/TreeText/?IDS=16530676955845194239"),
    ("ghanon_kar", "https://qavanin.ir/Law/TreeText/?IDS=3983654531606411392"),
    ("ghanon_ayeen_dadrasi_keyfari", "https://qavanin.ir/Law/TreeText/?IDS=2433638803151753757"),
    ("ghan_maliat_bar_arzesh_afzoode", "https://qavanin.ir/Law/TreeText/?IDS=17874811672232780652"),
    ("ghanon_hemayat_khanevade", "https://qavanin.ir/Law/TreeText/?IDS=5917848193987091276"),
    ("ghanon_assasi", "https://qavanin.ir/Law/TreeText/?IDS=6623702055317218729"),
]


# ---------------------------------------------------------
# Timeouts / waiting configuration
# ---------------------------------------------------------

NAVIGATION_TIMEOUT = 120_000    # 2 minutes
LAW_PAGE_TIMEOUT = 300_000      # 5 minutes
BODY_TIMEOUT = 240_000          # 2 minutes
POLL_INTERVAL = 2_000           # check every 2 seconds


def is_server_error(body: str) -> bool:
    error_messages = [
        "خطای ۵۰۴",
        "خطای 503",
        "خطای 502",
        "Gateway Timeout",
        "Gateway Error",
        "Service Unavailable",
        "سرور وب‌سایت به طور موقت از دسترس خارج شده است",
    ]

    return any(message in body for message in error_messages)

async def main():

    for name, url in URLS:

        print("\n" + "=" * 60)
        print(f"Processing: {name}")
        print(f"URL: {url}")

        p = None
        browser = None
        page = None

        try:
            # -------------------------------------------------
            # Start Playwright
            # -------------------------------------------------

            p = await async_playwright().start()

            browser = await p.chromium.launch(
                channel="chrome",
                headless=False,
            )

            page = await browser.new_page()

            # -------------------------------------------------
            # Initial navigation
            # -------------------------------------------------

            print("Opening page...")

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=NAVIGATION_TIMEOUT,
            )

            # -------------------------------------------------
            # Wait for the actual law page
            # -------------------------------------------------

            print("Waiting for actual law page...")

            body = ""

            for elapsed in range(
                0,
                LAW_PAGE_TIMEOUT,
                POLL_INTERVAL,
            ):

                body = await page.locator("body").inner_text(
                    timeout=BODY_TIMEOUT
                )

                elapsed_seconds = elapsed // 1000

                print(
                    f"Waiting... "
                    f"{elapsed_seconds}s / "
                    f"{LAW_PAGE_TIMEOUT // 1000}s "
                    f"| body length: {len(body)}"
                )

                # -------------------------------------------------
                # Immediately abandon temporary server error pages
                # -------------------------------------------------

                if is_server_error(body):
                    raise RuntimeError(
                        f"Qavanin server error detected after "
                        f"{elapsed_seconds}s"
                    )

                # -------------------------------------------------
                # Detect actual law page
                # -------------------------------------------------
                #
                # The anti-bot/interstitial page is very short.
                # A real law page should contain:
                #
                #   - substantial text
                #   - "ماده"
                #
                # This avoids depending on the exact Unicode
                # representation of the anti-bot message.
                # -------------------------------------------------

                if len(body) > 1000 and "ماده" in body:

                    print(
                        f"Actual law page detected "
                        f"after {elapsed_seconds}s."
                    )

                    break

                await page.wait_for_timeout(POLL_INTERVAL)

            else:

                raise TimeoutError(
                    "Actual law page did not appear within "
                    f"{LAW_PAGE_TIMEOUT // 1000} seconds."
                )

            # -------------------------------------------------
            # We have the law
            # -------------------------------------------------

            print("FINAL URL:", page.url)
            print("LEN body:", len(body))

            # -------------------------------------------------
            # Parse
            # -------------------------------------------------

            print("Parsing law...")

            articles = parse_law(body)

            if not articles:

                raise ValueError(
                    "parse_law() returned 0 articles."
                )

            # -------------------------------------------------
            # Save
            # -------------------------------------------------

            output_path = f"laws_data/{name}.json"

            with open(
                output_path,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump(
                    articles,
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            print(
                f"Saved {len(articles)} articles "
                f"to {output_path}"
            )

        # -----------------------------------------------------
        # Don't let one failed law stop the whole batch
        # -----------------------------------------------------

        except Exception as e:

            print("\n❌ FAILED")
            print(f"Law:   {name}")
            print(f"URL:   {url}")
            print(f"Error: {type(e).__name__}: {e}")

        # -----------------------------------------------------
        # Always clean up Playwright
        # -----------------------------------------------------

        finally:

            if page:

                try:
                    await page.close()
                except Exception:
                    pass

            if browser:

                try:
                    await browser.close()
                except Exception:
                    pass

            if p:

                try:
                    await p.stop()
                except Exception:
                    pass

            print(f"Finished: {name}")


if __name__ == "__main__":
    asyncio.run(main())