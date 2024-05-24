import pytest
from .. import KlinesDataframe


@pytest.fixture
def ref_single_kline() -> list:
    return [
        [
            "1716163200000",
            "66274.00000000",
            "71515.56000000",
            "66060.31000000",
            "71446.62000000",
            "50816.70110000",
            "1716249599999",
            "3485474763.75229410",
            "1930939",
            "26792.52994000",
            "1839346667.54078900",
            "0",
        ]
    ]


def test_klinedataframe_properties(ref_single_kline):
    assert KlinesDataframe(klines=ref_single_kline).n_rows == 1
    assert KlinesDataframe(klines=ref_single_kline * 2).n_rows == 2


def test_klinedataframe_from_list(ref_single_kline):
    """Check if the dataframe contains the right values also in the right place"""
    kdf = KlinesDataframe(klines=ref_single_kline)
    kdf_dict = kdf.df.iloc[0, :].to_dict()
    assert kdf_dict["Open"] == float(ref_single_kline[0][1])
    assert kdf_dict["High"] == float(ref_single_kline[0][2])
    assert kdf_dict["Low"] == float(ref_single_kline[0][3])
    assert kdf_dict["Close"] == float(ref_single_kline[0][4])
    assert kdf_dict["Volume"] == float(ref_single_kline[0][5])
