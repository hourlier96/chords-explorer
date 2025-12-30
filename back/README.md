# Chords generator

From a chord progression, provide an exhaustive analysis of each chord, including its quality, borrowed chords, substitutions and more !

Tonic & mode detection are made by calling Gemini model

## Workflow

```mermaid
flowchart TD
    %% Entrée HTTP
    Start[Client POST /analyze] --> Main["back/app/main.py"]
    Main --> B["services.analysis: get_analysis_data"]

    %% Analyse Globale et Détection de Mode
    subgraph S1["Analyse & IA"]
        B --> B1["utils.mode_detection_gemini: detect_tonic_and_mode"]
        B1 --> Gemini[Call Gemini API]
        Gemini --> B1
    end

    %% Analyse par segments
    subgraph S2["Segmentation & Contexte"]
        B1 --> B2["services.analysis: analyze_progression_segments"]
        B2 --> C1["For each segment: analyze_chord_in_context"]
    end

    %% Analyse unitaire des accords
    subgraph S3["Logiciel d'Analyse d'Accord (chords_analyzer.py)"]
        C1 --> D1["utils.common: parse_chord"]
        C1 --> D2["Calcul Intervalle (CHROMATIC_DEGREES_MAP)"]
        C1 --> D3["utils.common: is_chord_diatonic"]
        D1 & D2 & D3 --> C1
    end

    %% Utilitaires
    subgraph S_Utils["Utils & Constants"]
        U1["get_note_index"]
        U2["get_scale_notes"]
        U3["format_numeral"]
    end
    C1 -.-> S_Utils

    %% Post-Traitement & Enrichissement
    subgraph S4["Enrichissement des données"]
        B2 --> E1["fill_interface_data"]
        E1 --> E2["get_borrowed_chords"]
    end

    %% Substitutions et Harmonisation
    subgraph S5["Moteur de Substitution"]
        E2 --> G1["modal_substitution: get_substitutions"]
        G1 --> G2["secondary_dominant: get_secondary_dominant"]
        G1 --> G3["tritone_substitution: get_tritone_substitute"]

        G1 & G2 & G3 --> H["Harmonisation & Analyse des nouveaux accords"]
        H -->|Recursion sur analyze_chord_in_context| C1
    end

    %% Résultat final
    H --> Final["Main.py: Final JSON Response"]

    Final --- Result{{tonic, explanations, quality_analysis, substitutions, secondary_dom}}
```

## Installation

Install requirements.txt dependencies first with:

```bash
uv venv
source .venv/bin/activate
uv pip compile pyproject.toml --extra dev -o requirements.txt
uv pip install -r requirements.txt
cd ../ && pre-commit install
```

## Run

```bash

uvicorn app.main:app --reload
```

## Tests

```bash
python3 -m pytest
```

## CI

Linting & Tests

Test locally with act:

act -j <job_name> --rm -W .github/workflows/ci.yaml
