# AI-Based Patient Monitor - Architecture Diagrams

## System Architecture (Mermaid)

### High-Level Architecture

```mermaid
graph TB
    subgraph UI["User Interface Layer"]
        A[Streamlit Web App]
    end
    
    subgraph APP["Application Layer"]
        B[CSV Parser<br/>Pandas]
        C[Clinical Rule Engine<br/>Condition Detection]
    end
    
    subgraph AI["AI/RAG Layer"]
        D[Context Builder]
        E[OpenAI API<br/>GPT-4o-mini]
        F[Response Processor]
    end
    
    subgraph OBS["Observability + Governance Layer"]
        G[Token Tracking]
        H[Latency Monitoring]
        I[Error Handling]
        J[Correlation IDs\n(pm_session_id / pm_run_id)]
        K[Local JSONL Archive]
        L[Splunk HEC Logger]
        M[Splunk REST Run Summary\n(Mgmt API 8089)]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    F --> H
    F --> I
    F --> J
    F --> K
    F --> L
    L --> M
    
    style UI fill:#1E2761,color:#fff
    style APP fill:#CADCFC,color:#333
    style AI fill:#84B59F,color:#fff
    style OBS fill:#F96167,color:#fff
```

### Data Flow Pipeline

```mermaid
flowchart LR
    A[CSV Upload/<br/>Sample Selection] --> B[Validation<br/>Column & Type Check]
    B --> C[Analysis<br/>Vitals Calculation]
    C --> D[Detection<br/>Rule Evaluation]
    D --> E{Abnormal?}
    E -->|Yes| F[RAG Processing]
    E -->|No| G[Display Normal Status]
    F --> H[OpenAI API Call]
    H --> I[Parse AI Response]
    I --> J[Display Actions]
    
    D --> K[Visual Outputs<br/>Charts & Metrics]
    I --> L[Observability<br/>Tokens & Latency]
    
    style A fill:#1E2761,color:#fff
    style B fill:#CADCFC,color:#333
    style C fill:#CADCFC,color:#333
    style D fill:#84B59F,color:#fff
    style E fill:#F96167,color:#fff
    style F fill:#84B59F,color:#fff
    style H fill:#F96167,color:#fff
```

### RAG Pipeline Detail

```mermaid
sequenceDiagram
    participant UI as Streamlit UI
    participant APP as Application
    participant RAG as RAG Engine
    participant LLM as OpenAI API
    participant OBS as Observability
    
    UI->>APP: Upload patient CSV
    APP->>APP: Validate columns
    APP->>APP: Detect conditions
    
    alt Abnormality Detected
        APP->>RAG: Build context
        Note over RAG: 1. Extract 60min vitals<br/>2. Format as CSV string<br/>3. Add diagnosis summary
        
        RAG->>LLM: Send prompt with context
        Note over LLM: System: Clinical AI<br/>User: Patient data + task
        
        LLM-->>RAG: Response with actions
        RAG->>OBS: Log tokens & latency
        RAG->>APP: Return parsed actions
        APP->>UI: Display AI suggestions
    else Normal Vitals
        APP->>UI: Display normal status
    end
    
    OBS->>UI: Show metrics
```

### Component Architecture

```mermaid
graph TD
    subgraph Frontend["Frontend Components"]
        A1[File Uploader]
        A2[Metric Cards]
        A3[Alert Banner]
        A6[Alarm Engine\n(Web Audio + Ack Flow)]
        A4[Trend Charts]
        A5[Action Display]
    end
    
    subgraph Backend["Backend Components"]
        B1[Session Manager]
        B2[CSV Parser]
        B3[Condition Detector]
        B4[MAP Calculator]
        B5[AI Cache]
    end
    
    subgraph AI["AI Components"]
        C1[Prompt Builder]
        C2[API Client]
        C3[Response Parser]
        C4[Token Counter]
        C5[Cost Estimator]
    end

    subgraph Gov["Governance / Observability"]
        G1[Correlation IDs]
        G2[Splunk HEC Client]
        G3[Local JSONL Archive]
        G4[Splunk REST Search Client]
    end

    subgraph Alert["Alerting"]
        A6[Alarm Engine\n(Web Audio + Ack Flow)]
    end
    
    subgraph Data["Data Layer"]
        D1[Patient CSV]
        D2[Sample Files]
        D3[Cache Store]
    end
    
    A1 --> B1
    A1 --> D1
    B1 --> B2
    B2 --> B3
    B3 --> B4
    B3 --> C1
    C1 --> C2
    C2 --> C3
    C3 --> C4
    C4 --> C5
    C5 --> G1
    G1 --> G2
    G1 --> G3
    G2 --> G4
    C3 --> B5
    B5 --> D3
    D2 --> B2
    
    style Frontend fill:#1E2761,color:#fff
    style Backend fill:#CADCFC,color:#333
    style AI fill:#84B59F,color:#fff
    style Data fill:#F96167,color:#fff
```

### Emergency Detection Logic

```mermaid
flowchart TD
    A[Analyze Latest Vitals] --> B{SpO₂ < 88%?}
    B -->|Yes| C[EMERGENCY:<br/>Respiratory Failure]
    B -->|No| D{SBP < 90 OR<br/>MAP < 65?}
    
    D -->|Yes| E[EMERGENCY:<br/>Hypotension]
    D -->|No| F{HR ≥ 160 OR<br/>ECG = V-tach?}
    
    F -->|Yes| G[EMERGENCY:<br/>Arrhythmia]
    F -->|No| H{Sepsis Score ≥ 3?}
    
    H -->|Yes| I[EMERGENCY:<br/>Suspected Sepsis]
    H -->|No| J{Any WARNING<br/>criteria?}
    
    J -->|Yes| K[WARNING:<br/>Monitor Closely]
    J -->|No| L[NORMAL:<br/>Continue Routine]
    
    subgraph Sepsis["Sepsis Criteria (Score 1 each)"]
        S1[Fever ≥38°C OR<br/>Hypothermia ≤36°C]
        S2[Tachycardia >100]
        S3[Hypotension SBP<100]
        S4[Hypoxemia SpO₂<94%]
    end
    
    style C fill:#F96167,color:#fff
    style E fill:#F96167,color:#fff
    style G fill:#F96167,color:#fff
    style I fill:#F96167,color:#fff
    style K fill:#F9E795,color:#333
    style L fill:#84B59F,color:#fff
```

---

## Usage in Documentation

You can embed these Mermaid diagrams in:
- GitHub README.md
- Markdown documentation
- Wiki pages
- Most modern documentation platforms

### Example:
\`\`\`markdown
## Architecture

\`\`\`mermaid
graph TB
    A[User] --> B[App]
    B --> C[AI]
\`\`\`
\`\`\`

---

## Diagram Formats Provided

1. **PowerPoint (.pptx)** - 5 professional slides with colored diagrams
2. **Mermaid (.md)** - 5 diagrams for GitHub/documentation
3. **SVG** - Coming next (vector graphics for high-quality printing)

---

## Color Palette Used

- **Navy (#1E2761)** - User Interface / Primary
- **Ice Blue (#CADCFC)** - Application Layer / Secondary  
- **Sage (#84B59F)** - AI/Success / Positive
- **Coral (#F96167)** - Alerts/Emergency / Attention

These colors create a professional medical/healthcare aesthetic.
