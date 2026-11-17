import json
import os
import time
from dotenv import load_dotenv
load_dotenv()
from playwright.sync_api import sync_playwright
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # Or HuggingFaceEmbeddings for local/free

URL = "https://www.tnagrisnet.tn.gov.in/people_app/GoScheme"
JSON_PATH = "tn_uzhavan_goschemes.json"
FAISS_PATH = "faiss_index"


def scrape_goscheme() -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")

        all_records = []

        # Locate the Department dropdown (first <select> on the page)
        dept_select = page.locator("select").nth(0)
        dept_options = dept_select.locator("option").all()

        departments = []
        for opt in dept_options:
            val = opt.get_attribute("value")
            name = opt.inner_text().strip()
            if val and val not in ("", "0", "-1") and "select" not in name.lower():
                departments.append((val, name))

        for dept_val, dept_name in departments:
            print(f"Scraping department: {dept_name}")
            dept_select.select_option(dept_val)
            page.wait_for_timeout(1000)

            page.get_by_role("button", name="Submit").click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(1000)

            length_select = page.locator("select[name*='length']")
            if length_select.count() > 0:
                length_select.select_option("100")
                page.wait_for_timeout(500)

            while True:
                rows = page.locator("table tbody tr").all()
                for row in rows:
                    cells = row.locator("td").all()
                    if len(cells) < 7:
                        continue

                    go_link = ""
                    link_el = cells[6].locator("a")
                    if link_el.count() > 0:
                        go_link = link_el.first.get_attribute("href") or ""

                    record = {
                        "selected_department": dept_name,
                        "s_no": cells[0].inner_text().strip(),
                        "department": cells[1].inner_text().strip(),
                        "scheme": cells[2].inner_text().strip(),
                        "scheme_description": cells[3].inner_text().strip(),
                        "eligibility_criteria": cells[4].inner_text().strip(),
                        "documents_required": cells[5].inner_text().strip(),
                        "go_guidelines_text": cells[6].inner_text().strip(),
                        "go_guidelines_url": go_link,
                    }
                    all_records.append(record)

                next_btn = page.locator(".paginate_button.next:not(.disabled)")
                if next_btn.count() > 0:
                    next_btn.click()
                    page.wait_for_timeout(500)
                else:
                    break

            time.sleep(0.5)

        browser.close()

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_records, f, indent=2, ensure_ascii=False)

    print(f"Done! Saved {len(all_records)} scheme records to {JSON_PATH}")
    return all_records


def build_or_update_faiss(records: list[dict]):
    # Keep each scheme intact as much as possible while splitting very long descriptions
    splitter = RecursiveJsonSplitter(max_chunk_size=1000)

    # Pass each record separately with its own metadata so schemes don't bleed together
    metadatas = [
        {
            "source": JSON_PATH,
            "department": rec["department"] or rec["selected_department"],
            "scheme": rec["scheme"],
            "go_guidelines_url": rec["go_guidelines_url"],
        }
        for rec in records
    ]

    docs = splitter.create_documents(texts=records, metadatas=metadatas)
    print(f"Created {len(docs)} document chunks from {len(records)} records.")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # If an index already exists on disk, load and append; otherwise create a new one
    if os.path.exists(FAISS_PATH):
        vectorstore = FAISS.load_local(
            FAISS_PATH, embeddings, allow_dangerous_deserialization=True
        )
        vectorstore.add_documents(docs)
    else:
        vectorstore = FAISS.from_documents(docs, embeddings)

    vectorstore.save_local(FAISS_PATH)
    print(f"Saved FAISS index to '{FAISS_PATH}'")


if __name__ == "__main__":
    scraped_records = scrape_goscheme()
    if scraped_records:
        build_or_update_faiss(scraped_records)
