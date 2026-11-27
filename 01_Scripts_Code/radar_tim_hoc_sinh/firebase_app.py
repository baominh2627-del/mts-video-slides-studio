# -*- coding: utf-8 -*-
"""
Đẩy bài tìm gia sư vào APP RIÊNG (Firebase) — chỉ dùng thư viện chuẩn của Python:
  1. Ký JWT RS256 từ service-account.json để lấy OAuth2 access_token
  2. Lưu bài vào Firestore (collection "posts")  -> app hiện danh sách realtime
  3. Gửi push notification (FCM) tới mọi thiết bị đã bật thông báo (collection "tokens")
"""

import base64
import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SCOPES = "https://www.googleapis.com/auth/datastore https://www.googleapis.com/auth/firebase.messaging"
_SHA256_DER_PREFIX = bytes.fromhex("3031300d060960864801650304020105000420")

_sa_cache = None
_token_cache = ("", 0.0)


def _b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _der_read(buf: bytes, idx: int = 0):
    tag = buf[idx]
    idx += 1
    length = buf[idx]
    idx += 1
    if length & 0x80:
        nbytes = length & 0x7F
        length = int.from_bytes(buf[idx : idx + nbytes], "big")
        idx += nbytes
    return tag, buf[idx : idx + length], idx + length


def _parse_pkcs8_rsa(pem: str):
    b64 = "".join(line.strip() for line in pem.splitlines() if line and not line.startswith("-----"))
    der = base64.b64decode(b64)
    _, seq, _ = _der_read(der, 0)
    _, _, pos = _der_read(seq, 0)       # version
    _, _, pos = _der_read(seq, pos)     # algorithmIdentifier
    _, pk_octets, _ = _der_read(seq, pos)
    _, rsa_seq, _ = _der_read(pk_octets, 0)
    _, _, rpos = _der_read(rsa_seq, 0)  # version
    _, n_bytes, rpos = _der_read(rsa_seq, rpos)
    _, e_bytes, rpos = _der_read(rsa_seq, rpos)
    _, d_bytes, _ = _der_read(rsa_seq, rpos)
    return int.from_bytes(n_bytes, "big"), int.from_bytes(e_bytes, "big"), int.from_bytes(d_bytes, "big")


def _sign_rs256(data: bytes, n: int, e: int, d: int) -> bytes:
    digest_info = _SHA256_DER_PREFIX + hashlib.sha256(data).digest()
    k = (n.bit_length() + 7) // 8
    em = b"\x00\x01" + b"\xff" * (k - len(digest_info) - 3) + b"\x00" + digest_info
    sig_int = pow(int.from_bytes(em, "big"), d, n)
    if pow(sig_int, e, n).to_bytes(k, "big") != em:
        raise ValueError("RSA signature self-check failed")
    return sig_int.to_bytes(k, "big")


def _load_sa(cfg):
    global _sa_cache
    if _sa_cache is None:
        path = Path(cfg["firebase"]["service_account"])
        if not path.is_absolute():
            path = BASE_DIR / path
        raw = json.loads(path.read_text(encoding="utf-8"))
        n, e, d = _parse_pkcs8_rsa(raw["private_key"])
        _sa_cache = {
            "project_id": raw["project_id"],
            "client_email": raw["client_email"],
            "token_uri": raw.get("token_uri", "https://oauth2.googleapis.com/token"),
            "rsa": (n, e, d),
        }
    return _sa_cache


def _get_token(cfg):
    global _token_cache
    sa = _load_sa(cfg)
    now = time.time()
    if _token_cache[0] and now < _token_cache[1] - 60:
        return _token_cache[0], sa["project_id"]

    hdr = _b64u(json.dumps({"alg": "RS256", "typ": "JWT"}).encode("utf-8"))
    iat = int(now)
    claims = _b64u(json.dumps({
        "iss": sa["client_email"],
        "scope": SCOPES,
        "aud": sa["token_uri"],
        "iat": iat,
        "exp": iat + 3600,
    }).encode("utf-8"))
    signing_input = f"{hdr}.{claims}".encode("ascii")
    sig = _b64u(_sign_rs256(signing_input, *sa["rsa"]))
    jwt = f"{hdr}.{claims}.{sig}"

    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": jwt,
    }).encode("utf-8")
    req = urllib.request.Request(sa["token_uri"], data=body)
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read().decode("utf-8"))
    _token_cache = (resp["access_token"], now + int(resp.get("expires_in", 3600)))
    return _token_cache[0], sa["project_id"]


def _http_json(method: str, url: str, token: str, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Authorization": f"Bearer {token}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8")
            return r.status, (json.loads(raw) if raw else {}), raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return e.code, {}, raw


def _ngan(s, n):
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def gui(post, cfg):
    token, project = _get_token(cfg)
    fs = f"https://firestore.googleapis.com/v1/projects/{project}/databases/(default)/documents"
    app_url = cfg["firebase"].get("app_url", "").rstrip("/")

    # 1) lưu bài
    fields = {k: {"stringValue": str(post.get(k, ""))} for k in ("subject", "text", "link", "reason", "comment")}
    fields["status"] = {"stringValue": "new"}
    fields["createdAt"] = {"timestampValue": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")}
    code, doc_json, raw = _http_json("POST", f"{fs}/posts", token, {"fields": fields})
    if not (200 <= code < 300):
        raise RuntimeError(f"Firestore POST lỗi {code}: {raw[:300]}")
    doc_id = doc_json["name"].rsplit("/", 1)[-1]

    # 2) push tới các thiết bị
    code, tok_json, raw = _http_json("GET", f"{fs}/tokens?pageSize=300", token)
    if not (200 <= code < 300):
        raise RuntimeError(f"Firestore GET tokens lỗi {code}: {raw[:300]}")
    docs = tok_json.get("documents", [])
    title = "📚 Tìm gia sư — " + post.get("reason", "")
    body = _ngan(post.get("text") or post.get("subject"), 180)
    sent = 0
    for d in docs:
        fcm_token = d.get("fields", {}).get("token", {}).get("stringValue")
        if not fcm_token:
            continue
        msg = {"message": {
            "token": fcm_token,
            "notification": {"title": title, "body": body},
            "data": {"postId": doc_id, "link": post.get("link", "")},
            "webpush": {
                "notification": {"icon": f"{app_url}/icons/icon-192.png", "tag": doc_id},
                "fcm_options": {"link": f"{app_url}/?id={doc_id}"},
            },
        }}
        sc, _, sraw = _http_json("POST", f"https://fcm.googleapis.com/v1/projects/{project}/messages:send", token, msg)
        if 200 <= sc < 300:
            sent += 1
        elif sc == 404 or "UNREGISTERED" in sraw:
            _http_json("DELETE", f"https://firestore.googleapis.com/v1/{d['name']}", token)
        else:
            print(f"   FCM lỗi {sc}: {sraw[:200]}")
    print(f"   → đã lưu bài {doc_id}, push tới {sent}/{len(docs)} thiết bị")
    return True
