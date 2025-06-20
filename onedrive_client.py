import requests


class OneDriveClient:
    """Simple OneDrive client using Microsoft Graph API."""

    GRAPH_API_ROOT = "https://graph.microsoft.com/v1.0/me/drive"  # root endpoint

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    def upload_file(self, local_path: str, onedrive_path: str) -> requests.Response:
        """Upload a local file to the specified OneDrive path."""
        with open(local_path, "rb") as f:
            url = f"{self.GRAPH_API_ROOT}/root:/{onedrive_path}:/content"
            response = requests.put(url, headers=self._headers(), data=f)
        response.raise_for_status()
        return response

    def download_file(self, onedrive_path: str, local_path: str) -> None:
        """Download a file from OneDrive to the local filesystem."""
        url = f"{self.GRAPH_API_ROOT}/root:/{onedrive_path}:/content"
        response = requests.get(url, headers=self._headers(), stream=True)
        response.raise_for_status()
        with open(local_path, "wb") as out:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    out.write(chunk)


__all__ = ["OneDriveClient"]
