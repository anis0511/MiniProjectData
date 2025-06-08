import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="International Education Cost Insight",
    layout="wide",
    initial_sidebar_state="expanded"
)


#uploading main image for dashboard
st.image('edu2.jpg')

#title for dashboard
st.title("""Welcome to our Dashboard😄""")


#upload data
df = pd.read_csv("Cleaned_Education_Costs.csv")

# Calculate total cost
if 'Total_Cost_USD' not in df.columns:
    df["Total_Cost_USD"] = (
        df["Tuition_USD"] +
        df["Rent_USD"] * 12 * df["Duration_Years"] +
        df["Visa_Fee_USD"] +
        df["Insurance_USD"]
    )

# Sidebar layout
with st.sidebar:
    st.image("edu2.jpg", use_container_width=True)
    st.title("🎓 EduNav")
    page = st.radio("Navigate", ["Dashboard", "Map", "University Table"])
    st.markdown("---")
    selected_level = st.selectbox("Filter by Level", ["All"] + sorted(df["Level"].unique()))
    if selected_level != "All":
        filtered_df = df[df["Level"] == selected_level]
    else:
        filtered_df = df

# Colored Pages
st.markdown("""
<style>
/* Main background */
.stApp {
    background-color: #fdfcfb;
    font-family: 'Segoe UI', sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #e6f0ff;
}

/* Metric styling */
[data-testid="metric-container"] {
    background-color: #ffffff;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 10px;
    margin: 5px;
    color: #003366;
}

/* Markdown box cards */
div[style*="background-color:#f0f2f6"] {
    border: 1px solid #cdd4da;
}

/* Tabs or column content spacing */
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
</style>
""", unsafe_allow_html=True)



# Features that we want it to APPEAR IN ALL PAGES
# cards of 'Top 10 Cheapest Tution Fees Universities'
def render_top10_uni(filtered_df):
    st.subheader("🏅 Top 10 Cheapest Tuition Fees Universities")
    top10_unis = (
        filtered_df.groupby("University")["Tuition_USD"]
        .mean()
        .sort_values()
        .head(10)
        .reset_index()
    )
    for idx, row in top10_unis.iterrows():
        st.markdown(f"""
        <div style="background-color:#f0f2f6; padding:10px; margin-bottom:10px; border-radius:10px">
            <b>{idx+1}. {row['University']}</b><br>
            <span style="color:#555">Avg Tuition: <b>${row['Tuition_USD']:,.2f}</b></span>
        </div>
        """, unsafe_allow_html=True)
#_______________________________________________________________________
 
#Creating Pages        
# UNIVERSITY TABLE
if page == "University Table":
    col1, col2 = st.columns([3,1])

    with col1:
        st.title("🏫 University Listing")

        if filtered_df.empty:
            st.warning("No data available for the selected education level.")
        else:
            selected_columns = st.multiselect(
                "Select columns to view",
                df.columns.tolist(),
                default=["Country", "University", "Program", "Total_Cost_USD"]
            )

            if selected_columns:
                st.dataframe(filtered_df[selected_columns])
            else:
                st.info("Please select at least one column to display.")
    with col2:
        render_top10_uni(filtered_df)
#__________________________________________________________________________

# DASHBOARD
elif page == "Dashboard":
    st.title("📊 International Education Cost Insight")

    # Metric Cards at the top
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Tuition", f"${filtered_df['Tuition_USD'].mean():,.0f}")
    with col2:
        st.metric("Avg Rent (Monthly)", f"${filtered_df['Rent_USD'].mean():,.0f}")
    with col3:
        st.metric("Avg Total Cost", f"${filtered_df['Total_Cost_USD'].mean():,.0f}")
    st.markdown("---")

    # Charts
    tab1, tab2 = st.tabs(["Cost Breakdown", "Distribution"])

    with tab1:
        cost_cols = ["Tuition_USD", "Rent_USD", "Visa_Fee_USD", "Insurance_USD"]
        cost_avg = filtered_df[cost_cols].mean().reset_index()
        cost_avg.columns = ["Cost Type", "Average (USD)"]

        # Calculate KPI values
        total_universities = filtered_df["University"].nunique()
        max_tuition = filtered_df["Tuition_USD"].max()

        # Country with lowest average tuition
        cheapest_country = (
            filtered_df.groupby("Country")["Tuition_USD"].mean().sort_values().index[0]
        )

        # Country with highest average tuition
        most_expensive_country = (
            filtered_df.groupby("Country")["Tuition_USD"].mean().sort_values(ascending=False).index[0]
        )

        # Define a function to render each colored KPI card
        def colored_card(title, value, bg_color="#f0f2f6"):
            st.markdown(f"""
                <div class="kpi-card" style="
                    background-color: {bg_color};
                    padding: 15px 20px;
                    border-radius: 12px;
                    margin-bottom: 15px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                    transition: all 0.2s ease-in-out;
                ">
                    <h5 style="margin-bottom: 5px; color: #333;">{title}</h5>
                    <h3 style="margin: 0; color: #000;">{value}</h3>
                </div>
            """, unsafe_allow_html=True)

        # Container box for all KPI cards
        st.markdown("""
            <div style="
                background-color: #ffffff;
                border-radius: 15px;
                padding: 25px 30px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                margin-bottom: 30px;
                ">
        """, unsafe_allow_html=True)



        col_bar, _, col_pie, col_uni = st.columns([6, 0.5, 6, 5])

        with col_bar:
            colored_card("Total Universities", total_universities, "#E3F2FD")
            colored_card("Cheapest Country (Avg)", cheapest_country, "#F3E5F5")

            # Close container
            st.markdown("</div>", unsafe_allow_html=True)


            fig = px.bar(cost_avg, x="Cost Type", y="Average (USD)", color="Cost Type",
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 title="Average of Every Cost Type")

            fig.update_layout(xaxis_tickangle=-45)

            st.plotly_chart(fig, use_container_width=True)


        with col_pie:
            colored_card("Max Tuition", f"${max_tuition:,.0f}", "#FFF3E0")
            colored_card("Most Expensive Country (Avg)", most_expensive_country, "#E0F2F1")

            # Close container
            st.markdown("</div>", unsafe_allow_html=True)

            # Pie Chart
            level_counts = df["Level"].value_counts().reset_index()
            level_counts.columns = ["Level", "Count"]

            #custom color
            custom_colors = {
                "Bachelor": "#FF6692",
                "Master": "#FECB52",
                "PhD": "#B6E880"}

            fig_pie = px.pie(
                level_counts,
                values="Count",
                names="Level",
                color="Level", 
                title="Distribution of Education Levels",
                hole=0.3,
                color_discrete_map=custom_colors)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_uni:
            render_top10_uni(filtered_df)

 
        avg_by_duration = filtered_df.groupby("Duration_Years")[["Rent_USD", "Insurance_USD"]].mean().reset_index()

        avg_by_duration_melted = avg_by_duration.melt(
            id_vars="Duration_Years",
            value_vars=["Rent_USD", "Insurance_USD"],
            var_name="Cost Type",
            value_name="Average Cost"
        )

        fig = px.bar(
            avg_by_duration_melted,
            x="Duration_Years",
            y="Average Cost",
            color="Cost Type",
            barmode="group",
            title="Average Rent and Insurance Cost by Duration of Studies (Years)",
            labels={"Duration_Years": "Duration (Years)"}
        )
        st.plotly_chart(fig, use_container_width=True)

        

        top10_uni = (
            filtered_df.groupby("University")["Tuition_USD"]
            .mean()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )

        fig = px.bar(
            top10_uni,
            x="Tuition_USD",
            y="University",
            orientation="h",
            title="Top 10 Universities with Highest Average Tuition Fees",
            labels={"Tuition_USD": "Average Tuition (USD)", "University": "University"},
            color="Tuition_USD",
            color_continuous_scale="Haline"
        )

        fig.update_layout(yaxis=dict(autorange="reversed"))  # To show highest at top
        st.plotly_chart(fig, use_container_width=True)


        # Load data for Scatter Plot
        df = filtered_df.copy()  # assuming filtered_df already exists

        # Compute additional columns
        df["Total_Cost"] = df["Tuition_USD"] + df["Rent_USD"] + df["Insurance_USD"]
        df["Average_Annual_Tuition"] = df["Tuition_USD"] / df["Duration_Years"]

        # Dropdown to choose Y-axis metric
        y_axis_option = st.selectbox(
            "Select Y-Axis Metric:",
            (
                "Tuition_USD",
                "Total_Cost",
                "Average_Annual_Tuition"
            ),
            format_func=lambda x: {
                "Tuition_USD": "Tuition (USD)",
                "Total_Cost": "Total Cost (Tuition + Rent + Insurance)",
                "Average_Annual_Tuition": "Average Annual Tuition (USD)"
            }[x]
        )

        # Scatter plot
        fig = px.scatter(
            df,
            x="Duration_Years",
            y=y_axis_option,
            color="Level",  # Optional: You can change this to 'Country'
            size="Tuition_USD",  # Optional bubble size
            hover_data=["University", "Country", "Duration_Years"],
            title=f"{y_axis_option.replace('_', ' ')} vs Duration of Studies",
            opacity=0.7
        )

        fig.update_layout(
            xaxis_title="Duration of Studies (Years)",
            yaxis_title=y_axis_option.replace("_", " "),
            title_x=0,
            height=700,  # ⬅️ Increase vertical height here (default is ~450)
        )

        st.plotly_chart(fig, use_container_width=True)
#__________________________

        # Assume df is already loaded and cleaned properly
        df["Total_Cost"] = df["Tuition_USD"] + df["Rent_USD"] + df["Insurance_USD"]
        df["Avg_Annual_Tuition"] = df["Tuition_USD"] / df["Duration_Years"]

        # Selectbox for Y-axis
        y_axis_option = st.selectbox(
            "Select Y-Axis Metric:",
            ["Tuition_USD", "Total_Cost", "Avg_Annual_Tuition"],
            format_func=lambda x: {
                "Tuition_USD": "Tuition (USD)",
                "Total_Cost": "Total Cost (USD)",
                "Avg_Annual_Tuition": "Average Annual Tuition (USD)"
            }[x]
        )

        # Line plot: average values grouped by Level and Duration
        grouped = df.groupby(["Level", "Duration_Years"])[y_axis_option].mean().reset_index()

        fig = px.line(
            grouped,
            x="Duration_Years",
            y=y_axis_option,
            color="Level",
            markers=True,
            title=f"{y_axis_option.replace('_', ' ')} vs Duration of Studies",
            labels={
                "Duration_Years": "Duration of Studies (Years)",
                y_axis_option: y_axis_option.replace("_", " "),
                "Level": "Education Level"
            },
            color_discrete_map={
                "Bachelor": "dodgerblue",
                "Master": "skyblue",
                "PhD": "tomato"
            }
        )

        fig.update_layout(
            title_x=0,  # Align title to the left
            plot_bgcolor="#fff",
            paper_bgcolor="#fff"
        )

        st.plotly_chart(fig, use_container_width=True)



        
#_______________________________________________________________
    with tab2:
        column = st.selectbox("Select Numeric Column", cost_cols + ["Duration_Years"])
        fig = px.histogram(filtered_df, x=column, nbins=20,
                           color_discrete_sequence=['#08FDD8'])
        fig.update_traces(marker_line_color='black', marker_line_width=1)

        st.plotly_chart(fig, use_container_width=True)
#_________________________________________________________________________
    
# Map Page
elif page == "Map":
    col1, col2 = st.columns([3,1])
    with col1:
        st.title("🌍 University Locations")
        uni_country = filtered_df.groupby("Country")["University"].nunique().reset_index()
        uni_country.columns = ["Country", "University Count"]

        fig = px.choropleth(uni_country, locations='Country', locationmode='country names',
                            color='University Count', color_continuous_scale='YlOrRd',
                            title='Number of Universities by Country')
        st.plotly_chart(fig, use_container_width=True)


        # BAR GRAPH FOR 'average total education cost by country'
	# Make group by country & calculate the average total education cost
        avg_cost_by_country = filtered_df.groupby("Country")["Tuition_USD"].mean().reset_index()

        # Sort values for clearer visualization
        avg_cost_by_country = avg_cost_by_country.sort_values(by="Tuition_USD", ascending=False)

        fig_country = px.bar(
            avg_cost_by_country,
            x="Country",
            y="Tuition_USD",
            title="Average Tuition Cost by Country",
            labels={"Tuition_USD": "Average Cost (USD)"},
            color="Tuition_USD",
            color_continuous_scale="Sunsetdark")  #color asal plasma
        fig_country.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(fig_country, use_container_width=True)


    with col2:
        # Cards
        render_top10_uni(filtered_df)

#_________________________________________________________________

# Footer
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)



# LIVE TIME
st.sidebar.markdown(f"**Live Time:** {datetime.now().strftime('%H:%M:%S')}")

# APA 
#background
#objective at least 3
#choose and clean data, then save
#proceed buat dashboard
#buat discussion utk data kat dashboard dlm notebook
#conclusion5
