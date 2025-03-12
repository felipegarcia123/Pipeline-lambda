from unittest.mock import patch, Mock
from lambda_html import download_pages


@patch('lambda_html.s3_client.upload_file')
@patch('lambda_html.requests.get')
def test_download_pages_success(mock_get, mock_upload):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = "<html>Mocked page</html>"
    mock_get.side_effect = [mock_response] * 10

    result = download_pages()
    assert result["status"] == "ok"
    assert mock_get.call_count == 10
    assert mock_upload.call_count == 10


@patch('lambda_html.requests.get')
def test_download_pages_error(mock_get):
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.side_effect = [mock_response] * 10

    result = download_pages()
    assert result["status"] == "ok"
