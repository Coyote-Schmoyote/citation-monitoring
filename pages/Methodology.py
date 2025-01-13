import streamlit as st

# Sidebar navigation using native hamburger menu
st.sidebar.image("./data/b&s_logo.png")
st.sidebar.image("./data/pil_logo.png")

st.markdown("""           
## 1. Introduction

This section introduces the report by briefly commenting on the objectives (Section 1.1), the methodology (1.2) and the structure of this report (1.3).

### 1.1 Objectives
The monitoring team will provide two types of deliverables:
- **Quarterly monitoring reports**
The quarterly monitoring reports present all citations to EIGE and EIGE’s outputs from academia. The reports present the following information:
    - date of publication;
    - URL of the document citing EIGE;
    - name of the author/organisation citing EIGE;
    - name of the journal citing EIGE;
    - EIGE's output cited;
    - topic;
    - impact factor of the journal;
    - number of citations;
    - location of the citation;
    - category of mention;
    - number of mentions in social media;
    - weight
The quarterly reports are presented as an annex in form of an Excel spreadsheet in each corresponding report page.  
- **Analytical reports**
The analytical report includes the main findings and trends for the monitoring period January-March 2024. 
""")

st.markdown("""
## 1.2 Methodology

- For the monthly reports, we have monitored the keyword **“European Institute for Gender Equality”** using the tool Scite and double checking the results using the tool Google Scholar. 
- We only searched for results in **English**.
- To enable a more accurate list of results, we will search for the term using quotation marks (e.g., "European Institute of Gender Equality”, instead of European Institute of Gender Equality.) 
- We propose not to search for the term “EIGE” as the search leads to numerous false results (such as EIG, or the German term ‘eigen’).
- For the analytical report, we have produced graphics and trends based on the data collected for the current quarter.

The report is based on the methodology agreed with EIGE on 12 December 2024. However, during the collection of data for the first quarterly report, we have identified several caveats that need to be taken into consideration for the current monitoring and analysis:     
- Using the agreed search tools (Scite, Google Scholar) it is not possible to identify the documents by the exact **date** (only by year).
- Using the agreed search tools, it is not possible to access and read all the documents. Therefore, it is not always possible no identify the precise EIGE’s **output** that the document is referring to.
- For the same reason mentioned above, it is not possible to access all documents and therefore to identify the main **topics** where citations to EIGE are found.
- Being the first monitoring done for 2024, it is not possible to observe the **trend** in citations to EIGE.
            """)

st.markdown("""
## 1.3 Report structure
The report is organised in two main sections and three annexes, namely:
- This Methodology (section 2), including detail on the objectives, methodology and report structure.
- The Analysis ("Qx_YYYY_Report"), presenting the analysis of the quarterly reports.

- Annex 1 presents the Excel file that contains all the citations (January-March 2024), available for download on the page of each quarterly report.


""")