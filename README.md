# TRH17 Geometric Design Evaluator

An automated Python tool built to parse Civil 3D LandXML data and evaluate road geometry against South African TRH17 standards. 

## 🚀 Features
* **LandXML Parser:** Bypasses proprietary CAD locks to extract raw chainages and elevations.
* **Vertical Math Engine:** Automatically calculates entering/exiting gradients and K-Values.
* **TRH17 Logic:** Evaluates alignments against localized maximum gradients and minimum K-Values.
* **Automated Reporting:** Generates a formatted `.xlsx` master report.

## 🛠️ Installation & Setup
Before running the tool, ensure you have the required Excel library installed:
```bash
python -m pip install openpyxl