import pytest
from playwright.sync_api import sync_playwright

odds_on_bar = 'button._tab_33oei_5:has-text("Odds")'
@pytest.mark.parametrize("link", [
    'https://www.basketball24.com/match/v5QYCKw8',
    'https://www.basketball24.com/match/Aeu3mByg',
    'https://www.basketball24.com/match/WWG7ksfA'
])
def test_selector_presence(link):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto(link)

        selector_exists = page.query_selector(odds_on_bar) is not None

        assert selector_exists, f"Selector {odd_on_bar} not found on the page {link}"
