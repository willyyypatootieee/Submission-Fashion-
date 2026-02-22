import pytest
import pandas as pd
from utils.transform import (
    transform_products,
    _parse_price_to_idr,
    _parse_rating,
    _parse_colors,
    _clean_size,
    _clean_gender,
)


class TestPriceToIdr:
    def test_convert_price_valid(self):
        result = _parse_price_to_idr("$10.50", exchange_rate=16000)
        assert result == 168000

    def test_convert_price_with_comma(self):
        result = _parse_price_to_idr("$1,200.00", exchange_rate=16000)
        assert result == 19200000

    def test_convert_price_invalid(self):
        result = _parse_price_to_idr("invalid", exchange_rate=16000)
        assert result is None

    def test_convert_price_none(self):
        result = _parse_price_to_idr(None, exchange_rate=16000)
        assert result is None


class TestParseRating:
    def test_parse_rating_valid(self):
        result = _parse_rating("Rating: 4.5 / 5")
        assert result == 4.5

    def test_parse_rating_integer(self):
        result = _parse_rating("5 / 5")
        assert result == 5.0

    def test_parse_rating_invalid(self):
        result = _parse_rating("Invalid Rating")
        assert result is None

    def test_parse_rating_none(self):
        result = _parse_rating(None)
        assert result is None


class TestParseColors:
    def test_parse_colors_valid(self):
        result = _parse_colors("3 Colors")
        assert result == 3

    def test_parse_colors_just_number(self):
        result = _parse_colors("5")
        assert result == 5

    def test_parse_colors_invalid(self):
        result = _parse_colors("No colors")
        assert result is None

    def test_parse_colors_none(self):
        result = _parse_colors(None)
        assert result is None


class TestCleanSize:
    def test_clean_size_valid(self):
        result = _clean_size("Size: M")
        assert result == "M"

    def test_clean_size_uppercase(self):
        result = _clean_size("SIZE: XL")
        assert result == "XL"

    def test_clean_size_none(self):
        result = _clean_size(None)
        assert result is None


class TestCleanGender:
    def test_clean_gender_valid(self):
        result = _clean_gender("Gender: Male")
        assert result == "Male"

    def test_clean_gender_uppercase(self):
        result = _clean_gender("GENDER: Female")
        assert result == "Female"

    def test_clean_gender_none(self):
        result = _clean_gender(None)
        assert result is None


class TestTransformProducts:
    def test_transform_valid_dataframe(self):
        df_raw = pd.DataFrame({
            "Title": ["T-Shirt Blue", "Pants Black"],
            "Price": ["$10.00", "$25.00"],
            "Rating": ["4.5 / 5", "4.8 / 5"],
            "Colors": ["3 Colors", "2 Colors"],
            "Size": ["Size: M", "Size: L"],
            "Gender": ["Gender: Male", "Gender: Female"],
            "timestamp": ["2026-02-22T10:00:00", "2026-02-22T10:00:00"],
        })

        result = transform_products(df_raw, exchange_rate=16000)

        assert len(result) == 2
        assert result["Price"].dtype == "int64"
        assert result["Rating"].dtype == "float64"
        assert result["Colors"].dtype == "int64"
        assert result["Size"].dtype == "string"
        assert result["Gender"].dtype == "string"

    def test_transform_removes_duplicates(self):
        df_raw = pd.DataFrame({
            "Title": ["T-Shirt", "T-Shirt"],
            "Price": ["$10.00", "$10.00"],
            "Rating": ["4.5 / 5", "4.5 / 5"],
            "Colors": ["3 Colors", "3 Colors"],
            "Size": ["Size: M", "Size: M"],
            "Gender": ["Gender: Male", "Gender: Male"],
            "timestamp": ["2026-02-22T10:00:00", "2026-02-22T10:00:00"],
        })

        result = transform_products(df_raw)
        assert len(result) == 1

    def test_transform_removes_null(self):
        df_raw = pd.DataFrame({
            "Title": ["T-Shirt", None],
            "Price": ["$10.00", "$20.00"],
            "Rating": ["4.5 / 5", "4.8 / 5"],
            "Colors": ["3 Colors", "2 Colors"],
            "Size": ["Size: M", "Size: L"],
            "Gender": ["Gender: Male", "Gender: Female"],
            "timestamp": ["2026-02-22T10:00:00", "2026-02-22T10:00:00"],
        })

        result = transform_products(df_raw)
        assert len(result) == 1

    def test_transform_empty_dataframe(self):
        df_raw = pd.DataFrame()
        with pytest.raises(ValueError):
            transform_products(df_raw)

    def test_transform_missing_columns(self):
        df_raw = pd.DataFrame({
            "Title": ["T-Shirt"],
            "Price": ["$10.00"],
        })
        with pytest.raises(ValueError):
            transform_products(df_raw)