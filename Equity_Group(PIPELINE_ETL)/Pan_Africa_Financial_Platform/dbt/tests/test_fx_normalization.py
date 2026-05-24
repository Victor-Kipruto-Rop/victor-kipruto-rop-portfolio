import pytest
from forex.fx_normalizer import FXNormalizer

def test_fx_normalization_kes():
    normalizer = FXNormalizer()
    result = normalizer.normalize(130.0, "KES")
    assert result["usd"] == 1.0
    assert result["kes"] == 130.0

def test_fx_normalization_ugx():
    normalizer = FXNormalizer()
    # 3800 UGX = 1 USD = 130 KES
    result = normalizer.normalize(3800.0, "UGX")
    assert result["usd"] == 1.0
    assert result["kes"] == 130.0

def test_fx_normalization_invalid():
    normalizer = FXNormalizer()
    result = normalizer.normalize(100.0, "INVALID")
    assert result["usd"] == 0
    assert result["kes"] == 0
