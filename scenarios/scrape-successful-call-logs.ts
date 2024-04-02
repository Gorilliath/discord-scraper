import { test } from "@playwright/test";
import { createWriteStream, existsSync, mkdirSync } from "fs";
import { EOL } from "os";
import { join } from "path";

test("Scrape Discord for successful call logs", async ({ page }) => {
  // --- Reporting
  const outputPath = join("./output");
  if (!existsSync(outputPath)) mkdirSync(outputPath);

  const outputFile = join(outputPath, "successful-call-logs.csv");
  const outputFileWriter = createWriteStream(outputFile, { flags: "a" });

  outputFileWriter.write(`ID,Raw Text${EOL}`);

  // --- Selectors

  const loginURL = "https://discord.com/login";
  const listItems = page.locator("#search-results li");
  const nextButton = page.locator("button[type='button'][rel='next']");

  // --- Scraping logic

  await page.goto(loginURL);

  console.log(
    "1. Login to Playwright's browser window\n" +
      "2. Might need to press `step-over` button in the playwright debugging window so the Discord login page is opened\n" +
      "3. Go to the desired DM\n" +
      "4. Set up search filter to have `mentions:` for both users\n" +
      "5. Look at `Old` entries first to have consistent IDs with subsequent runs\n" +
      "6. Continue execution"
  );
  await page.pause();

  let count = 0;

  // Process each page
  while (true) {
    // Process each search result list item
    for (const listItem of await listItems.all()) {
      // Get the text content
      let textContent = (await listItem.textContent()) || "";

      // Skip if the message isn't a successful call log (e.g: replies and actual mentions)
      if (!textContent.includes("started a call")) continue;

      // Remove 'Jump' label text
      textContent = textContent.replace("Jump", "");

      // Save results
      count++;

      outputFileWriter.write(`${count},${textContent}${EOL}`);

      await listItem.scrollIntoViewIfNeeded();
      await listItem.screenshot({
        path: `${outputPath}/${count}-${Date.now()}.png`
      });
    }

    // Exit early if the last page has just been processed
    if (await nextButton.isDisabled()) break;

    // Go to the next page
    await nextButton.click();

    // Sledgehammer timeout to be sure the new items are loaded
    await page.waitForTimeout(3 * 1000);
  }

  outputFileWriter.close();
});
