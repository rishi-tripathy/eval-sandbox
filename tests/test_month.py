import pytest
from workbench.month import Month


class TestMonthConstruction:
    def test_valid_month_construction(self):
        m = Month(2024, 3)
        assert m.year == 2024
        assert m.month == 3
    
    def test_invalid_month_zero(self):
        with pytest.raises(ValueError, match="0 specified is not a valid month"):
            Month(2024, 0)
    
    def test_invalid_month_thirteen(self):
        with pytest.raises(ValueError, match="13 specified is not a valid month"):
            Month(2024, 13)
    
    def test_invalid_month_negative(self):
        with pytest.raises(ValueError, match="-1 specified is not a valid month"):
            Month(2024, -1)
    
    def test_invalid_year_negative(self):
        with pytest.raises(ValueError, match="-1 specified is not a valid year"):
            Month(-1, 3)


class TestMonthParsing:
    def test_parse_valid_string(self):
        m = Month.from_string("2024-03")
        assert m.year == 2024
        assert m.month == 3
    
    def test_parse_without_zero_pad(self):
        # This should work - the implementation doesn't require zero padding
        m = Month.from_string("2024-3")
        assert m.year == 2024
        assert m.month == 3
    
    def test_parse_invalid_month(self):
        with pytest.raises(ValueError, match="13 specified is not a valid month"):
            Month.from_string("2024-13")
    
    def test_parse_invalid_format(self):
        # This will fail when trying to unpack the split result
        with pytest.raises(ValueError):
            Month.from_string("2024/03")
    
    def test_parse_non_numeric(self):
        # This will fail when trying to convert to int
        with pytest.raises(ValueError):
            Month.from_string("2024-XX")


class TestMonthStringOutput:
    def test_to_string_single_digit_month(self):
        m = Month(2024, 3)
        assert m.to_string() == "2024-03"
    
    def test_to_string_double_digit_month(self):
        m = Month(2024, 12)
        assert m.to_string() == "2024-12"
    
    def test_to_string_january(self):
        m = Month(2024, 1)
        assert m.to_string() == "2024-01"


class TestMonthComparisons:
    def test_same_year_comparison(self):
        m1 = Month(2024, 3)
        m2 = Month(2024, 4)
        assert m1 < m2
        assert m2 > m1
        assert m1 <= m2
        assert m2 >= m1
        assert m1 != m2
    
    def test_different_year_comparison(self):
        m1 = Month(2023, 12)
        m2 = Month(2024, 1)
        assert m1 < m2
        assert m2 > m1
    
    def test_equality(self):
        m1 = Month(2024, 3)
        m2 = Month(2024, 3)
        assert m1 == m2
        assert m1 <= m2
        assert m1 >= m2
    
    def test_inequality_with_different_types(self):
        m = Month(2024, 3)
        # These will raise AttributeError because __eq__ doesn't handle non-Month types
        with pytest.raises(AttributeError):
            m == "2024-03"
        with pytest.raises(AttributeError):
            m == 2024
        with pytest.raises(AttributeError):
            m == None


class TestMonthAddition:
    def test_add_within_year(self):
        m = Month(2024, 3)
        result = m.add(2)
        assert result.year == 2024
        assert result.month == 5
    
    def test_add_across_year_boundary(self):
        m = Month(2024, 11)
        result = m.add(3)
        assert result.year == 2025
        assert result.month == 2
    
    def test_add_exactly_one_year(self):
        m = Month(2024, 3)
        result = m.add(12)
        assert result.year == 2025
        assert result.month == 3
    
    def test_add_zero(self):
        m = Month(2024, 3)
        result = m.add(0)
        assert result.year == 2024
        assert result.month == 3
    
    def test_add_negative_within_year(self):
        m = Month(2024, 3)
        result = m.add(-2)
        assert result.year == 2024
        assert result.month == 1
    
    def test_add_negative_across_year_boundary(self):
        m = Month(2024, 2)
        result = m.add(-3)
        assert result.year == 2023
        assert result.month == 11
    
    def test_add_large_positive(self):
        m = Month(2024, 1)
        result = m.add(25)  # 2 years + 1 month
        assert result.year == 2026
        assert result.month == 2
    
    def test_add_large_negative(self):
        m = Month(2024, 12)
        result = m.add(-25)  # -2 years - 1 month
        assert result.year == 2022
        assert result.month == 11


class TestMonthFromIndex:
    def test_from_index_zero(self):
        m = Month.from_index(0)  # January of year 0
        assert m.year == 0
        assert m.month == 1
    
    def test_from_index_simple(self):
        m = Month.from_index(24)  # January of year 2
        assert m.year == 2
        assert m.month == 1
    
    def test_from_index_december(self):
        m = Month.from_index(11)  # December of year 0
        assert m.year == 0
        assert m.month == 12
    
    def test_from_index_large(self):
        m = Month.from_index(24290)  # 2024*12 + 3 - 1 = 24288 + 2 = 24290
        assert m.year == 2024
        assert m.month == 3
    
    def test_from_index_round_trip(self):
        original = Month(2024, 7)
        index = original._index
        reconstructed = Month.from_index(index)
        assert reconstructed.year == original.year
        assert reconstructed.month == original.month


class TestMonthEdgeCases:
    def test_december_to_january(self):
        m = Month(2024, 12)
        result = m.add(1)
        assert result.year == 2025
        assert result.month == 1
    
    def test_january_to_december(self):
        m = Month(2024, 1)
        result = m.add(-1)
        assert result.year == 2023
        assert result.month == 12
    
    def test_hash_and_dict_usage(self):
        # The Month class doesn't implement __hash__, so it's not hashable
        m1 = Month(2024, 3)
        m2 = Month(2024, 3)
        m3 = Month(2024, 4)
        
        # This will raise TypeError: unhashable type: 'Month'
        with pytest.raises(TypeError, match="unhashable type"):
            month_set = {m1, m2, m3}
        
        with pytest.raises(TypeError, match="unhashable type"):
            month_dict = {m1: "March", m3: "April"}