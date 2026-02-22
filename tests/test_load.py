import pytest
import pandas as pd
import os
from unittest.mock import patch, MagicMock
from utils.load import save_to_csv, save_to_postgresql, save_to_google_sheets


class TestSaveToCsv:
    def test_save_to_csv_success(self, tmp_path):
        df = pd.DataFrame({
            "Title": ["T-Shirt"],
            "Price": [168000],
            "Rating": [4.5],
            "Colors": [3],
            "Size": ["M"],
            "Gender": ["Male"],
            "timestamp": ["2026-02-22T10:00:00"],
        })
        output_path = str(tmp_path / "test.csv")
        save_to_csv(df, output_path)
        assert os.path.exists(output_path)

    def test_save_to_csv_empty_dataframe(self):
        df = pd.DataFrame()
        with pytest.raises(ValueError):
            save_to_csv(df, "test.csv")

    def test_save_to_csv_none_dataframe(self):
        with pytest.raises(ValueError):
            save_to_csv(None, "test.csv")

    def test_save_to_csv_invalid_extension(self):
        df = pd.DataFrame({"col": [1]})
        with pytest.raises(ValueError):
            save_to_csv(df, "test.txt")


class TestSaveToPostgresql:
    def test_save_to_postgresql_empty_dataframe(self):
        df = pd.DataFrame()
        with pytest.raises(ValueError):
            save_to_postgresql(df, "postgresql://user:pass@localhost/db")

    def test_save_to_postgresql_no_connection_uri(self):
        df = pd.DataFrame({"col": [1]})
        with pytest.raises(ValueError):
            save_to_postgresql(df, "")

    def test_save_to_postgresql_no_table_name(self):
        df = pd.DataFrame({"col": [1]})
        with pytest.raises(ValueError):
            save_to_postgresql(df, "postgresql://user:pass@localhost/db", table_name="")

    @patch("utils.load.create_engine")
    def test_save_to_postgresql_success(self, mock_engine):
        df = pd.DataFrame({
            "Title": ["T-Shirt"],
            "Price": [168000],
        })
        mock_engine_instance = MagicMock()
        mock_engine.return_value = mock_engine_instance

        save_to_postgresql(df, "postgresql://user:pass@localhost/db", "products")
        mock_engine.assert_called_once()


class TestSaveToGoogleSheets:
    def test_save_to_google_sheets_empty_dataframe(self):
        df = pd.DataFrame()
        with pytest.raises(ValueError):
            save_to_google_sheets(df, "sheet_id", "worksheet", "service.json")

    def test_save_to_google_sheets_no_spreadsheet_id(self):
        df = pd.DataFrame({"col": [1]})
        with pytest.raises(ValueError):
            save_to_google_sheets(df, "", "worksheet", "service.json")

    def test_save_to_google_sheets_no_worksheet_name(self):
        df = pd.DataFrame({"col": [1]})
        with pytest.raises(ValueError):
            save_to_google_sheets(df, "sheet_id", "", "service.json")

    def test_save_to_google_sheets_no_service_account(self):
        df = pd.DataFrame({"col": [1]})
        with pytest.raises(ValueError):
            save_to_google_sheets(df, "sheet_id", "worksheet", "")

    @patch("utils.load.gspread.service_account")
    def test_save_to_google_sheets_success(self, mock_gspread):
        df = pd.DataFrame({
            "Title": ["T-Shirt"],
            "Price": [168000],
        })
        mock_client = MagicMock()
        mock_spreadsheet = MagicMock()
        mock_worksheet = MagicMock()

        mock_gspread.return_value = mock_client
        mock_client.open_by_key.return_value = mock_spreadsheet
        mock_spreadsheet.worksheet.return_value = mock_worksheet

        save_to_google_sheets(df, "sheet_id", "products", "service.json")
        mock_gspread.assert_called_once_with(filename="service.json")