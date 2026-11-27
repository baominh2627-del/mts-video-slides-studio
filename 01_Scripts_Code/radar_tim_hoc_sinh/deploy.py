# -*- coding: utf-8 -*-
"""
Đưa Web App (Firebase Hosting) + Quy tắc bảo mật (Firestore Rules) lên mạng
chỉ bằng Python chuẩn + service-account.json (mất ~3 giây, không cần npm/firebase-tools).

Chạy: python deploy.py
"""

import gzip
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import firebase_app

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "app"
PUBLIC_DIR = APP_DIR / "public"
DEPLOY_SCOPES = "https://www.googleapis.com/auth/cloud-platform https://www.googleapis.com/auth/firebase"


def get_deploy_token(cfg):
    sa = firebase_app._load_sa(cfg)
    now = int(time.time())
    hdr = firebase_app._b64u(json.dumps({"alg": "RS256", "typ": "JWT"}).encode("utf-8"))
    claims = firebase_app._b64u(json.dumps({
        "iss": sa["client_email"],
        "scope": DEPLOY_SCOPES,
        "aud": sa["token_uri"],
        "iat": now,
        "exp": now + 3600,
    }).encode("utf-8"))
    sig = firebase_app._b64u(firebase_app._sign_rs256(f"{hdr}.{claims}".encode("ascii"), *sa["rsa"]))
    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": f"{hdr}.{claims}.{sig}",
    }).encode("utf-8")
    with urllib.request.urlopen(urllib.request.Request(sa["token_uri"], data=body), timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))["access_token"], sa["project_id"]


def req_json(method, url, token, payload=None, raw_bytes=None, content_type="application/json"):
    data = raw_bytes if raw_bytes is not None else (json.dumps(payload).encode("utf-8") if payload is not None else None)
    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        headers["Content-Type"] = content_type
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            txt = r.read().decode("utf-8", errors="replace")
            return r.status, (json.loads(txt) if txt.strip().startswith("{") else {}), txt
    except urllib.error.HTTPError as e:
        txt = e.read().decode("utf-8", errors="replace")
        return e.code, {}, txt


def deploy_firestore_rules(token, project):
    rules_text = (APP_DIR / "firestore.rules").read_text(encoding="utf-8")
    code, rs, txt = req_json(
        "POST",
        f"https://firebaserules.googleapis.com/v1/projects/{project}/rulesets",
        token,
        {"source": {"files": [{"name": "firestore.rules", "content": rules_text}]}},
    )
    if not (200 <= code < 300):
        raise RuntimeError(f"Tạo ruleset lỗi {code}: {txt}")
    rs_name = rs["name"]
    rel_name = f"projects/{project}/releases/cloud.firestore"
    code, _, txt = req_json(
        "PATCH",
        f"https://firebaserules.googleapis.com/v1/{rel_name}",
        token,
        {"release": {"name": rel_name, "rulesetName": rs_name}},
    )
    if code == 404:
        code, _, txt = req_json(
            "POST",
            f"https://firebaserules.googleapis.com/v1/projects/{project}/releases",
            token,
            {"name": rel_name, "rulesetName": rs_name},
        )
    if not (200 <= code < 300):
        raise RuntimeError(f"Cập nhật release Firestore Rules lỗi {code}: {txt}")
    print(f"✅ Đã cập nhật Firestore Rules ({rs_name.rsplit('/', 1)[-1]})")


def deploy_hosting(token, project):
    fb_cfg = json.loads((APP_DIR / "firebase.json").read_text(encoding="utf-8")).get("hosting", {})
    # Đảm bảo site mặc định tồn tại
    code, site, txt = req_json("GET", f"https://firebasehosting.googleapis.com/v1beta1/projects/{project}/sites/{project}", token)
    if code == 404:
        code, site, txt = req_json(
            "POST",
            f"https://firebasehosting.googleapis.com/v1beta1/projects/{project}/sites?siteId={project}",
            token,
            {},
        )
    if not (200 <= code < 300):
        raise RuntimeError(f"Kiểm tra Hosting site lỗi {code}: {txt}")

    headers_cfg = []
    for h in fb_cfg.get("headers", []):
        headers_cfg.append({
            "glob": h["source"],
            "headers": {kv["key"]: kv["value"] for kv in h.get("headers", [])},
        })

    code, ver, txt = req_json(
        "POST",
        f"https://firebasehosting.googleapis.com/v1beta1/sites/{project}/versions",
        token,
        {"config": {"headers": headers_cfg}},
    )
    if not (200 <= code < 300):
        raise RuntimeError(f"Tạo version Hosting lỗi {code}: {txt}")
    ver_name = ver["name"]

    files_map = {}
    gz_by_hash = {}
    for p in sorted(PUBLIC_DIR.rglob("*")):
        if not p.is_file():
            continue
        rel = "/" + p.relative_to(PUBLIC_DIR).as_posix()
        gz = gzip.compress(p.read_bytes(), compresslevel=9)
        h = hashlib.sha256(gz).hexdigest()
        files_map[rel] = h
        gz_by_hash[h] = gz

    code, pop, txt = req_json(
        "POST",
        f"https://firebasehosting.googleapis.com/v1beta1/{ver_name}:populateFiles",
        token,
        {"files": files_map},
    )
    if not (200 <= code < 300):
        raise RuntimeError(f"populateFiles lỗi {code}: {txt}")

    upload_url = pop.get("uploadUrl", "")
    needed = pop.get("uploadRequiredHashes", [])
    for h in needed:
        uc, _, utxt = req_json("POST", f"{upload_url}/{h}", token, raw_bytes=gz_by_hash[h], content_type="application/octet-stream")
        if not (200 <= uc < 300):
            raise RuntimeError(f"Upload file {h[:10]} lỗi {uc}: {utxt}")

    code, _, txt = req_json(
        "PATCH",
        f"https://firebasehosting.googleapis.com/v1beta1/{ver_name}?updateMask=status",
        token,
        {"status": "FINALIZED"},
    )
    if not (200 <= code < 300):
        raise RuntimeError(f"FINALIZED lỗi {code}: {txt}")

    code, rel, txt = req_json(
        "POST",
        f"https://firebasehosting.googleapis.com/v1beta1/sites/{project}/releases?versionName={urllib.parse.quote(ver_name, safe='')}",
        token,
        {},
    )
    if not (200 <= code < 300):
        raise RuntimeError(f"Release Hosting lỗi {code}: {txt}")

    default_url = site.get("defaultUrl") or f"https://{project}.web.app"
    print(f"✅ Đã đưa Web App lên mạng ({len(files_map)} file, tải mới {len(needed)} file): {default_url}")
    return default_url


def main():
    cfg_path = BASE_DIR / "config.json"
    if not cfg_path.exists():
        cfg_path = BASE_DIR / "config.example.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    token, project = get_deploy_token(cfg)
    deploy_firestore_rules(token, project)
    url = deploy_hosting(token, project)
    print(f"\n🎉 Hoàn tất! Mở app tại: {url}")


if __name__ == "__main__":
    main()
