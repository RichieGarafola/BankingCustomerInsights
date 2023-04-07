# Import libraries
# to simulate a real time data, time loop
import time  
# np mean, np random
import numpy as np  
# read csv, df manipulation
import pandas as pd  
# interactive charts
import plotly.express as px  
# data web app development
import streamlit as st  

df = pd.read_csv("./Resources/Bank.csv")

st.set_page_config(
    page_title="Banking Customer Insights Dashboard",
    page_icon="✅",
    layout="wide",
)

# dashboard title

st.title("Banking Customer Insights")

# top-level filters 

job_filter = st.selectbox("Select the Job", pd.unique(df['job']))


# creating a single-element container.
placeholder = st.empty()

# dataframe filter 

df = df[df['job']==job_filter]

# near real-time / live feed simulation 

for seconds in range(200):
    
    # simulate changes in the data
    df['age_new'] = df['age'] * np.random.choice([0.8, 0.9, 1, 1.1, 1.2], size=len(df))
    df['balance_new'] = df['balance'] * np.random.choice([0.8, 0.9, 1, 1.1, 1.2], size=len(df))

    # create descriptive KPI labels
    avg_age_label = f"Average Age of {job_filter.capitalize()} Employees"
    married_count_label = f"Married Count of {job_filter.capitalize()} Employees"
    avg_balance_label = f"Average Account Balance of {job_filter.capitalize()} Employees"

    # creating KPIs 
    avg_age = np.mean(df['age_new']) 

    count_married = int(df[(df["marital"]=='married')]['marital'].count() + np.random.choice(range(1,30)))
    
    balance = np.mean(df['balance_new'])

    with placeholder.container():
        # create three columns
        kpi1, kpi2, kpi3 = st.columns(3)

        # fill in those three columns with respective metrics or KPIs 
        kpi1.metric(label=avg_age_label, value=round(avg_age), delta= round(avg_age) - 10)
        kpi2.metric(label=married_count_label, value= int(count_married), delta= - 10 + count_married)
        kpi3.metric(label=avg_balance_label, value= f"$ {round(balance,2)} ", delta= - round(balance/count_married) * 100)

        # create two columns for charts 

        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            st.markdown("### Distribution of Ages")
            fig = px.histogram(data_frame=df, x='age_new', nbins=20)
            fig.update_layout(title="Age Distribution of Selected Job Category", xaxis_title="Age", yaxis_title="Count")
            st.plotly_chart(fig)
        with fig_col2:
            st.markdown("### Account Balances")
            fig2 = px.histogram(data_frame=df, x='balance_new', nbins=20)
            fig2.update_layout(title="Account Balance Distribution of Selected Job Category", xaxis_title="Account Balance", yaxis_title="Count")
            st.plotly_chart(fig2)

        # show detailed data view
        st.markdown("### Detailed Data View")
        st.dataframe(df)
        
        # allow the user to control the update frequency
        time.sleep(3)
