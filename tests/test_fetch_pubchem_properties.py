import pytest
from unittest.mock import patch, MagicMock

from fetch_pubchem_properties import (
    fetch_cid_by_name,
    fetch_properties_by_cid,
    process_library,
)


def _mock_response(status_code, json_data):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    return mock


@patch("fetch_pubchem_properties.requests.get")
def test_fetch_cid_by_name_success(mock_get):
    mock_get.return_value = _mock_response(200, {"IdentifierList": {"CID": [5280343]}})
    assert fetch_cid_by_name("Quercetin") == 5280343


@patch("fetch_pubchem_properties.requests.get")
def test_fetch_cid_by_name_not_found(mock_get):
    mock_get.return_value = _mock_response(404, {})
    assert fetch_cid_by_name("NotARealCompound123") is None


@patch("fetch_pubchem_properties.requests.get")
def test_fetch_properties_by_cid_success(mock_get):
    mock_get.return_value = _mock_response(
        200,
        {"PropertyTable": {"Properties": [{"MolecularWeight": "302.24", "XLogP": "1.5"}]}},
    )
    props = fetch_properties_by_cid(5280343)
    assert props["MolecularWeight"] == "302.24"


def test_process_library_raises_on_missing_column(tmp_path):
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text("name,foo\nQuercetin,1\n")
    with pytest.raises(ValueError, match="compound_name"):
        process_library(str(bad_csv), str(tmp_path / "out.csv"))


def test_process_library_raises_on_empty_input(tmp_path):
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("compound_name\n")
    with pytest.raises(ValueError, match="no rows"):
        process_library(str(empty_csv), str(tmp_path / "out.csv"))
