import os
import time
import json
import uuid
import base64
import io
from typing import Optional, Dict, Any
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st
import requests
import streamlit.components.v1 as components

# ============================================================================
# SPLUNK AI OBSERVABILITY (HEC) - OPTIONAL / FAIL-OPEN
# ============================================================================
SPLUNK_HEC_URL = os.getenv("SPLUNK_HEC_URL", "").strip()
SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_HEC_TOKEN", "").strip()
SPLUNK_INDEX = os.getenv("SPLUNK_INDEX", "").strip()
SPLUNK_SOURCETYPE = os.getenv("SPLUNK_SOURCETYPE", "ai-patient-monitor").strip()
SPLUNK_MGMT_URL = os.getenv("SPLUNK_MGMT_URL", "").strip()
SPLUNK_USERNAME = os.getenv("SPLUNK_USERNAME", "").strip()
SPLUNK_PASSWORD = os.getenv("SPLUNK_PASSWORD", "").strip()


# --- Splunk Management API (8089) credentials for in-app run summary ---

# TLS verify for localhost demo (set PM_SPLUNK_VERIFY_TLS=1 to verify)
PM_SPLUNK_VERIFY_TLS = os.getenv("PM_SPLUNK_VERIFY_TLS", "0").strip() in ("1","true","TRUE","yes","YES")



def splunk_log(event: Dict[str, Any]):
    """Send a structured event to Splunk HEC. Fails open (never breaks the demo).

    Adds correlation ids (pm_session_id, pm_run_id) and optionally archives events locally as JSONL.
    """
    if not (SPLUNK_HEC_URL and SPLUNK_HEC_TOKEN):
        return

    # Enrich for correlation / investigation
    try:
        event = dict(event or {})
        event.setdefault("app", "ai_patient_monitor")
        event.setdefault("pm_session_id", st.session_state.get("pm_session_id"))
        event.setdefault("pm_run_id", st.session_state.get("pm_run_id"))
    except Exception:
        # If anything weird happens, don't break the demo
        return

    # Optional cost estimate (demo-friendly). Override with env var COST_PER_TOKEN.
    try:
        cost_per_token = float(os.getenv("COST_PER_TOKEN", "0.0000005"))
        tokens = event.get("tokens_total")
        if tokens is not None:
            tokens_f = float(tokens)
            event["estimated_cost_usd"] = round(tokens_f * cost_per_token, 6)
    except Exception:
        pass

    payload = {
        "time": time.time(),
        "host": os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME") or "unknown-host",
        "source": "streamlit",
        "sourcetype": SPLUNK_SOURCETYPE,
        "event": event,
    }
    if SPLUNK_INDEX:
        payload["index"] = SPLUNK_INDEX

    # Local JSONL archive (optional)
    try:
        log_path = os.getenv("PM_EVENT_LOG", "logs/events.jsonl").strip()
        if log_path:
            os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload) + "\n")
    except Exception:
        pass

    # TLS verification toggle (default: off for local demo)
    verify_tls = os.getenv("PM_SPLUNK_VERIFY_TLS", "0").strip() in ("1", "true", "TRUE", "yes", "YES")

    try:
        requests.post(
            SPLUNK_HEC_URL,
            headers={"Authorization": f"Splunk {SPLUNK_HEC_TOKEN}"},
            data=json.dumps(payload),
            timeout=2,
            verify=verify_tls,
        )
    except Exception:
        pass

# === PIL for local visuals ===
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
except ImportError:
    PIL_OK = False

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "alarm_beeped": False,
        "alert_ack": False,
        "alarm_last_beep_ts": 0.0,
        "sample_file": None,
        "auto_ai": True,
        "ai_cache": {},
        "last_llm_ok": None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================================================
# AUDIO ALERT SYSTEM
# ============================================================================
def play_3_beeps():
    """Plays 3 short beeps using Web Audio API with improved browser compatibility"""
    token = str(uuid.uuid4())
    components.html(
        f"""
        <div id="beep-container-{token}" style="display:none;"></div>
        <script>
        (function() {{
          try {{
            // Create or resume audio context
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (!AudioContext) {{
              console.error('Web Audio API not supported');
              return;
            }}
            
            const ctx = new AudioContext();
            
            // Resume audio context if suspended (browser autoplay policy)
            if (ctx.state === 'suspended') {{
              ctx.resume().then(() => {{
                playBeeps();
              }});
            }} else {{
              playBeeps();
            }}
            
            function playBeeps() {{
              function beep(startDelayMs, durationMs, freq) {{
                try {{
                  const osc = ctx.createOscillator();
                  const gain = ctx.createGain();
                  
                  osc.type = "sine";
                  osc.frequency.value = freq;
                  
                  // Louder volume for better audibility
                  gain.gain.setValueAtTime(0.001, ctx.currentTime);
                  gain.gain.exponentialRampToValueAtTime(0.5, ctx.currentTime + 0.01);
                  
                  osc.connect(gain);
                  gain.connect(ctx.destination);
                  
                  const startTime = ctx.currentTime + (startDelayMs / 1000);
                  const stopTime = startTime + (durationMs / 1000);
                  
                  osc.start(startTime);
                  gain.gain.exponentialRampToValueAtTime(0.001, stopTime);
                  osc.stop(stopTime);
                }} catch (e) {{
                  console.error('Error playing beep:', e);
                }}
              }}
              
              // 3 beeps: 200ms each, 200ms gaps (more distinct)
              beep(0,   200, 880);   // First beep
              beep(400, 200, 880);   // Second beep
              beep(800, 200, 880);   // Third beep
              
              console.log('Alarm beeps triggered');
            }}
          }} catch (error) {{
            console.error('Audio initialization error:', error);
          }}
        }})();
        </script>
        """,
        height=0,
    )

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="AI Based Patient Monitor", 
    layout="wide",
    page_icon="🩺"
)


# ============================================================================
# RUN / SESSION IDS (for observability correlation)
# ============================================================================
import uuid
if "pm_session_id" not in st.session_state:
    st.session_state.pm_session_id = str(uuid.uuid4())
if "pm_run_id" not in st.session_state:
    st.session_state.pm_run_id = str(uuid.uuid4())


# ============================================================================
# VISUAL STYLING
# ============================================================================
def inject_ward_background():
    """Inject custom CSS for ward-themed background"""
    bg_path = Path("assets/ward_bg.jpg")
    
    # Check if background image exists
    if bg_path.exists():
        bg_base64 = base64.b64encode(bg_path.read_bytes()).decode()
        bg_style = f'background-image: url("data:image/jpeg;base64,{bg_base64}");'
    else:
        # Fallback to solid color
        bg_style = 'background-color: #0e1117;'
    
    st.markdown(
        f"""
        <style>
        /* Dark base theme */
        html, body, [data-testid="stAppViewContainer"] {{
            background-color: #0e1117 !important;
        }}

        /* Background layer */
        body::before {{
            content: "";
            position: fixed;
            inset: 0;
            {bg_style}
            background-size: cover;
            background-position: center;
            opacity: 0.14;
            z-index: -1;
        }}

        /* Main content container */
        .block-container {{
            background: rgba(14, 17, 23, 0.78);
            border-radius: 14px;
            padding: 1.2rem;
        }}

        /* Sidebar styling */
        section[data-testid="stSidebar"] {{
            background: rgba(14, 17, 23, 0.90);
        }}

        /* Cards and metrics */
        div[data-testid="stMetric"],
        div[data-testid="stExpander"],
        div[data-testid="stAlert"] {{
            background: rgba(22, 27, 34, 0.85);
            border-radius: 10px;
            padding: 10px;
        }}
        
        /* Emergency banner animation */
        @keyframes blinker {{ 50% {{ opacity: 0; }} }}
        .alarm {{
            color: white;
            background: #d32f2f;
            padding: 14px 16px;
            border-radius: 12px;
            font-weight: 800;
            font-size: 20px;
            animation: blinker 1s linear infinite;
            text-align: center;
            box-shadow: 0 10px 25px rgba(211,47,47,0.35);
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_ward_background()

# ============================================================================
# UI COMPONENTS
# ============================================================================
def flashing_red_banner(text: str):
    """Display flashing red emergency banner"""
    st.markdown(f"<div class='alarm'>🚨 {text} 🚨</div>", unsafe_allow_html=True)

def status_chip(label: str, level: str):
    """Display status chip with color coding"""
    colors = {
        "NORMAL": "#2e7d32",
        "WARNING": "#ef6c00",
        "EMERGENCY": "#c62828"
    }
    html = (
        f"<div style='display:inline-block;padding:6px 10px;border-radius:999px;"
        f"background:{colors.get(level, '#455a64')};color:white;font-weight:700;'>"
        f"{label}: {level}</div>"
    )
    st.markdown(html, unsafe_allow_html=True)

# ============================================================================
# DATA ANALYSIS FUNCTIONS
# ============================================================================
def detect_conditions(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze patient vitals and detect abnormal conditions
    Returns diagnosis summary with severity level
    """
    latest = df.iloc[-1].to_dict()
    
    hr = latest.get("heart_rate_bpm", 0)
    temp = latest.get("temperature_c", 0)
    sbp = latest.get("bp_systolic_mmHg", 0)
    dbp = latest.get("bp_diastolic_mmHg", 0)
    spo2 = latest.get("spo2_percent", 100)
    ecg = latest.get("ECG", "")
    
    # Calculate Mean Arterial Pressure
    map_val = round(dbp + (sbp - dbp) / 3, 1) if sbp and dbp else None
    
    flags = []
    level = "NORMAL"
    diagnosis = "Normal vitals"
    
    # === EMERGENCY CONDITIONS ===
    # Severe hypoxemia
    if spo2 < 88:
        flags.append(f"CRITICAL: Severe hypoxemia (SpO₂ {spo2}%)")
        level = "EMERGENCY"
        diagnosis = "Respiratory failure"
    
    # Hypotension
    if sbp < 90 or (map_val and map_val < 65):
        flags.append(f"CRITICAL: Hypotension (SBP {sbp}, MAP {map_val})")
        if level != "EMERGENCY":
            level = "EMERGENCY"
        diagnosis = "Hemodynamic instability"
    
    # Suspected V-tach
    if hr >= 160 or "V-tach" in str(ecg):
        flags.append(f"CRITICAL: Suspected V-tach (HR {hr}, ECG {ecg})")
        level = "EMERGENCY"
        diagnosis = "Cardiac arrhythmia"
    
    # === SEPSIS DETECTION (multi-factor) ===
    sepsis_score = 0
    if temp >= 38.0 or temp <= 36.0:
        sepsis_score += 1
        flags.append(f"Fever/hypothermia (Temp {temp}°C)")
    if hr > 100:
        sepsis_score += 1
        flags.append(f"Tachycardia (HR {hr})")
    if sbp < 100:
        sepsis_score += 1
        flags.append(f"Low BP (SBP {sbp})")
    if spo2 < 94:
        sepsis_score += 1
        flags.append(f"Hypoxemia (SpO₂ {spo2}%)")
    
    if sepsis_score >= 3:
        level = "EMERGENCY"
        diagnosis = "Suspected sepsis"
        flags.append("⚠️ SEPSIS-LIKE PATTERN DETECTED")
    
    # === WARNING CONDITIONS ===
    if level != "EMERGENCY":
        if spo2 < 92:
            flags.append(f"Mild hypoxemia (SpO₂ {spo2}%)")
            level = "WARNING"
            diagnosis = "Respiratory concern"
        
        if hr > 120 or hr < 50:
            flags.append(f"Abnormal HR ({hr} bpm)")
            level = "WARNING"
            diagnosis = "Cardiac monitoring needed"
        
        if temp >= 37.8:
            flags.append(f"Elevated temperature ({temp}°C)")
            if level != "WARNING":
                level = "WARNING"
    
    return {
        "level": level,
        "diagnosis": diagnosis,
        "flags": flags,
        "latest": latest,
        "map": map_val
    }

def make_json_safe(obj: Any) -> Any:
    """Convert objects to JSON-safe format"""
    if isinstance(obj, dict):
        return {k: make_json_safe(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_safe(v) for v in obj]
    elif pd.isna(obj):
        return None
    elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)
    else:
        return obj

# ============================================================================
# AI/LLM INTEGRATION
# ============================================================================
def estimate_ai_confidence(summary: Dict, llm_ok: Optional[bool] = None) -> str:
    """Estimate AI confidence based on severity and LLM status"""
    level = summary.get("level", "NORMAL")
    flags = summary.get("flags") or []
    
    if level == "EMERGENCY":
        base = "High"
    elif level == "WARNING":
        base = "Medium"
    else:
        base = "Medium" if flags else "Low"
    
    # Downgrade if LLM failed
    if llm_ok is False:
        if base == "High":
            return "Medium"
        if base == "Medium":
            return "Low"
    
    return base

def render_token_viz(usage: Optional[Dict]):
    """Display token usage visualization"""
    if not usage:
        st.info("Token usage not available for this response.")
        return
    
    prompt = usage.get("prompt_tokens", 0)
    completion = usage.get("completion_tokens", 0)
    total = usage.get("total_tokens", 0)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Input Tokens", f"{prompt:,}")
    col2.metric("Output Tokens", f"{completion:,}")
    col3.metric("Total Tokens", f"{total:,}")
    
    # Visual bar
    if total > 0:
        prompt_pct = (prompt / total) * 100
        completion_pct = (completion / total) * 100
        
        st.markdown(
            f"""
            <div style="display:flex;width:100%;height:30px;border-radius:8px;overflow:hidden;">
                <div style="width:{prompt_pct}%;background:#1976d2;display:flex;align-items:center;justify-content:center;color:white;font-size:12px;">
                    Input
                </div>
                <div style="width:{completion_pct}%;background:#388e3c;display:flex;align-items:center;justify-content:center;color:white;font-size:12px;">
                    Output
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

def call_llm_actions(summary: Dict, df_tail: pd.DataFrame, source_name: Optional[str] = None) -> Dict:
    """
    Call LLM to generate nurse action suggestions based on patient data
    """
    # Get API credentials from environment or Streamlit secrets
    api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
    
    if not api_key:
        splunk_log({"event_type":"ai_inference","app":"ai_patient_monitor","scenario": source_name or "unknown","alert_level": summary.get("level","UNKNOWN"),"diagnosis": summary.get("diagnosis",""),"model": os.getenv("OPENAI_MODEL","gpt-4o-mini"),"success": False,"error":"No API key configured"})
        return {
            "ok": False,
            "error": "⚠️ No API key configured. Set OPENAI_API_KEY environment variable or add to Streamlit secrets.",
            "latency_s": 0,
            "usage": None,
            "text": None
        }
    
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Prepare data for LLM
    vitals_table = df_tail[["timestamp", "heart_rate_bpm", "temperature_c", 
                             "bp_systolic_mmHg", "bp_diastolic_mmHg", 
                             "spo2_percent", "ECG"]].to_csv(index=False)
    
    system = """You are an ICU clinical decision support AI. Based on patient vitals, suggest immediate nursing actions following standard ICU protocols.

Format your response as:
1. **Immediate Actions**: What to do RIGHT NOW
2. **Monitoring**: What to watch closely
3. **Documentation**: What to record
4. **Escalation**: When to call MD/Rapid Response

Be specific, practical, and protocol-driven."""

    user_content = {
        "task": "Analyze ICU vitals and suggest nurse actions",
        "patient_summary": make_json_safe(summary),
        "recent_vitals_csv": vitals_table
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_content, indent=2)}
        ],
        "temperature": 0.2
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    url = base_url.rstrip("/") + "/chat/completions"

    # --- Splunk AI observability context ---
    _scenario = source_name or (summary.get("latest", {}).get("patient_id") if isinstance(summary.get("latest", {}), dict) else None) or "unknown"
    _alert_level = summary.get("level", "UNKNOWN")
    _diagnosis = summary.get("diagnosis", "")
    _prompt_chars = len(system) + len(json.dumps(user_content))

    def _log_ai_event(ok: bool, latency_s: float, usage: Optional[Dict], status_code: Optional[int] = None, error: Optional[str] = None):
        splunk_log({
            "event_type": "ai_inference",
            "app": "ai_patient_monitor",
            "scenario": _scenario,
            "alert_level": _alert_level,
            "diagnosis": _diagnosis,
            "model": model,
            "latency_ms": int(latency_s * 1000),
            "status_code": status_code,
            "prompt_chars": _prompt_chars,
            "tokens_in": (usage or {}).get("prompt_tokens"),
            "tokens_out": (usage or {}).get("completion_tokens"),
            "tokens_total": (usage or {}).get("total_tokens"),
            "success": bool(ok),
            "error": error,
        })
    
    try:
        t0 = time.perf_counter()
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        latency = time.perf_counter() - t0
        
        if resp.status_code != 200:
            error_msg = resp.text[:300]
            _log_ai_event(False, latency, None, status_code=resp.status_code, error=f"LLM API error {resp.status_code}: {error_msg}")
            return {
                "ok": False,
                "error": f"LLM API error {resp.status_code}: {error_msg}",
                "latency_s": round(latency, 3),
                "usage": None,
                "text": None
            }
        
        data = resp.json()
        text_out = data["choices"][0]["message"]["content"]
        usage = data.get("usage")
        
        _log_ai_event(True, latency, usage, status_code=resp.status_code, error=None)
        return {
            "ok": True,
            "error": None,
            "latency_s": round(latency, 3),
            "usage": usage,
            "text": text_out
        }
    
    except requests.exceptions.Timeout:
        _log_ai_event(False, 60.0, None, status_code=None, error="Request timed out after 60 seconds")
        return {
            "ok": False,
            "error": "Request timed out after 60 seconds",
            "latency_s": 60.0,
            "usage": None,
            "text": None
        }
    except Exception as e:
        _log_ai_event(False, 0.0, None, status_code=None, error=f"Error calling LLM: {str(e)}")
        return {
            "ok": False,
            "error": f"Error calling LLM: {str(e)}",
            "latency_s": 0,
            "usage": None,
            "text": None
        }

# ============================================================================
# CONDITION VISUALIZATION
# ============================================================================
def get_cached_condition_image(patient_id: str, level: str) -> Optional[bytes]:
    """Generate or retrieve cached condition illustration"""
    if not PIL_OK:
        return None
    
    try:
        # Create simple visual indicator
        width, height = 520, 200
        
        if level == "EMERGENCY":
            color = (211, 47, 47)
            text = "⚠️ EMERGENCY"
        elif level == "WARNING":
            color = (239, 108, 0)
            text = "⚠️ WARNING"
        else:
            color = (46, 125, 50)
            text = "✓ NORMAL"
        
        img = Image.new('RGB', (width, height), (30, 30, 40))
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([10, 10, width-10, height-10], outline=color, width=5)
        
        # Add text
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Center text
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((width - text_width) // 2, (height - text_height) // 2)
        
        draw.text(position, text, fill=color, font=font)
        
        # Convert to bytes
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
    
    except Exception as e:
        st.warning(f"Could not generate condition image: {e}")
        return None

# ============================================================================
# MAIN APPLICATION
# ============================================================================
st.title("🩺 AI Based Patient Monitor (Prototype)")
st.caption("⚠️ Educational demo only. Not for clinical use. Follow facility protocols.")

# ============================================================================
# SIDEBAR - FILE UPLOAD & PATIENT SELECTION
# ============================================================================
with st.sidebar:
    st.header("📁 Load Patient Data")
    uploaded = st.file_uploader("Upload CSV (optional)", type=["csv"])
    
    st.markdown("### 🔍 Quick Load Samples")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Patient 1", use_container_width=True):
            st.session_state.sample_file = "patient1_sepsis.csv"
            st.session_state.ai_cache = {}
            play_3_beeps()
    
    with col2:
        if st.button("Patient 2", use_container_width=True):
            st.session_state.sample_file = "patient2_vtach.csv"
            st.session_state.ai_cache = {}
            play_3_beeps()
    
    with col3:
        if st.button("Patient 3", use_container_width=True):
            st.session_state.sample_file = "patient3_respfailure.csv"
            st.session_state.ai_cache = {}
            play_3_beeps()
    
    st.markdown("---")
    st.checkbox(
        "🤖 Auto-generate AI actions when abnormality detected",
        value=True,
        key="auto_ai"
    )
    
    st.markdown("---")
    if st.button("🔄 Reset Monitor / Clear Data", use_container_width=True):
        _sid = st.session_state.get("pm_session_id")
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        # preserve session id, start a new run
        st.session_state.pm_session_id = _sid or str(uuid.uuid4())
        st.session_state.pm_run_id = str(uuid.uuid4())
        st.rerun()

# ============================================================================
# LOAD DATA
# ============================================================================
df = None
source_name = None

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        source_name = uploaded.name
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
        st.stop()

elif st.session_state.get("sample_file") is not None:
    sample_path = st.session_state.sample_file
    if os.path.exists(sample_path):
        df = pd.read_csv(sample_path)
        source_name = sample_path
    else:
        st.error(f"Sample file not found: {sample_path}")
        st.info("💡 Make sure patient CSV files are in the same directory as app.py")
        st.stop()

if df is None:
    st.info("👈 Select a patient (1/2/3) or upload a CSV to begin monitoring.")
    st.stop()

# ============================================================================
# VALIDATE DATA
# ============================================================================
required_cols = [
    "patient_id", "timestamp", "ECG", "heart_rate_bpm",
    "temperature_c", "bp_systolic_mmHg", "bp_diastolic_mmHg", "spo2_percent"
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    st.error(f"❌ CSV is missing required columns: {', '.join(missing)}")
    st.info("Required columns: " + ", ".join(required_cols))
    st.stop()

# Convert timestamp
try:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
except Exception as e:
    st.warning(f"Could not parse timestamps: {e}")

# ============================================================================
# ANALYZE PATIENT DATA
# ============================================================================
summary = detect_conditions(df)

# ============================================================================
# DISPLAY HEADER METRICS
# ============================================================================
c1, c2, c3, c4, c5 = st.columns([2, 3, 2, 2, 2])

with c1:
    status_chip("Alert Level", summary["level"])

with c2:
    st.metric("Diagnosis", summary["diagnosis"])

with c3:
    map_val = summary["map"]
    st.metric("MAP (mmHg)", f"{map_val}" if map_val else "N/A")

with c4:
    last_time = df["timestamp"].iloc[-1]
    st.metric("Last Updated", str(last_time))

with c5:
    conf = estimate_ai_confidence(summary, llm_ok=st.session_state.get("last_llm_ok"))
    st.metric("AI Confidence", conf)

# ============================================================================
# CONDITION VISUALIZATION
# ============================================================================
if summary.get('level') in ['WARNING', 'EMERGENCY']:
    img_bytes = get_cached_condition_image(source_name, summary['level'])
    
    if img_bytes:
        st.markdown("### 📊 Condition Visual Indicator")
        col_a, col_b = st.columns([1, 2])
        
        with col_a:
            st.image(
                img_bytes,
                caption="Status indicator",
                use_container_width=True
            )
        
        with col_b:
            if summary["flags"]:
                st.warning("**Detected Issues:**")
                for flag in summary["flags"]:
                    st.write(f"• {flag}")

# ============================================================================
# EMERGENCY ALERT BANNER
# ============================================================================
# Reset acknowledgement when leaving emergency state
if summary["level"] != "EMERGENCY":
    st.session_state.alert_ack = False

if summary["level"] == "EMERGENCY" and not st.session_state.alert_ack:
    # Sound alarm with cooldown
    now = time.time()
    if now - st.session_state.alarm_last_beep_ts > 0.8:
        play_3_beeps()
        st.session_state.alarm_last_beep_ts = now
    
    splunk_log({"event_type":"clinical_alert","app":"ai_patient_monitor","scenario": source_name or "unknown","alert_level":"EMERGENCY","diagnosis": summary.get("diagnosis",""),"flags": summary.get("flags", [])})
    flashing_red_banner("EMERGENCY DETECTED — IMMEDIATE ACTION REQUIRED")
    
    if st.button("✅ Acknowledge Alert", type="primary"):
        st.session_state.alert_ack = True
        splunk_log({"event_type":"alert_acknowledged","app":"ai_patient_monitor","scenario": source_name or "unknown","alert_level":"EMERGENCY","diagnosis": summary.get("diagnosis","")})
        st.success("✓ Alert acknowledged. Continue monitoring per protocol.")
        st.rerun()

elif summary["level"] == "EMERGENCY" and st.session_state.alert_ack:
    st.info("✓ Emergency alert acknowledged. Monitor closely and follow protocols.")

# ============================================================================
# LATEST VITALS
# ============================================================================
st.subheader("📊 Latest Vitals (Most Recent Minute)")

latest = summary["latest"]
m1, m2, m3, m4, m5 = st.columns(5)

m1.metric("Heart Rate", f"{latest['heart_rate_bpm']} bpm")
m2.metric("Temperature", f"{latest['temperature_c']} °C")
m3.metric("Blood Pressure", f"{latest['bp_systolic_mmHg']}/{latest['bp_diastolic_mmHg']}")
m4.metric("SpO₂", f"{latest['spo2_percent']}%")
m5.metric("ECG", latest['ECG'])

# ============================================================================
# EXPLAINABILITY
# ============================================================================
with st.expander("🔍 Why This Alert? (Explainability)"):
    st.markdown("**Rule Triggers:**")
    if summary.get("flags"):
        for flag in summary["flags"]:
            st.write(f"• {flag}")
    else:
        st.write("• No abnormalities detected")
    
    st.markdown("**Latest Values:**")
    st.json(make_json_safe(summary.get("latest", {})))
    
    st.markdown("**Emergency Criteria:**")
    st.write("""
    - Severe hypoxemia: SpO₂ < 88%
    - Hypotension: SBP < 90 or MAP < 65
    - Suspected V-tach: HR ≥ 160 or V-tach ECG pattern
    - Sepsis pattern: 3+ of (fever/hypothermia, tachycardia, hypotension, hypoxemia)
    """)

# ============================================================================
# TREND CHARTS
# ============================================================================
st.subheader("📈 Trends (Last 60 Minutes)")

colA, colB = st.columns(2)

with colA:
    st.markdown("**Heart Rate & Oxygen**")
    st.line_chart(df.set_index("timestamp")[["heart_rate_bpm", "spo2_percent"]])

with colB:
    st.markdown("**Temperature & Blood Pressure**")
    st.line_chart(df.set_index("timestamp")[["temperature_c", "bp_systolic_mmHg", "bp_diastolic_mmHg"]])

# ============================================================================
# RAW DATA
# ============================================================================
with st.expander("📋 Show Raw Data (CSV)"):
    st.dataframe(df, use_container_width=True)

# ============================================================================
# AGENTIC AI - ACTION SUGGESTIONS
# ============================================================================
st.subheader("🤖 Agentic AI: Suggested Nurse Actions")
st.caption("Auto-generates LLM-powered action plan using RAG with patient CSV data.")

abnormal = summary["level"] in ["WARNING", "EMERGENCY"]

if not abnormal:
    st.info("✓ No abnormality detected — AI action plan not generated.")
else:
    # Create cache key
    last_ts = df["timestamp"].iloc[-1]
    cache_key = f"{source_name}|{summary['level']}|{summary['diagnosis']}|{str(last_ts)}"
    
    regen = st.button("🔄 Re-generate AI Action Plan")
    
    # Generate AI response if needed
    if (st.session_state.auto_ai and cache_key not in st.session_state.ai_cache) or regen:
        with st.spinner("🤖 Calling AI..."):
            df_tail = df.tail(60)
            result = call_llm_actions(summary, df_tail, source_name=source_name)
            st.session_state.last_llm_ok = bool(result.get("ok"))
        
        st.session_state.ai_cache[cache_key] = result
    else:
        result = st.session_state.ai_cache.get(cache_key)
    
    # Display results
    if not result:
        st.warning("⏳ AI action plan not generated yet. Click the button above.")
    else:
        # === AI OBSERVABILITY ===
        st.markdown("### 📊 AI Observability")
        
        obs_col1, obs_col2 = st.columns(2)
        
        with obs_col1:
            latency = result.get("latency_s", 0)
            st.metric("⏱️ Latency", f"{latency}s")
        
        with obs_col2:
            status = "✅ Success" if result.get("ok") else "❌ Failed"
            st.metric("Status", status)
        
        st.markdown("**Token Usage:**")
        render_token_viz(result.get("usage"))
        
        if result.get("usage"):
            with st.expander("📄 Raw Usage JSON"):
                st.json(result["usage"], expanded=False)
        
        st.markdown("---")
        
        # === AI-GENERATED ACTIONS ===
        if not result.get("ok"):
            st.error(f"❌ {result.get('error')}")
            
            if "API key" in str(result.get('error')):
                st.info("""
                **How to add your API key:**
                
                Option 1: Environment Variable
                ```bash
                export OPENAI_API_KEY='your-key-here'
                streamlit run app.py
                ```
                
                Option 2: Streamlit Secrets
                Create `.streamlit/secrets.toml`:
                ```toml
                OPENAI_API_KEY = "your-key-here"
                ```
                """)
        else:
            st.markdown("### 💡 Suggested Actions (AI-Generated)")
            st.markdown(result.get("text"))
            
            # Download action plan
            action_text = f"""
AI-BASED PATIENT MONITOR - ACTION PLAN
Generated: {pd.Timestamp.now()}
Patient: {source_name}

DIAGNOSIS: {summary['diagnosis']}
ALERT LEVEL: {summary['level']}

{result.get('text')}

---
This is an AI-generated suggestion. Follow facility protocols and clinical judgment.
"""
            st.download_button(
                label="📥 Download Action Plan",
                data=action_text,
                file_name=f"action_plan_{source_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("🏥 AI-Based Patient Monitor v2.0 | Educational Prototype | Not for clinical use")
st.sidebar.caption(f"Mgmt URL set: {bool(SPLUNK_MGMT_URL)}")
st.sidebar.caption(f"Mgmt URL set: {bool(os.getenv('SPLUNK_MGMT_URL'))}")
st.sidebar.caption(f"Username set: {bool(SPLUNK_USERNAME)}")
st.sidebar.caption(f"Password set: {bool(SPLUNK_PASSWORD)}")
# ==========================================================
# Splunk REST Search (Management API 8089) — for in-app summaries
# ==========================================================

def splunk_rest_enabled() -> bool:
    return bool(SPLUNK_MGMT_URL and SPLUNK_USERNAME and SPLUNK_PASSWORD)

def run_splunk_search(query: str, earliest: str = "-60m", latest: str = "now", timeout_s: int = 20) -> List[Dict[str, Any]]:
    """
    Run a Splunk search via Management API and return results (JSON rows).
    Note: For localhost demos, PM_SPLUNK_VERIFY_TLS=0 is fine; production should verify TLS.
    """
    jobs_url = f"{SPLUNK_MGMT_URL}/services/search/jobs"
    # Splunk expects 'search' prefixed with 'search ' if using raw SPL
    data = {
        "search": f"search {query}",
        "earliest_time": earliest,
        "latest_time": latest,
        "output_mode": "json",
        "exec_mode": "normal",
    }

    r = requests.post(jobs_url, data=data, auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD), verify=PM_SPLUNK_VERIFY_TLS, timeout=10)
    r.raise_for_status()

    try:
        sid = r.json().get("sid")
    except Exception:
        sid = None
    if not sid:
        raise RuntimeError("Splunk did not return a search job SID (sid).")

    job_url = f"{SPLUNK_MGMT_URL}/services/search/jobs/{sid}"
    t0 = time.time()
    while True:
        jr = requests.get(job_url, params={"output_mode": "json"}, auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
                          verify=PM_SPLUNK_VERIFY_TLS, timeout=10)
        jr.raise_for_status()
        payload = jr.json()
        entry = (payload.get("entry") or [{}])[0]
        content = entry.get("content", {})
        if content.get("isDone") is True or content.get("dispatchState") == "DONE":
            break
        if time.time() - t0 > timeout_s:
            raise TimeoutError("Timed out waiting for Splunk search completion.")
        time.sleep(0.6)

    results_url = f"{SPLUNK_MGMT_URL}/services/search/jobs/{sid}/results"
    rr = requests.get(results_url, params={"output_mode": "json", "count": 0}, auth=(SPLUNK_USERNAME, SPLUNK_PASSWORD),
                      verify=PM_SPLUNK_VERIFY_TLS, timeout=10)
    rr.raise_for_status()
    return rr.json().get("results") or []

def get_demo_run_summary(pm_run_id: str) -> Dict[str, Any]:
    """
    Summarize this demo run using pm_run_id correlation.
    Looks back 24h to avoid time-range surprises during demos.
    """
    base = f'index={SPLUNK_INDEX} sourcetype="{SPLUNK_SOURCETYPE}" pm_run_id="{pm_run_id}"'

    q_ai = base + ' event_type="ai_inference" ' \
        '| eval latency_ms=tonumber(latency_ms) ' \
        '| eval tokens_total=tonumber(tokens_total) ' \
        '| eval est=tonumber(estimated_cost_usd) ' \
        '| eval s=case(success="true",1, success=1,1, true(),0) ' \
        '| stats count as ai_calls sum(s) as successes ' \
        '       avg(latency_ms) as avg_latency_ms p95(latency_ms) as p95_latency_ms ' \
        '       sum(tokens_total) as tokens_sum sum(est) as est_cost_usd'

    rows = run_splunk_search(q_ai, earliest="-24h", latest="now")
    ai = rows[0] if rows else {}

    q_em = base + ' event_type="clinical_alert" alert_level="EMERGENCY" | stats count as emergency_count'
    rows2 = run_splunk_search(q_em, earliest="-24h", latest="now")
    em = rows2[0] if rows2 else {}

    def _to_int(v, default=0):
        try:
            return int(float(v))
        except Exception:
            return default

    def _to_float(v, default=0.0):
        try:
            return float(v)
        except Exception:
            return default

    ai_calls = _to_int(ai.get("ai_calls"), 0)
    successes = _to_int(ai.get("successes"), 0)
    failures = max(ai_calls - successes, 0)
    success_rate = round((100.0 * successes / ai_calls), 2) if ai_calls else 0.0

    return {
        "ai_calls": ai_calls,
        "successes": successes,
        "failures": failures,
        "success_rate_pct": success_rate,
        "avg_latency_ms": _to_int(ai.get("avg_latency_ms"), 0),
        "p95_latency_ms": _to_int(ai.get("p95_latency_ms"), 0),
        "tokens_sum": _to_int(ai.get("tokens_sum"), 0),
        "est_cost_usd": round(_to_float(ai.get("est_cost_usd"), 0.0), 4),
        "emergency_count": _to_int(em.get("emergency_count"), 0),
    }
