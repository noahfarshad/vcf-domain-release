# Domain target release

When a workload domain says it is already on the target, and the plan buttons are dead, read `isCustomizedBom` before you read the screen.

`GET /v1/releases/domains/{id}` returns that field. The domain version is the floor of the component versions. A customized BOM can pin HOST and VCENTER to the builds they already have while NSX has moved on. `PATCH /v1/releases/domains/{id}` with a `targetVersion` is the write that clears it. The 9.1.1 set those patches should agree with is the [VCF 9.1.1 Bill of Materials](https://techdocs.broadcom.com/us/en/vmware-cis/vcf/vcf-9-0-and-later/9-1/release-notes/vmware-cloud-foundation-9-1-1-0-release-notes/vmware-cloud-foundation-9-1-1-0-bill-of-material.html).

## Run

```bash
export SDDC_URL=https://sddc.example.com
export SDDC_TOKEN=...   # a bearer token you already have; this script does not collect one
python3 domain_release.py list
python3 domain_release.py show DOMAIN_ID
python3 domain_release.py clear DOMAIN_ID --target 9.1.1.0
python3 domain_release.py clear DOMAIN_ID --target 9.1.1.0 --commit
```

`clear` prints the payload and does not write unless you pass `--commit`. TLS is verified. `--insecure` is there for an appliance certificate you have not trusted yet. Prefer the CA.

After the write, hard-refresh the Upgrades tab. The sequence should be there, and the plan controls should be live. Lifecycle of the components themselves is still done in VCF Operations.
