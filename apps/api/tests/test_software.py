"""Tests for the software download management endpoints (issue #2)."""

import os

CONTENT = b"fake-installer-binary"


def _upload(client, headers, name="Solotalk Client", version="1.0.0", platform="windows"):
    files = {"file": ("solotalk-setup.exe", CONTENT, "application/octet-stream")}
    data = {"name": name, "version": version, "platform": platform}
    return client.post("/api/admin/software", files=files, data=data, headers=headers)


def test_admin_upload_then_public_list(client, admin_headers):
    resp = _upload(client, admin_headers)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["name"] == "Solotalk Client"
    assert body["version"] == "1.0.0"
    assert body["platform"] == "windows"
    assert body["file_size"] == len(CONTENT)
    assert body["download_count"] == 0
    assert body["is_active"] is True

    public = client.get("/api/software")
    assert public.status_code == 200
    items = public.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == body["id"]


def test_upload_requires_admin(client, user_headers):
    assert _upload(client, {}).status_code == 401
    assert _upload(client, user_headers).status_code == 403


def test_download_increments_count(client, admin_headers):
    software_id = _upload(client, admin_headers).json()["id"]

    resp = client.get(f"/api/software/{software_id}/download")
    assert resp.status_code == 200
    assert resp.content == CONTENT

    items = client.get("/api/software").json()["items"]
    assert items[0]["download_count"] == 1


def test_deactivate_hides_from_public(client, admin_headers):
    software_id = _upload(client, admin_headers).json()["id"]

    resp = client.patch(
        f"/api/admin/software/{software_id}",
        json={"is_active": False},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    assert client.get("/api/software").json()["items"] == []
    assert client.get(f"/api/software/{software_id}/download").status_code == 404

    admin_items = client.get("/api/admin/software", headers=admin_headers).json()
    assert len(admin_items) == 1
    assert admin_items[0]["is_active"] is False


def test_update_metadata(client, admin_headers):
    software_id = _upload(client, admin_headers).json()["id"]

    resp = client.patch(
        f"/api/admin/software/{software_id}",
        json={"name": "Solotalk Pro", "version": "2.0.0"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Solotalk Pro"
    assert body["version"] == "2.0.0"
    assert body["platform"] == "windows"  # untouched


def test_delete_removes_record_and_file(client, admin_headers):
    upload_dir = os.environ["UPLOAD_DIR"]
    before = set(os.listdir(upload_dir))  # other tests share this dir
    software_id = _upload(client, admin_headers).json()["id"]
    assert len(os.listdir(upload_dir)) == len(before) + 1

    resp = client.delete(f"/api/admin/software/{software_id}", headers=admin_headers)
    assert resp.status_code == 204

    assert client.get("/api/admin/software", headers=admin_headers).json() == []
    assert client.get(f"/api/software/{software_id}/download").status_code == 404
    assert set(os.listdir(upload_dir)) == before
