# Space-Mission-Analysis
# 🚀 Space Missions Exploratory Data Analysis (EDA) Dashboard

An interactive, web-based analytics dashboard built with **Streamlit** and **Plotly** to explore historical space launch data from 1957 to 2020. This project allows users to inspect trends, launch frequency, costs, and success rates across global space agencies and private companies.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Plotly](https://img.shields.io/badge/Plotly-5.15+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📌 Features

* **Live Interactive Filtering:** Filter space missions dynamically by Year Range, Organization, Country, and Mission Outcome.
* **Keyword Search:** Search specific mission payloads or detail keywords (e.g., *Falcon 9*, *Apollo*, *Starlink*) in real time.
* **Key Metrics Summary (KPIs):** Instant view of total launches, overall success rate, active vs. retired rockets, and spending analytics.
* **Interactive Visualizations:**
  * **Timeline Analytics:** Stacked annual launch volume and success share breakdown.
  * **Leaderboards:** Top launch organizations and country activity maps.
  * **Financial Distribution:** Price distributions and average mission cost comparisons.
* **Data Explorer & Export:** Dynamic column selection with one-click filtered CSV export functionality.

---

## 📂 Project Structure

```text
space-mission-eda/
├── app.py                  # Main Streamlit application
├── space_mission_data.csv  # Space launch dataset
├── requirements.txt        # Python dependency list
└── README.md               # Project documentation
