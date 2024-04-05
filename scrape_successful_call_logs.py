import os
import time
from playwright.sync_api import sync_playwright


output_path = "./output/successful-call-logs"
raw_output_file_path = os.path.join(output_path, "raw.csv")


if __name__ == "__main__":
    try:
        # Reporting setup
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        output_file_writer = open(raw_output_file_path, "a")
        output_file_writer.write("ID,Raw Text\n")

        # Playwright setup
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False, slow_mo=100)
        context = browser.new_context()
        page = context.new_page()

        # Selectors
        login_url = "https://discord.com/login"
        list_items = page.locator("#search-results li")
        next_button = page.locator("button[type='button'][rel='next']")

        # Scraping logic
        page.goto(login_url)

        # Pause for manual preparation
        print(
            "1. Login to Playwright's browser window\n",
            "2. Go to the desired DM\n",
            "3. Set up the search filter to have `mentions:` for both users\n",
            "4. Sort results with `Old` entries first to have consistent IDs with subsequent runs\n",
        )
        input("Press Enter to continue...\n")

        count = 0

        # Process each search result page
        while True:
            # Process each search result list item
            for list_item in list_items.all():
                # Get the text content
                text_content = list_item.text_content() or ""

                # Skip if the message isn't a successful call log (e.g., replies and actual mentions)
                if "started a call" not in text_content:
                    continue

                # Count successful call logs
                count += 1

                # Remove 'Jump' label text
                text_content = text_content.replace("Jump", "")

                # Save results
                output_file_writer.write(f"{count},{text_content}\n")
                list_item.scroll_into_view_if_needed()
                list_item.screenshot(
                    path=os.path.join(output_path, f"{count}-{int(time.time())}.png")
                )

            # Exit early if the last page has just been processed
            if next_button.is_disabled():
                break

            # Go to the next page
            next_button.click()

            # Wait to ensure new items are loaded
            page.wait_for_timeout(3000)

        print("Done!\n")

    finally:
        # Cleanup
        if output_file_writer:
            output_file_writer.close()
        if page:
            page.close()
        if context:
            context.close()
        if browser:
            browser.close()
        if playwright:
            playwright.stop()
