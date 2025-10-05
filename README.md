# Chord Analysis Interface

This repository provides a full-stack application designed for advanced musicians comfortable with Anglo-American chord notation. It includes:

- `/back`: a Python-based API providing chord analysis, mode detection, and intelligent substitution suggestions via AI.
- `/front`: a Vue 3 web interface for building, listening to, and analyzing chord progressions.

---

## 🎵 Overview

The interface enables musicians to:

- **Build custom chord grids** using a flexible editor
- **Play back progressions** with an integrated audio player
- **Analyze progressions via AI**, identifying their harmonic structure
- **Explore modal substitutions** and alternative reharmonizations for creative composition

This tool is intended as a powerful assistant for composition, arrangement, and harmonic exploration.

---

## 🗂 Structure

- **`/back`** – REST API with harmonic logic and AI-based analysis
- **`/front`** – Vue 3 client consuming the API, providing an interactive music UI

Each folder contains its own `README.md` with installation and usage instructions.

---

## 🚀 Getting Started

To run the project locally, clone the repository and setup project with:

```bash
git clone https://github.com/hourlier96/chords-analyzer.git
cd chords-analyzer
make install
make run
