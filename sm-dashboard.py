import streamlit as st


cover_page = st.Page("cover.py", title="Bienvenidos")
stress_transf_page = st.Page("stress-transf.py", title="1. Transformación de esfuerzos")
strain_transf_page = st.Page(
    "strain-transf.py", title="2. Transformación de deformaciones"
)
failure_page = st.Page("failure.py", title="3. Criterios de falla")

pg = st.navigation(
    {
        "Inicio": [cover_page],
        "Aplicaciones": [stress_transf_page, strain_transf_page, failure_page],
    }
)
pg.run()

st.set_page_config(page_title="SolidLab")
