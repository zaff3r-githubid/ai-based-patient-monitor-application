# 🩺 AI-Based Patient Monitor

> **Intelligent ICU Patient Monitoring System with AI-Powered Clinical Decision Support**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Data Format](#data-format)
- [AI Capabilities](#ai-capabilities)
- [Project Structure](#project-structure)
- [Security](#security)
- [Assignment Details](#assignment-details)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## 🎯 Overview

AI-Based Patient Monitor is an intelligent ICU monitoring prototype that uses **Retrieval Augmented Generation (RAG)** to analyze patient vital signs and provide real-time clinical decision support. The system monitors critical parameters including ECG, heart rate, blood pressure, temperature, and oxygen saturation, detecting life-threatening conditions and suggesting evidence-based nursing interventions.

### Key Capabilities

- 🔍 **Real-time Vital Sign Analysis** - Continuous monitoring of 8 critical parameters
- 🚨 **Emergency Detection** - Identifies sepsis, V-tach, respiratory failure, and hemodynamic instability
- 🤖 **AI-Powered Suggestions** - LLM-generated clinical action plans using RAG
- 📊 **Visual Analytics** - Interactive trend charts and condition indicators
- 🔔 **Alert System** - Audio/visual alarms with acknowledgment workflow
- 📈 **AI Observability** - Token usage tracking and latency monitoring

---

## ✨ Features

### Clinical Features

| Feature | Description |
|---------|-------------|
| **Multi-Parameter Monitoring** | ECG, HR, BP, Temp, SpO₂ tracking |
| **Condition Detection** | Sepsis, arrhythmia, respiratory failure |
| **Severity Classification** | NORMAL → WARNING → EMERGENCY |
| **MAP Calculation** | Automated Mean Arterial Pressure computation |
| **Trend Analysis** | 60-minute rolling window visualization |
| **Explainability** | Rule-based trigger explanation |

### Technical Features

| Feature | Description |
|---------|-------------|
| **RAG Integration** | Patient CSV data as context for LLM |
| **OpenAI API** | GPT-4o-mini for clinical decision support |
| **Streamlit UI** | Professional medical-themed interface |
| **Session Management** | Cached AI responses for performance |
| **Error Handling** | Graceful degradation without API key |
| **Token Visualization** | Input/output token usage metrics |

---

## 🎥 Demo

**[Insert Demo Video Link Here]**

### Sample Screenshots

```
┌─────────────────────────────────────────┐
│  🩺 AI Based Patient Monitor            │
│  ─────────────────────────────────────  │
│  Alert: EMERGENCY | Diagnosis: Sepsis   │
│  MAP: 58 | Updated: 10:45 | Conf: High  │
├─────────────────────────────────────────┤
│  🚨 EMERGENCY DETECTED 🚨               │
│  IMMEDIATE ACTION REQUIRED              │
├─────────────────────────────────────────┤
│  Latest Vitals:                         │
│  HR: 135 | Temp: 38.9°C | BP: 85/50    │
│  SpO₂: 89% | ECG: Sinus Tach            │
├─────────────────────────────────────────┤
│  🤖 AI Suggested Actions:               │
│  1. Notify MD immediately               │
│  2. Start broad-spectrum antibiotics    │
│  3. Increase O₂ to 6L/min              │
│  4. Prepare for possible septic shock   │
└─────────────────────────────────────────┘
```

---

## 🏗️ System Architecture

```
┌──────────────────┐
│  User Interface  │
│   (Streamlit)    │
└────────┬─────────┘
         │
         ↓
┌─────────────────────────────────────────┐
│         Application Layer               │
│  ┌─────────────┐    ┌────────────────┐ │
│  │ Data Parser │    │ Condition      │ │
│  │ (CSV/Pandas)│    │ Detector       │ │
│  └──────┬──────┘    └────┬───────────┘ │
│         │                │              │
│         ↓                ↓              │
│  ┌──────────────────────────────────┐  │
│  │   Clinical Rule Engine           │  │
│  │   - Sepsis detection             │  │
│  │   - Arrhythmia identification    │  │
│  │   - Respiratory assessment       │  │
│  └──────────────┬───────────────────┘  │
└─────────────────┼──────────────────────┘
                  │
                  ↓
┌──────────────────────────────────────────┐
│          AI/RAG Layer                    │
│  ┌────────────────┐  ┌────────────────┐ │
│  │ Context Builder│→ │ OpenAI API     │ │
│  │ (Patient Data) │  │ (GPT-4o-mini)  │ │
│  └────────────────┘  └────┬───────────┘ │
│                           │              │
│  ┌────────────────────────┴──────────┐  │
│  │  LLM Response Processing          │  │
│  │  - Action extraction              │  │
│  │  - Token tracking                 │  │
│  │  - Latency measurement            │  │
│  └───────────────────────────────────┘  │
└──────────────────────────────────────────┘
                  │
                  ↓
┌──────────────────────────────────────────┐
│        Observability Layer               │
│  - Token usage (input/output)            │
│  - Response latency                      │
│  - Success/failure metrics               │
└──────────────────────────────────────────┘
```

### Workflow

1. **Data Ingestion**: CSV file uploaded or sample patient selected
2. **Validation**: Column presence and data type verification
3. **Analysis**: Rule-based condition detection (sepsis, V-tach, etc.)
4. **Classification**: Severity assignment (NORMAL/WARNING/EMERGENCY)
5. **RAG Preparation**: Patient data converted to context for LLM
6. **AI Processing**: OpenAI API generates clinical action plan
7. **Presentation**: Results displayed with alerts and visualizations
8. **Observability**: Token usage and latency tracked

---

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/ai-patient-monitor.git
cd ai-patient-monitor
```

### Step 2: Install Dependencies

**For Windows:**
```bash
pip install -r requirements_windows.txt
```

**For Mac/Linux:**
```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key

**Option A: Environment Variable (Recommended)**

*Windows PowerShell:*
```powershell
$env:OPENAI_API_KEY="sk-your-api-key-here"
```

*Windows CMD:*
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
```

*Mac/Linux:*
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Option B: Streamlit Secrets (For Development)**

Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "sk-your-api-key-here"
```

⚠️ **IMPORTANT**: Never commit `secrets.toml` to GitHub! Use `.gitignore`.

### Step 4: Run Application

```bash
streamlit run er_monitor_app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📊 Usage

### Quick Start

1. **Launch the app** using the command above
2. **Select a patient** from the sidebar (Patient 1, 2, or 3)
3. **View diagnosis** and alert level in the header
4. **Review AI suggestions** in the Agentic AI section
5. **Acknowledge alerts** if EMERGENCY is detected

### Loading Custom Data

1. Click **"Upload CSV"** in the sidebar
2. Select a properly formatted patient CSV file
3. App automatically validates and analyzes the data

### Understanding Alerts

| Level | Indicator | Meaning |
|-------|-----------|---------|
| 🟢 **NORMAL** | Green chip | All vitals within acceptable ranges |
| 🟡 **WARNING** | Orange chip | Minor abnormalities detected |
| 🔴 **EMERGENCY** | Red flashing banner | Critical condition requiring immediate intervention |

### AI-Generated Actions

When abnormalities are detected, the AI provides:

- **Immediate Actions** - What to do RIGHT NOW
- **Monitoring** - Parameters to watch closely
- **Documentation** - What to record in patient chart
- **Escalation** - When to notify MD/activate rapid response

---

## 📁 Data Format

### Required CSV Columns

Patient CSV files must include these exact column names:

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| `patient_id` | string | - | Unique patient identifier |
| `timestamp` | datetime | - | Reading timestamp (ISO 8601) |
| `ECG` | string | - | ECG interpretation (e.g., "Normal", "V-tach") |
| `heart_rate_bpm` | integer | 40-200 | Heart rate in beats per minute |
| `temperature_c` | float | 35.0-42.0 | Core temperature in Celsius |
| `bp_systolic_mmHg` | integer | 60-220 | Systolic blood pressure |
| `bp_diastolic_mmHg` | integer | 40-130 | Diastolic blood pressure |
| `spo2_percent` | integer | 70-100 | Oxygen saturation percentage |

### Sample Data

```csv
patient_id,timestamp,ECG,heart_rate_bpm,temperature_c,bp_systolic_mmHg,bp_diastolic_mmHg,spo2_percent
P001,2024-02-08 10:00:00,Normal,75,37.0,120,80,98
P001,2024-02-08 10:01:00,Normal,78,37.1,118,79,98
P001,2024-02-08 10:02:00,Sinus Tach,95,37.5,115,77,97
```

### Included Sample Patients

1. **patient1_sepsis.csv** - Septic deterioration pattern
   - Progressive fever + tachycardia + hypotension + hypoxemia
   
2. **patient2_vtach.csv** - Ventricular tachycardia episode
   - Sudden onset sustained V-tach at HR ≥160
   
3. **patient3_respfailure.csv** - Progressive respiratory failure
   - Declining SpO₂ over 60-minute period

---

## 🤖 AI Capabilities

### RAG (Retrieval Augmented Generation)

The system uses RAG to provide context-aware clinical decision support:

1. **Retrieval**: Patient CSV data is loaded and parsed
2. **Augmentation**: Recent vitals (last 60 minutes) are formatted as context
3. **Generation**: LLM receives patient summary + vitals and generates actions

### Prompt Engineering

**System Prompt:**
```
You are an ICU clinical decision support AI. Based on patient vitals, 
suggest immediate nursing actions following standard ICU protocols.

Format your response as:
1. Immediate Actions: What to do RIGHT NOW
2. Monitoring: What to watch closely
3. Documentation: What to record
4. Escalation: When to call MD/Rapid Response
```

**User Prompt:**
```json
{
  "task": "Analyze ICU vitals and suggest nurse actions",
  "patient_summary": {
    "level": "EMERGENCY",
    "diagnosis": "Suspected sepsis",
    "flags": ["Fever", "Tachycardia", "Hypotension", "Hypoxemia"]
  },
  "recent_vitals_csv": "..."
}
```

### AI Observability

The app tracks:
- **Latency**: Response time in seconds
- **Input Tokens**: Prompt length
- **Output Tokens**: Response length
- **Total Tokens**: Sum (affects API cost)
- **Success Rate**: API call reliability

---

## 📂 Project Structure

```
ai-patient-monitor/
├── er_monitor_app.py              # Main Streamlit application
├── requirements.txt             # Python dependencies (Mac/Linux)
├── requirements_windows.txt     # Python dependencies (Windows)
├── .gitignore                   # Git ignore rules (protects secrets)
├── secrets.toml.example         # API key format example
├── README.md                    # This file
├── GITHUB_SECURITY_GUIDE.md     # Security best practices
├── WINDOWS_INSTALL_GUIDE.md     # Windows-specific setup
├── CHANGES_COMPARISON.md        # Code improvements documentation
├── patient1_sepsis.csv          # Sample patient data (sepsis)
├── patient2_vtach.csv           # Sample patient data (V-tach)
├── patient3_respfailure.csv     # Sample patient data (resp failure)
└── assets/                      # Optional assets
    └── ward_bg.jpg              # Background image (optional)
```

---

## 🔒 Security

### API Key Protection

⚠️ **NEVER** commit your OpenAI API key to GitHub!

**Safe Practices:**

1. ✅ Use `.gitignore` to exclude `secrets.toml`
2. ✅ Use environment variables for production
3. ✅ Include only `secrets.toml.example` in repo
4. ✅ Set API spending limits in OpenAI dashboard
5. ✅ Revoke keys immediately if exposed

**Check Before Committing:**
```bash
git status
# Verify secrets.toml is NOT listed
```

See [GITHUB_SECURITY_GUIDE.md](GITHUB_SECURITY_GUIDE.md) for detailed instructions.

---

## 📚 Assignment Details

### Course Information

- **Course**: AI Practitioner Crash Course
- **Assignment**: #8 - AI Based Patient Monitor
- **Type**: Individual project
- **Tools Allowed**: ChatGPT, Claude, Gemini, DeepSeek, etc.

### Grading Rubric

| Component | Points | Status |
|-----------|--------|--------|
| Patient CSV files (3 files with conditions) | 25 | ✅ Included |
| Working app with RAG-based diagnosis | 25 | ✅ Implemented |
| Agentic AI with LLM-generated actions | 25 | ✅ Implemented |
| Creativity and demo quality | 15 | ✅ Enhanced UX |
| AI Observability (tokens, latency) | 5 | ✅ Full tracking |
| AI Architecture diagram | 5 | ✅ Documented |
| **TOTAL** | **100** | |

### Key Requirements Met

✅ **Part 1**: Three patient CSV files with minute-by-minute vitals  
✅ **Part 2**: Streamlit app reads CSV and displays diagnosis  
✅ **Part 3**: Agentic AI generates nurse actions using LLM API  
✅ **Part 4**: Token usage and latency observability  
✅ **Part 5**: Architecture workflow diagram  
✅ **Bonus**: Enhanced error handling, download features, professional UI  

---

## ⚠️ Disclaimer

**FOR EDUCATIONAL PURPOSES ONLY**

This application is a **prototype** designed for academic demonstration. It is **NOT** intended for clinical use and should **NEVER** be used in actual patient care settings.

- ❌ Not FDA approved
- ❌ Not clinically validated
- ❌ Not HIPAA compliant
- ❌ AI suggestions may be incorrect
- ❌ Does not replace clinical judgment

**Always follow facility protocols and consult licensed healthcare professionals for patient care decisions.**

---

## 📄 License

This project is licensed under the MIT License - see below for details:

```
MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **OpenAI** - GPT-4o-mini API for clinical decision support
- **Streamlit** - Web application framework
- **Pandas** - Data manipulation library
- **Course Instructors** - AI Practitioner Crash Course guidance
- **ChatGpt and Claude (Anthropic)** - Code improvement assistance

---

## 📞 Contact

**Student**: [Zafar Adil]  
**Email**: [zafaradil@ungmail.com]  
**GitHub**: [@zaff3r-githubid](https://github.com/zaff3r-githubid)  
**Course**: AI Practitioner Crash Course  

---

## 🔄 Version History

- **v2.0** (2024-02-08) - Improved version with enhanced error handling
- **v1.0** (2024-02-07) - Initial release

---

<div align="center">

**Made with ❤️ for Healthcare AI Education**

[![GitHub](https://img.shields.io/badge/GitHub-View_Repository-black?logo=github)](https://github.com/yourusername/ai-patient-monitor)
[![Demo](https://img.shields.io/badge/YouTube-Watch_Demo-red?logo=youtube)](https://youtube.com/your-demo-link)

</div>
