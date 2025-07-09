import csv
import json
import os
import sys
from datetime import datetime
from google.cloud import logging_v2

PROJECTS_FILE = "projects.json"
METHODS_FILE = "audit_methods.txt"
TIMESTAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
OUTPUT_FILE = f"gcp_netsec_audit_{TIMESTAMP}.csv"
LOG_FILE = f"gcp_netsec_audit_{TIMESTAMP}.log"

# Load project list
try:
    with open(PROJECTS_FILE) as f:
        projects = json.load(f)
except Exception as e:
    sys.exit(f"[ERROR] Failed to load {PROJECTS_FILE}: {e}")

# Load audit method list
try:
    with open(METHODS_FILE) as f:
        method_names = [line.strip() for line in f if line.strip()]
except Exception as e:
    sys.exit(f"[ERROR] Failed to load {METHODS_FILE}: {e}")

print(f"[*] Loaded {len(projects)} projects and {len(method_names)} method filters")

# Initialize output
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ProjectID", "Time", "User", "IP", "Method", "Resource", "Service"
        ])

def log(msg):
    print(msg)
    with open(LOG_FILE, "a") as logf:
        logf.write(msg + "\n")

# Perform scan
for project_id, project_name in projects.items():
    log(f"\n🔍 Auditing project {project_id} ({project_name})")
    try:
        client = logging_v2.Client(project=project_id)
        for method in method_names:
            log(f"  ➤ Searching for: {method}")
            query = f'protoPayload.methodName="{method}"'
            entries = client.list_entries(filter_=query, order_by=logging_v2.DESCENDING, page_size=100)

            for entry in entries:
                payload = entry.payload.get("protoPayload", entry.payload)
                auth_info = payload.get("authenticationInfo", {})
                metadata = payload.get("requestMetadata", {})

                row = [
                    project_id,
                    payload.get("timestamp", entry.timestamp),
                    auth_info.get("principalEmail", "UNKNOWN"),
                    metadata.get("callerIp", "UNKNOWN"),
                    payload.get("methodName"),
                    payload.get("resourceName", "N/A"),
                    payload.get("serviceName", "N/A")
                ]
                with open(OUTPUT_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(row)
    except Exception as e:
        log(f"  ❌ Error while processing {project_id}: {e}")

log("\n✅ Audit completed. Output written to:")
log(f"   {OUTPUT_FILE}")
