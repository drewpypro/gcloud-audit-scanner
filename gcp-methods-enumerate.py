import requests

# This generates a report of methods that do not match the required input for accurately querying methods in google cloud logging

DISCOVERY_URL = "https://www.googleapis.com/discovery/v1/apis"
all_methods = set()

print("[*] Fetching API list from Google Discovery Service...")
apis = requests.get(DISCOVERY_URL).json()["items"]
print(f"[+] Found {len(apis)} APIs")

for i, api in enumerate(apis, 1):
    api_name = api["name"]
    version = api["version"]
    discovery_rest_url = api["discoveryRestUrl"]
    print(f"\n[{i}/{len(apis)}] → Processing API: {api_name} (version: {version})")

    try:
        desc = requests.get(discovery_rest_url).json()
        print(f"    ↳ Fetched discovery doc for {api_name}")

        if "resources" not in desc:
            print(f"    ⚠️  No 'resources' in {api_name} — skipping")
            continue

        def extract_methods(obj, prefix=""):
            methods = []
            if "methods" in obj:
                for method_name in obj["methods"]:
                    full_method = f"{prefix}{method_name}"
                    methods.append(full_method)
            if "resources" in obj:
                for res_name, res_obj in obj["resources"].items():
                    methods += extract_methods(res_obj, prefix=f"{prefix}{res_name}.")
            return methods

        service_methods = extract_methods(desc)
        print(f"    ↳ Found {len(service_methods)} methods")

        for method in service_methods:
            fqmn = f"{desc['name']}.{method}"
            all_methods.add(fqmn)

    except Exception as e:
        print(f"    ❌ Failed to process {api_name}: {e}")

# Output summary
print(f"\n✅ Completed! Total unique methods collected: {len(all_methods)}")

# Preview sample
print("\n🔎 Sample method names:")
for m in sorted(all_methods)[:10]:
    print(f"   - {m}")

# Save to file
out_file = "all_gcp_protopayload_methodnames.txt"
with open(out_file, "w") as f:
    for m in sorted(all_methods):
        f.write(m + "\n")

print(f"\n💾 Full list written to: {out_file}")
