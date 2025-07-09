# GCP Audit Scanner 💦

A simple Python tool to scan multiple GCP projects for sensitive `protoPayload.methodName` activity using Cloud Audit Logs.

---

## 🔧 Prerequisites

1. **Python 3.7+**
2. **Install GCP logging client:**

```bash
pip install google-cloud-logging
```

3. **Authenticate:**

```bash
gcloud auth application-default login
```

Make sure your user/service account has at least:
- `roles/logging.viewer` on each target project

---

## 📁 Setup

### 1. `projects.json`

```json
{
  "project-id-1": "display-name-1",
  "project-id-2": "display-name-2"
}
```

> ⚠️ **Use actual project IDs**, not display names.

---

### 2. `audit_methods.txt`

One method per line:
```
v1.compute.firewalls.insert
v1.compute.firewalls.delete
beta.compute.routes.insert
...
```

---

## ▶️ Run

```bash
python3 gcloud-audit-scanner.py
```

---

## 📄 Output

- Results: `gcp_netsec_audit_<timestamp>.csv`
- Log file: `gcp_netsec_audit_<timestamp>.log`

---

## ✅ Example Result (CSV)

| ProjectID         | Time                | User                  | IP           | Method                          | Resource               | Service         |
|-------------------|---------------------|------------------------|--------------|----------------------------------|------------------------|------------------|
| project-xyz           | 2025-07-08T21:24:00 | bob@example.com        | 1.2.3.4      | v1.compute.firewalls.insert     | projects/project-xyz/...   | compute.googleapis.com |

---

## 🙋‍♂️ Notes

- Denied attempts (`PERMISSION_DENIED`) may not appear unless partially authorized
- Can be run as user or service account (set `$GOOGLE_APPLICATION_CREDENTIALS`)
