import pytest
from unittest.mock import Mock, patch, MagicMock
from utils.extract import (
    build_page_url,
    fetch_html,
    _find_text_by_pattern,
    parse_product_card,
    parse_page,
    scrape_products,
    ExtractError,
)
from bs4 import BeautifulSoup


class TestBuildPageUrl:
    def test_page_1_returns_root(self):
        assert build_page_url(1) == "https://fashion-studio.dicoding.dev/"

    def test_page_2_returns_page2(self):
        assert build_page_url(2) == "https://fashion-studio.dicoding.dev/page2"

    def test_page_50_returns_page50(self):
        assert build_page_url(50) == "https://fashion-studio.dicoding.dev/page50"

    def test_invalid_page_raises_error(self):
        with pytest.raises(ValueError):
            build_page_url(0)

    def test_negative_page_raises_error(self):
        with pytest.raises(ValueError):
            build_page_url(-1)


class TestFetchHtml:
    @patch("utils.extract.requests.Session.get")
    def test_fetch_html_success(self, mock_get):
        mock_response = Mock()
        mock_response.text = "<html>Test</html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        session = Mock()
        session.get = mock_get

        result = fetch_html(session, "http://example.com")
        assert result == "<html>Test</html>"

    @patch("utils.extract.requests.Session.get")
    def test_fetch_html_timeout(self, mock_get):
        import requests
        mock_get.side_effect = requests.Timeout("Timeout")

        session = Mock()
        session.get = mock_get

        with pytest.raises(ExtractError):
            fetch_html(session, "http://example.com")

    @patch("utils.extract.requests.Session.get")
    def test_fetch_html_connection_error(self, mock_get):
        import requests
        mock_get.side_effect = requests.ConnectionError("Connection failed")

        session = Mock()
        session.get = mock_get

        with pytest.raises(ExtractError):
            fetch_html(session, "http://example.com")


class TestFindTextByPattern:
    def test_find_price(self):
        html = '<div><span>Price: $10.50</span></div>'
        card = BeautifulSoup(html, "html.parser").find("div")
        result = _find_text_by_pattern(card, r"\$\s*[\d.,]+")
        assert result is not None
        assert "$10.50" in result

    def test_find_rating(self):
        html = '<div><span>Rating: 4.5 / 5</span></div>'
        card = BeautifulSoup(html, "html.parser").find("div")
        result = _find_text_by_pattern(card, r"rating|/ 5")
        assert result is not None

    def test_pattern_not_found(self):
        html = '<div><span>No match here</span></div>'
        card = BeautifulSoup(html, "html.parser").find("div")
        result = _find_text_by_pattern(card, r"\$\s*[\d.,]+")
        assert result is None


class TestParseProductCard:
    def test_parse_valid_card(self):
        html = """
        <div class="card">
            <h3>T-Shirt Blue</h3>
            <span>$20.00</span>
            <span>Rating: 4.5 / 5</span>
            <span>3 Colors</span>
            <span>Size: M</span>
            <span>Gender: Male</span>
        </div>
        """
        card = BeautifulSoup(html, "html.parser").find("div")
        result = parse_product_card(card, "2026-02-22T10:00:00")

        assert result is not None
        assert result["Title"] == "T-Shirt Blue"
        assert result["Price"] == "$20.00"
        assert result["Gender"] == "Male"
        assert result["timestamp"] == "2026-02-22T10:00:00"

    def test_parse_card_missing_field(self):
        html = """
        <div class="card">
            <h3>T-Shirt Blue</h3>
            <span>$20.00</span>
        </div>
        """
        card = BeautifulSoup(html, "html.parser").find("div")
        result = parse_product_card(card, "2026-02-22T10:00:00")
        assert result is None


class TestScrapProducts:
    def test_invalid_page_range(self):
        with pytest.raises(ValueError):
            scrape_products(start_page=5, end_page=2)

    def test_invalid_start_page(self):
        with pytest.raises(ValueError):
            scrape_products(start_page=0, end_page=5)

    @patch("utils.extract.scrape_products")
    def test_scrape_with_mock(self, mock_scrape):
        mock_scrape.return_value = [
            {
                "Title": "Shirt",
                "Price": "$10",
                "Rating": "4.5",
                "Colors": "2",
                "Size": "M",
                "Gender": "Male",
                "timestamp": "2026-02-22T10:00:00",
            }
        ]
        result = scrape_products()
        assert len(result) == 1
        assert result[0]["Title"] == "Shirt"