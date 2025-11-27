# Disease Information Dashboard

This repository contains a **Streamlit** web application that generates structured summaries about diseases using the **OpenAI API** and presents them in an interactive dashboard.

You can:

- Query **1–5 diseases** at a time.
- (Optionally) specify a **timeframe** for the requested statistics.
- Get AI-generated **JSON** with:
  - Key statistics (total cases, recovery rate, mortality rate)
  - Recovery options
  - Medication information
- Visualize **recovery vs mortality rates** in a bar chart.
- Export a **PDF report** with statistics, recovery options and medication sections for all requested diseases.

This project was built during the **Workearly AI Programming Summer School**.

>  **Important:** This app is for **educational/demo purposes only**.  
> The generated content is AI-generated and **must not** be used as real medical advice, diagnosis, or treatment guidance.

## Features

### AI-generated disease summaries

For each disease name you enter, the app calls the **OpenAI Chat Completions API** to request information in a specific JSON structure:

- `name` – disease name
- `statistics`
  - `total_cases` – numeric value (string in JSON, but representing a number)
  - `recovery_rate` – percentage string (e.g. `"85%"`)
  - `mortality_rate` – percentage string (e.g. `"2%"`)
- `recovery_options`
  - Keys `"1"`, `"2"`, `"3"`, `"4"` with detailed descriptions
- `medication`
  - Includes medication name, side effects (list of strings) and dosage information, following an example JSON template

The app supports an **optional timeframe**: if enabled, the system prompt asks the model to focus on statistics between a given start and end date.

Internally, the function:

```python
get_disease_info(disease_name, time_frame)
