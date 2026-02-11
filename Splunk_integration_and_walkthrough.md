# 1️⃣ How the App Integrates with Splunk

## 🔷 High-Level Architecture

```
Streamlit App
    ↓
Structured JSON event
    ↓
HTTP POST (Splunk HEC)
    ↓
Splunk Index (main)
    ↓
Search Processing Language (SPL)
    ↓
Dashboard Panels
```

---

## 🔷 What Happens When AI Runs

When a patient button is pressed and AI inference is triggered:

1. The app generates:

   * diagnosis
   * latency
   * tokens used
   * success/failure
   * alert level
   * scenario
   * model name

2. The app builds a structured JSON payload:

```json
{
  "event_type": "ai_inference",
  "app": "ai_patient_monitor",
  "scenario": "patient2_vtach.csv",
  "alert_level": "EMERGENCY",
  "model": "gpt-4o-mini",
  "latency_ms": 842,
  "tokens_total": 512,
  "success": true
}
```

3. The app sends this to Splunk via:

```
POST https://localhost:8088/services/collector
Authorization: Splunk <HEC_TOKEN>
```

Using environment variables:

```python
SPLUNK_HEC_URL
SPLUNK_HEC_TOKEN
SPLUNK_INDEX
SPLUNK_SOURCETYPE
```

---

## 🔷 Inside the App (Key Logic)

Your integration is essentially:

```python
def send_to_splunk(event_dict):
    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}"
    }

    payload = {
        "index": SPLUNK_INDEX,
        "sourcetype": SPLUNK_SOURCETYPE,
        "event": event_dict
    }

    requests.post(
        SPLUNK_HEC_URL,
        headers=headers,
        json=payload,
        verify=False
    )
```

Every AI inference or clinical alert generates a structured event.

---

## 🔷 Why This Is Powerful

You now have:

| Feature                 | What It Means              |
| ----------------------- | -------------------------- |
| AI Inference logging    | Full AI observability      |
| Latency tracking        | Performance monitoring     |
| Token tracking          | Cost monitoring            |
| Success/failure capture | Reliability tracking       |
| Alert level logging     | Clinical risk visibility   |
| Scenario tagging        | Root cause filtering       |
| Time-series metrics     | Operational trend analysis |

This is enterprise-grade AI telemetry.



# 3️⃣ Full Setup Walkthrough

This is your “from zero to dashboard” guide.

---

# Step 1 — Enable HTTP Event Collector (HEC)

In Splunk:

1. Settings → Data Inputs
2. Click **HTTP Event Collector**
3. Enable HEC
4. Click **New Token**

---

# Step 2 — Create Token

During setup:

* Name: `ai_patient_monitor`
* Index: `main`
* Source type: `ai-patient-monitor`
* Leave defaults
* Save

Copy the token.

---

# Step 3 — Verify HEC Is Listening

On Windows:

```powershell
netstat -ano | findstr :8088
```

You should see:

```
TCP 0.0.0.0:8088 LISTENING
```

---

# Step 4 — Test HEC Manually

```powershell
$uri="https://localhost:8088/services/collector"

$body = @{
  event = @{
    event_type = "test_event"
    app = "ai_patient_monitor"
    message = "hello test"
  }
} | ConvertTo-Json -Depth 6

Invoke-RestMethod -Method Post `
  -Uri $uri `
  -Headers @{Authorization="Splunk YOUR_TOKEN"} `
  -Body $body `
  -ContentType "application/json"
```

If you see:

```
Success 0
```

HEC is working.

---

# Step 5 — Verify in Splunk

```spl
index=main sourcetype="ai-patient-monitor"
```

You should see the test event.

---

# Step 6 — Configure App

Set environment variables and run:

```powershell
streamlit run er_monitor_app_splunk.py
```

Trigger AI actions.

---

# Step 7 — Confirm AI Events

```spl
index=main sourcetype="ai-patient-monitor"
| stats count by event_type
```

---

# Step 8 — Create Dashboard

1. Dashboards → Create New Dashboard
2. Edit → Source
3. Paste the working XML
4. Save

---

# What You’ve Built (Enterprise View)

You now have:

| Capability             | Description             |
| ---------------------- | ----------------------- |
| AI Observability       | Logs every LLM call     |
| Performance Monitoring | Tracks latency          |
| Cost Tracking          | Tracks tokens           |
| Reliability Monitoring | Tracks failures         |
| Clinical Risk Tracking | Tracks EMERGENCY events |
| Root Cause Analysis    | Filter by scenario      |
| Time-based Trending    | Full timechart support  |

This is how production AI systems are monitored in real enterprises.

---

# Bonus: Resume Anchor

If you ever need to restart this setup:

1. Enable HEC
2. Confirm port 8088 listening
3. Test with PowerShell
4. Set env vars
5. Trigger AI
6. Run:

   ```spl
   index=main sourcetype="ai-patient-monitor"
   ```

