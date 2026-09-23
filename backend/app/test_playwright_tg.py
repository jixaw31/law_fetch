from playwright.async_api import async_playwright
import asyncio


async def main():
    async with async_playwright() as p:

        context = await p.chromium.launch_persistent_context(
            "./telegram_profile",
            channel="chrome",
            headless=False
        )

        page = await context.new_page()

        await page.goto("https://web.telegram.org/")

        print("Log in to Telegram if necessary.")

        await page.wait_for_timeout(30_000)

        print("Current URL:", page.url)

        await context.close()


asyncio.run(main())