# Import libraries
import pandas as pd
import numpy as np
import joblib
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
import io

# Load model and columns
model = joblib.load("pollution_model.pkl")
model_cols = joblib.load("model_columns.pkl")

# Load station geolocation data
station_data = pd.read_csv("stations.csv")  

# Mock real-time data 
real_time_data = {
    'O2': np.random.uniform(2, 10),
    'NO3': np.random.uniform(0, 3),
    'NO2': np.random.uniform(0, 2),
    'SO4': np.random.uniform(5, 25),
    'PO4': np.random.uniform(0, 1.5),
    'CL': np.random.uniform(10, 50)
}

# Page config
st.set_page_config(page_title="Water Pollutants Predictor", layout="wide")
st.markdown("<h1 style='text-align: center; color: #3399ff;'>💧 Water Pollutants Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Predict water pollutant levels based on Year and Station ID</p>", unsafe_allow_html=True)

# Sidebar
st.sidebar.header("📌 Instructions")
st.sidebar.markdown("""
1. Enter a **year** between 2000 and 2100.  
2. Input a valid **station ID**.  
3. Click **Predict** to see results.  
4. Download or compare with real-time data.
#  👨‍💻 Developed by **Roni Seikh**
""")

# Inputs
st.subheader("🔢 Input Parameters")
col1, col2 = st.columns(2)
year_input = col1.number_input("Enter Year", min_value=2000, max_value=2100, value=2022, step=1)
station_id = col2.text_input("Enter Station ID", value='1')

# Station map 
st.subheader("🗺️ Station Map")
if station_id in station_data['id'].astype(str).values:
    station_map = station_data.copy()
    station_map = station_map[station_map['id'].astype(str) == station_id]
    st.map(station_map[['lat', 'lon']])
else:
    st.warning("📍 Station ID not found in map data.")

# Prediction
if st.button("🚀 Predict"):
    if not station_id.strip():
        st.warning("⚠️ Please enter a valid Station ID.")
    else:
        try:
            input_df = pd.DataFrame({'year': [year_input], 'id': [station_id]})
            input_encoded = pd.get_dummies(input_df, columns=['id'])

            for col in model_cols:
                if col not in input_encoded.columns:
                    input_encoded[col] = 0
            input_encoded = input_encoded[model_cols]

            predicted_pollutants = model.predict(input_encoded)[0]
            pollutants = ['O2', 'NO3', 'NO2', 'SO4', 'PO4', 'CL']
            results = {pollutants[i]: round(predicted_pollutants[i], 2) for i in range(len(pollutants))}
            results_df = pd.DataFrame([results])

            st.success(f"✅ Predicted pollutant levels for Station '{station_id}' in {year_input}:")
            st.table(results_df)

            # Plotly interactive bar chart
            st.subheader("📊 Interactive Pollutant Levels")
            fig = px.bar(
                x=list(results.keys()),
                y=list(results.values()),
                labels={'x': 'Pollutant', 'y': 'Level'},
                title="Predicted Pollutant Levels",
                text=[f"{v:.2f}" for v in results.values()],
                color=list(results.keys())
            )
            fig.update_traces(marker_line_color='black', marker_line_width=1.2, textposition='outside')
            st.plotly_chart(fig)

            # Comparison with Real-time data
            st.subheader("🔄 Comparison with Real-time Data (Mocked)")
            comparison_df = pd.DataFrame({
                'Pollutant': pollutants,
                'Predicted': [results[p] for p in pollutants],
                'Real-Time': [round(real_time_data[p], 2) for p in pollutants]
            })
            st.dataframe(comparison_df)

            comparison_fig = px.bar(
                comparison_df.melt(id_vars='Pollutant', value_vars=['Predicted', 'Real-Time']),
                x='Pollutant',
                y='value',
                color='variable',
                barmode='group',
                title="Predicted vs Real-time Pollutants"
            )
            st.plotly_chart(comparison_fig)

            # Download
            st.subheader("⬇️ Download Results")
            csv = results_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download as CSV",
                data=csv,
                file_name=f'pollutants_{station_id}_{year_input}.csv',
                mime='text/csv'
            )

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

st.markdown(
    """
    <hr style="margin-top: 3rem; margin-bottom: 1rem;">
    <p style="text-align: center; font-size: 0.9em;">
        © 2025 Water Quality Prediction | Roni Seikh | All rights reserved.
    </p>
    """,
    unsafe_allow_html=True
)
