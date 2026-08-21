#!/usr/bin/env python3
"""Extract subject, sent time, and body text from an Outlook .msg file.

Usage: python3 parse_msg.py FILE.msg [FILE.msg ...]

Reads the OLE compound-file streams directly (olefile) because the
`extract_msg` package cannot be installed here — its red-black-tree-mod
dependency fails to build.
"""
import datetime
import html
import re
import struct
import sys

import olefile

STR_PROPS = {
    "0037": "subject",
    "0C1A": "sender_name",
    "0065": "sender_email",
    "0E04": "to",
    "1000": "body_plain",
}


def stream_text(ole, entry):
    name = entry[0]
    data = ole.openstream(entry).read()
    if name[16:20] == "001F":
        return data.decode("utf-16-le", "ignore")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", "ignore")


def html_to_text(raw):
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", raw, flags=re.S | re.I)
    t = re.sub(r"<br[^>]*>|</p>|</div>|</tr>|</h[1-6]>", "\n", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t\xa0]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def sent_time(ole):
    """PR_CLIENT_SUBMIT_TIME (0x0039), a FILETIME in the properties stream."""
    try:
        data = ole.openstream("__properties_version1.0").read()
    except OSError:
        return None
    for i in range(32, len(data) - 15, 16):
        entry = data[i : i + 16]
        prop_type, prop_tag = struct.unpack("<HH", entry[0:4])
        if prop_type == 0x0040 and prop_tag == 0x0039:
            ft = struct.unpack("<Q", entry[8:16])[0]
            if ft:
                return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=ft // 10)
    return None


def parse(path):
    ole = olefile.OleFileIO(path)
    out = {"file": path}
    html_body = None
    for entry in ole.listdir():
        name = entry[0]
        if not name.startswith("__substg1.0_"):
            continue
        tag = name[12:16]
        if tag in STR_PROPS:
            out[STR_PROPS[tag]] = stream_text(ole, entry).strip()
        elif tag == "1013":
            html_body = stream_text(ole, entry)

    ts = sent_time(ole)
    out["sent_utc"] = ts.strftime("%Y-%m-%dT%H:%M:%SZ") if ts else None
    body = out.get("body_plain") or ""
    if html_body and len(html_to_text(html_body)) > len(body):
        body = html_to_text(html_body)
    out["body"] = body
    # Links, in order of appearance, with Proofpoint urldefense wrappers unwrapped.
    urls = re.findall(r'https?://[^\s"\'<>)]+', html_body or body)
    clean, seen = [], set()
    for u in urls:
        m = re.match(r"https://urldefense\.com/v3/__(.+?)__;", u)
        if m:
            u = m.group(1)
        u = u.rstrip(".,;")
        if u not in seen and "outlook.office" not in u and "schemas." not in u:
            seen.add(u)
            clean.append(u)
    out["urls"] = clean
    return out


for p in sys.argv[1:]:
    d = parse(p)
    print("=" * 70)
    print("FILE   :", d["file"])
    print("SUBJECT:", d.get("subject"))
    print("SENT   :", d.get("sent_utc"))
    print("FROM   :", d.get("sender_name"), d.get("sender_email", ""))
    print("URLS   :")
    for u in d["urls"]:
        print("   ", u)
    print("--- BODY ---")
    print(d["body"])
