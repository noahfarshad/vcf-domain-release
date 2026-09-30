#!/usr/bin/env python3
"""Show or clear a domain target release on SDDC Manager.

A domain can report that it is already on the target while isCustomizedBom is
true and HOST or VCENTER is still pinned. The Upgrades tab then has nothing
to plan. Get Release By Domain is the field. Update Release By Domain ID is
the write.

https://developer.broadcom.com/xapis/vmware-cloud-foundation-api/latest/v1/releases/domains/domainId/get/
https://developer.broadcom.com/xapis/sddc-manager-api/latest/v1/releases/domains/domainId/patch/

Token from the environment. This script does not ask for a password.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

def request(method, url, token, body=None, insecure=False):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    ctx = None
    if insecure:
        import ssl
        ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=60) as res:
            raw = res.read().decode()
            return res.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        sys.exit(f"{exc.code} {exc.read().decode()[:400]}")

def main():
    parser = argparse.ArgumentParser(description="Show or set a domain target release")
    parser.add_argument("action", choices=["list", "show", "clear"])
    parser.add_argument("domain_id", nargs="?")
    parser.add_argument("--target", default="9.1.1.0")
    parser.add_argument("--commit", action="store_true")
    parser.add_argument("--insecure", action="store_true", help="skip TLS verify; prefer the SDDC Manager CA")
    args = parser.parse_args()
    host = os.environ.get("SDDC_URL", "").rstrip("/")
    token = os.environ.get("SDDC_TOKEN", "")
    if not host or not token:
        sys.exit("Set SDDC_URL and SDDC_TOKEN")
    if args.action == "list":
        status, body = request("GET", host + "/v1/domains", token, insecure=args.insecure)
        for domain in body.get("elements", []):
            print(domain.get("id"), domain.get("name"), domain.get("type"))
        return
    if not args.domain_id:
        sys.exit("domain id required")
    url = f"{host}/v1/releases/domains/{args.domain_id}"
    status, current = request("GET", url, token, insecure=args.insecure)
    print(json.dumps({
        "targetVersion": current.get("targetVersion"),
        "isCustomizedBom": current.get("isCustomizedBom"),
        "patches": current.get("patches"),
    }, indent=2))
    if args.action == "show":
        return
    payload = {"targetVersion": args.target}
    print("PATCH", json.dumps(payload))
    if not args.commit:
        print("dry run; pass --commit to write")
        return
    request("PATCH", url, token, payload, insecure=args.insecure)
    status, after = request("GET", url, token, insecure=args.insecure)
    print(json.dumps({
        "targetVersion": after.get("targetVersion"),
        "isCustomizedBom": after.get("isCustomizedBom"),
        "patches": after.get("patches"),
    }, indent=2))

if __name__ == "__main__":
    main()
