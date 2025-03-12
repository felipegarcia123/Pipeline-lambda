from unittest.mock import patch, ANY, Mock
import datetime
from lambda_csv import process_html


@patch('lambda_csv.s3.list_objects_v2')
@patch('lambda_csv.s3.get_object')
@patch('lambda_csv.s3.upload_file')
def test_process_html(mock_upload, mock_get, mock_list):
    mock_list.return_value = {
        "Contents": [{
            "Key": f"{datetime.date.today().strftime('%Y-%m-%d')}-page-1.html"
        }]
    }
    mock_body = Mock()
    mock_body.read.return_value = (
        b'<html><body><div class="listings__cards notSponsored">'
        b'<a class="listing listing-card" data-location="Barrio1" '
        b'data-price="$100" data-rooms="2" data-floorarea="50">'
        b'<p data-test="bathrooms">3</p></a></div></body></html>'
    )
    mock_get.return_value = {
        "Body": mock_body
    }
    result = process_html()
    print("Result:", result)
    assert result["status"] == "ok"
    mock_upload.assert_called_once_with(
        ANY,
        "casas-final-lambda2",
        f"casas_data_{datetime.date.today().strftime('%Y-%m-%d')}.csv"
    )
