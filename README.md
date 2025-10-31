
# Scene Builder Agent 

An intelligent **AI-powered scene planning system** that generates cinematic scene structures (JSON blueprints) from natural language prompts using **Gemini 2.5 Flash**.  
Built with **FastAPI**, it transforms user prompts into structured scene data suitable for media pipelines, video generation, or storyboarding.

---

##  Features

- Converts **natural language prompts** into detailed **scene JSON** (with scenes, actions, and transitions).  
- Supports **Gemini 2.5 Flash** for high-speed reasoning.  
- Implements **schema validation** via Pydantic (`SceneSchema`) for strict structure compliance.  
- Includes **robust normalization** to clean and repair malformed LLM outputs.  
- Provides **two ways to test the API:**  
  - via **Swagger UI**
  - via **cURL / CLI**  
- Extensible and modular file structure (`pipeline.py`, `scene.py`, `schema.py`, etc.)

---

##  Folder Structure

```
scene_builder/
│
├── main.py             # FastAPI entrypoint — starts the application server
├── pipeline.py         # Core pipeline — integrates LLM & scene normalization logic
├── scene.py            # Scene modeling and schema-to-object conversions
├── schema.py           # Pydantic schema validation for structured outputs
├── utils/              # Utility helpers (logger, config loader)
└── README.md           
```

---

##  Setup

### 1. Clone the Repository 
```bash
git clone https://github.com/not2511/Scene-Builder
cd Scene-Builder
```
### 2. Create and activate virtual environment

```bash
python -m venv scene-builder
source scene-builder/bin/activate     # Linux/Mac
scene-builder\Scripts\activate      # Windows PowerShell
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key


Store it in a `.env` file:

```
GOOGLE_API_KEY=your_api_key_here
```

---

##  Running the Server

Launch the FastAPI app using **Uvicorn**:

```bash
uvicorn src.main:app --reload
```

Once running, you’ll see:

```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

##  Testing the API

### Option 1: **Swagger UI**

Visit:

```
http://127.0.0.1:8000/docs
```

In the Swagger interface:
- Expand `POST /v1/agent/scene`
- Click **Try it out**
- Use the sample body below and **Execute**:

```json
{
  "prompt": "Create a 10-second cinematic intro about teamwork with inspirational music",
  "constraints": {
    "totalDurationSec": 10,
    "aspectRatio": "16:9",
    "fps": 30,
    "language": "en",
    "deterministic": false
  }
}
```

You should get a structured `SceneSchema` JSON response containing all generated scenes.

---

### Option 2: **cURL / Command Line**

```bash
curl -X POST "http://127.0.0.1:8000/v1/agent/scene" -H "Content-Type: application/json" -d "{"prompt": "Create a 10-second cinematic video about teamwork with inspirational music", "constraints": {"totalDurationSec": 10, "aspectRatio": "16:9", "fps": 30, "language": "en", "deterministic": false}}"
```

Expected response (shortened):

```json
{
  "plan": {
    "scenesCount": 3,
    "notes": "Generated 3 scene(s) from prompt",
    "prompt": "Create a 10-second cinematic video about teamwork..."
  },
  "scene": {
    "scenes": [
      {
        "id": "scene_01",
        "title": "The Midnight Push",
        "durationSec": 3.5,
        ...
      }
    ]
  }
}
```

---

##  Key Files Explained

### `main.py`
Defines FastAPI routes, startup configuration, and handles requests to the `/v1/agent/scene` endpoint.

### `pipeline.py`
Handles prompt processing, calls the **Gemini 2.5 Flash** model, parses the JSON output, and normalizes it into the `SceneSchema` format.

### `scene.py`
Contains models and logic for handling scene construction — rows, actions, transitions, and effects.

### `schema.py`
Defines all **Pydantic validation schemas** for consistent output, ensuring every generated response passes type checks.

---

##  Error Handling

Common issues & resolutions:

| Error | Cause | Fix |
|-------|--------|-----|
| `422 Unprocessable Entity` | Invalid request or malformed JSON | Validate JSON structure or check `.env` key |
| `No API_KEY or ADC found` | Missing Google API Key | Set `GOOGLE_API_KEY` as shown above |
| `Empty output / Invalid LLM response` | Gemini returned non-JSON | Check `_normalize_to_scene_schema` and ensure JSON parsing section is intact |

---

##  Project Goals

✅ Build an **end-to-end prototype** for AI-driven cinematic scene generation.  
✅ Maintain **schema validity and creative fidelity**.  
✅ Make system **LLM-agnostic and pluggable** for future models.  
✅ Ensure the output can serve as input to **media generation pipelines**.

---

##  License

This project is for **educational and research use** under the Synorus internship assignment.  
All rights reserved © 2025.

---

##  Author

**Ranjot Singh**    
Project: *Scene Builder Agent (Gemini 2.5 Flash)*

