import streamlit as st
from datetime import datetime
from openai import OpenAI
import json
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
client = OpenAI(api_key=st.secrets["OpenAI_key"])

def get_disease_info(disease_name, time_frame):
    medication_format = '''{
        "name": "",
        "statistics": {
            "total_cases": "",
            "recovery_rate": "",
            "mortality_rate": ""
        },
        "recovery_options": {
            "1": "", 
            "2": "", 
            "3": "", 
            "4": ""
        },
        "medication": {
            "name": "",
            "side_effects": [
                "",
                "",
                ""
            ],
            "dosage": ""
        }
    }'''

    system_message = f"Please provide information on the following aspects for {disease_name}: 1. Key Statistics, 2. Recovery Options, 3. Recommended Medications. Format the response in JSON with keys for 'name'(name of the disease), 'statistics'(contains total_cases, recovery_rate, mortality_rate), 'total_cases' (this always has to be a digital number), 'recovery_rate' (this always has to be a percentage!), 'mortality_rate' (this always has to be a percentage!) 'recovery_options', (explain each recovery option in detail), and 'medication', (give some side effect examples and dosages) always use this example json format for medication : {medication_format} ."
    if len(time_frame) > 1:
        system_message = f"Please provide information for the timeframe {time_frame[0]} until {time_frame[1]} on the following aspects for {disease_name}: 1. Key Statistics, 2. Recovery Options, 3. Recommended Medications. Format the response in JSON with keys for 'name'(name of the disease), 'statistics'(contains total_cases, recovery_rate, mortality_rate), 'total_cases' (this always has to be a digital number), 'recovery_rate' (this always has to be a percentage!), 'mortality_rate' (this always has to be a percentage!) 'recovery_options', (explain each recovery option in detail), and 'medication', (give some side effect examples and dosages) always use this example json format for medication : {medication_format} ."

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Using gpt4o mini for more accurate results without errors at JSON parsing
        messages=[
            {"role": "system", "content": system_message}
        ]
    )
    return response.choices[0].message.content

def display_disease_info(disease_info):
    disease_info2 = disease_info.strip("```json").strip("```").strip()
    print(disease_info2)
    
    try:
        info = json.loads(disease_info2)

        recovery_rate = float(info['statistics']["recovery_rate"].strip('%'))
        mortality_rate = float(info['statistics']["mortality_rate"].strip('%'))

        chart_data = pd.DataFrame(
            {
                "Recovery Rate": [recovery_rate],
                "Mortality Rate": [mortality_rate],
            },
            index=["Rate"]
        )

        st.write(f"## Statistics for {info['name']}")
        st.write(info['statistics'])
        st.bar_chart(chart_data)
        st.write("## Recovery Options")
        recovery_options = info['recovery_options']
        for option, description in recovery_options.items():
            st.subheader(option)
            st.write(description)
        st.write("## Medication")
        medication = info['medication']
        medication_count = 1
        for option, description in medication.items():
            st.subheader(f"{medication_count}. {option}")
            st.write(description)
            medication_count += 1
    except json.JSONDecodeError:
        print("Failed to decode the response into JSON. Please check the format of the OpenAI response.")

def generate_pdf(disease_info_list):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    story = []

    for disease_info in disease_info_list:
        disease_info2 = disease_info.strip("```json").strip("```").strip()
        try:
            info = json.loads(disease_info2)

            story.append(Paragraph(f"Statistics for {info['name']}", styles['Title']))
            story.append(Spacer(1, 12))

            stats = f"Total Cases: {info['statistics']['total_cases']}<br/>" \
                    f"Recovery Rate: {info['statistics']['recovery_rate']}<br/>" \
                    f"Mortality Rate: {info['statistics']['mortality_rate']}"
            story.append(Paragraph(stats, styles['Normal']))
            story.append(Spacer(1, 12))

            story.append(Paragraph("Recovery Options", styles['Heading2']))
            for option, description in info['recovery_options'].items():
                story.append(Paragraph(f"{option}: {description}", styles['Normal']))
            story.append(Spacer(1, 12))

            story.append(Paragraph("Medication", styles['Heading2']))
            medication = info['medication']
            for key, value in medication.items():
                story.append(Paragraph(f"{key}: {value}", styles['Normal']))
            story.append(Spacer(1, 12))
            story.append(Spacer(1, 24))

        except json.JSONDecodeError:
            story.append(Paragraph("Failed to decode the response into JSON.", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

st.title("Disease Information Dashboard")

st.sidebar.header('User Input Options')
enable_timeframe = st.sidebar.checkbox("Enable Timeframe Selection")

num_diseases = st.sidebar.number_input('Number of Diseases to Compare', min_value=1, max_value=5, value=1, step=1)

time_frame = []
if enable_timeframe:
    start_date = st.sidebar.date_input("Start Date", datetime(2024, 1, 1))
    end_date = st.sidebar.date_input("End Date", datetime.today().date())
    if start_date >= end_date:
        st.sidebar.error('Error: End date must fall after start date.')
    elif end_date > datetime.today().date():
        st.sidebar.error('Error: We can\'t predict the future yet. :)')
    time_frame.append(start_date)
    time_frame.append(end_date)

disease_names = []
for i in range(num_diseases):
    disease_name = st.text_input(f"Enter the name of disease {i+1}:")
    disease_names.append(disease_name)

if all(disease_names):
    disease_info_list = [get_disease_info(disease_name, time_frame) for disease_name in disease_names]
    
    if num_diseases > 1:
        tabs = st.tabs([f"Disease {i+1}" for i in range(num_diseases)])
        for i, tab in enumerate(tabs):
            with tab:
                display_disease_info(disease_info_list[i])
    else:
        display_disease_info(disease_info_list[0])
    
    # Adding download button for PDF
    pdf_buffer = generate_pdf(disease_info_list)
    st.sidebar.download_button(
        label="Download Disease Info as PDF",
        data=pdf_buffer,
        file_name="disease_info.pdf",
        mime="application/pdf"
    )
