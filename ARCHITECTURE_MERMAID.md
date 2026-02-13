# AI-Based Patient Monitor — Mermaid Diagrams (GitHub-safe)

These diagrams avoid characters that sometimes break GitHub’s Mermaid renderer (parentheses right after a line break, etc.).

---

## 1) High-Level Architecture

```mermaid
graph TB
  subgraph UI["User Interface Layer"]
    UI1[Streamlit Web App]
  end

  subgraph APP["Application Layer"]
    APP1[CSV Parser<br>Pandas]
    APP2[Clinical Rule Engine<br>Detection and Severity]
  end

  subgraph AI["AI and RAG Layer"]
    AI1[Context Builder<br>Summary plus last 60 mins]
    AI2[OpenAI API<br>gpt-4o-mini]
    AI3[Response Processor<br>Structured Actions]
  end

  subgraph GOV["Observability and Governance"]
    GOV1[Token and Latency Tracking]
    GOV2[Correlation IDs<br>pm_session_id and pm_run_id]
    GOV3[Estimated Cost<br>per token]
    GOV4[Local JSONL Archive<br>optional]
    GOV5[Splunk HEC Logger<br>optional]
    GOV6[Splunk REST Run Summary<br>Mgmt API 8089 optional]
  end

  UI1 --> APP1 --> APP2 --> AI1 --> AI2 --> AI3 --> GOV1 --> GOV2
  GOV2 --> GOV3
  GOV2 --> GOV4
  GOV2 --> GOV5 --> GOV6
```

---

## 2) End-to-End Data Flow

```mermaid
flowchart LR
  DF1[CSV Upload<br>or Sample Select] --> DF2[Validate Columns<br>Parse Timestamp]
  DF2 --> DF3[Analyze Latest Vitals<br>Compute MAP]
  DF3 --> DF4[Rule Evaluation<br>Assign Severity]
  DF4 --> DF5{Abnormal?<br>WARNING or EMERGENCY}

  DF5 -->|No| DF6[Display Normal Status<br>Charts and Metrics]

  DF5 -->|Yes| DF7[Build RAG Context<br>Summary plus last 60 mins]
  DF7 --> DF8[LLM Call]
  DF8 --> DF9[Parse Actions<br>Immediate Monitoring Documentation Escalation]
  DF9 --> DF10[Display Actions<br>Download Action Plan]

  DF8 --> DF11[Log Telemetry<br>tokens latency success]
  DF11 --> DF12[Add Correlation IDs<br>Cost Estimate]
  DF12 --> DF13[Optional JSONL Archive]
  DF12 --> DF14[Optional Splunk HEC]
  DF14 --> DF15[Optional Splunk REST Summary]
```

---

## 3) RAG + Observability Sequence

```mermaid
sequenceDiagram
  participant U as User UI
  participant A as App
  participant R as RAG Context Builder
  participant L as LLM OpenAI API
  participant O as Observability and Governance

  U->>A: Upload CSV or select sample
  A->>A: Validate and parse data
  A->>A: Detect conditions and severity

  alt WARNING or EMERGENCY
    A->>R: Build context
    R->>L: Send prompt
    L-->>R: Structured action plan
    R-->>A: Return actions and usage
    A->>O: Log tokens latency success correlation IDs cost
    O-->>O: Optional JSONL archive
    O-->>O: Optional Splunk HEC event
    O-->>O: Optional REST run summary
    A-->>U: Render actions and observability
  else NORMAL
    A-->>U: Render normal status
  end
```

---

## 4) Component Architecture

```mermaid
graph TD
  subgraph FE["Frontend Streamlit"]
    FE1[File Uploader and Sample Buttons]
    FE2[Metrics and Trend Charts]
    FE3[Alert Banner and Ack Button]
    FE4[AI Action Plan Viewer<br>Download]
    FE5[Observability Widgets<br>Tokens and Latency]
  end

  subgraph BE["Backend"]
    BE1[Session State Manager]
    BE2[CSV Loader and Validator]
    BE3[Condition Detector<br>Rules and MAP]
    BE4[AI Cache<br>per patient timestamp]
  end

  subgraph LLM["AI and RAG"]
    LLM1[Prompt Builder]
    LLM2[OpenAI Client]
    LLM3[Response Parser]
  end

  subgraph GOV["Observability and Governance"]
    GOVa[Correlation IDs]
    GOVb[Telemetry Logger<br>latency tokens success]
    GOVc[Cost Estimator]
    GOVd[JSONL Archive optional]
    GOVe[Splunk HEC Client optional]
    GOVf[Splunk REST Search Client optional]
  end

  subgraph AL["Alerting"]
    AL1[Alarm Engine<br>Web Audio 3 beeps]
  end

  FE1 --> BE1 --> BE2 --> BE3
  BE3 --> FE2
  BE3 --> FE3
  FE3 --> AL1
  BE3 --> LLM1 --> LLM2 --> LLM3 --> FE4
  LLM3 --> BE4

  LLM3 --> GOVb --> GOVa
  GOVb --> GOVc
  GOVa --> GOVd
  GOVa --> GOVe --> GOVf
  GOVb --> FE5
```

---

## 5) Emergency Detection Logic

```mermaid
flowchart TD
  E1[Analyze Latest Vitals] --> E2{SpO2 < 88 percent?}
  E2 -->|Yes| E3[EMERGENCY<br>Respiratory Failure]
  E2 -->|No| E4{SBP < 90<br>or MAP < 65?}

  E4 -->|Yes| E5[EMERGENCY<br>Hypotension]
  E4 -->|No| E6{HR >= 160<br>or ECG contains V tach?}

  E6 -->|Yes| E7[EMERGENCY<br>Arrhythmia]
  E6 -->|No| E8{Sepsis Score >= 3?}

  E8 -->|Yes| E9[EMERGENCY<br>Suspected Sepsis]
  E8 -->|No| E10{Any WARNING criteria?}

  E10 -->|Yes| E11[WARNING<br>Monitor Closely]
  E10 -->|No| E12[NORMAL<br>Continue Routine]

  subgraph S["Sepsis Criteria 1 point each"]
    S1[Fever >= 38C<br>or <= 36C]
    S2[Tachycardia > 100]
    S3[SBP < 100]
    S4[SpO2 < 94 percent]
  end
```

