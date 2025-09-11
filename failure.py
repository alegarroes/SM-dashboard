import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from failurefunc import tresca, von_mises, rankine, mohr, plot_mohrs_circle

plt.rcParams["font.family"] = "monospace"

st.title("Criterios de falla")
st.set_page_config(page_title="Criterios de falla", layout=None)

materiales = ["Dúctil", "Frágil - Rankine", "Frágil - Mohr"]

with st.container(border=True):
    st.write("Ingrese los valores de esfuerzos principales")
    col1, col2, col3 = st.columns(3)
    with col1:
        sigma1 = st.number_input("$\sigma_{1}$", value=50.0, step=1.0)
    with col2:
        sigma2 = st.number_input("$\sigma_{2}$", value=100.0, step=1.0)
    with col3:
        seleccion_material = st.radio("Tipo de material", options=materiales)

    if seleccion_material == "Dúctil":
        with col1:
            sigma_yield = st.number_input("$\sigma_{YP}$", value=100.0, step=1.0)
    elif seleccion_material == "Frágil - Mohr":
        with col1:
            sigma_ut = st.number_input("$\sigma_{UT}$", value=100.0, step=1.0)
        with col2:
            sigma_uc = st.number_input("$\sigma_{UC}$", value=200.0, step=1.0)
    else:
        with col1:
            sigma_u = st.number_input("$\sigma_{U}$", value=100.0, step=1.0)

if seleccion_material == "Dúctil":
    failure_tresca_bool, fs_tresca = tresca(sigma1, sigma2, sigma_yield)

    failure_vm_bool, fs_vm = von_mises(sigma1, sigma2, sigma_yield)

    with st.container(border=True):
        st.write("Fluencia y factores de seguridad")
        col1, col2 = st.columns(2, border=True)
        if seleccion_material == "Dúctil":
            with col1:
                cols = st.columns(2)
                with cols[0]:
                    st.subheader("Tresca")
                with cols[1]:
                    if failure_tresca_bool:
                        st.error("Fluencia!")
                    else:
                        st.success("No hay fluencia")
                st.metric("$FS_{Tresca}$", f"{fs_tresca:.2f}")
            with col2:
                cols = st.columns(2)
                with cols[0]:
                    st.subheader("von Mises")
                with cols[1]:
                    if failure_vm_bool:
                        st.error("Fluencia!")
                    else:
                        st.success("No hay fluencia")
                st.metric("$FS_{vonMises}$", f"{fs_vm:.2f}")
        else:
            st.write("En construcción...")

    fig, ax = plt.subplots()

    surface_tresca = np.array(
        [
            [sigma_yield, 0],
            [sigma_yield, sigma_yield],
            [0, sigma_yield],
            [-sigma_yield, 0],
            [-sigma_yield, -sigma_yield],
            [0, -sigma_yield],
            [sigma_yield, 0],
        ]
    )

    # estas son las ecuaciones parametricas de una elipse rotada 45 grados
    t = np.linspace(-2 * np.pi, 2 * np.pi, 100)
    x = sigma_yield * np.cos(t) - sigma_yield / np.sqrt(3) * np.sin(t)
    y = sigma_yield * np.cos(t) + sigma_yield / np.sqrt(3) * np.sin(t)

    ax.plot(surface_tresca[:, 0], surface_tresca[:, 1], label="Tresca")
    ax.plot(x, y, label="Von Mises")
    ax.plot([sigma1], [sigma2], "bo", markersize=4)

    ax.set_aspect("equal")
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines[["right", "top"]].set_visible(False)
    ax.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncols=2, frameon=False)
    ax.set_xlabel("$\sigma_1$", loc="right")
    ax.set_ylabel("$\sigma_2$", loc="top", rotation=0)
    # Hide tick labels at 0
    for label in ax.get_xticklabels():
        if label.get_text() == "0":
            label.set_visible(False)

    for label in ax.get_yticklabels():
        if label.get_text() == "0":
            label.set_visible(False)
    st.pyplot(fig)

elif seleccion_material == "Frágil - Rankine":
    failure_rankine_bool, fs_rankine = rankine(sigma1, sigma2, sigma_u)

    with st.container(border=True):
        st.write("Falla y factor de seguridad")
        cols = st.columns(2)
        with cols[0]:
            if failure_rankine_bool:
                st.error("Falla!")
            else:
                st.success("No hay falla")
        with cols[1]:
            st.metric("$FS_{Rankine}$", f"{fs_rankine:.2f}")

    surface_rankine = np.array(
        [
            [sigma_u, sigma_u],
            [-sigma_u, sigma_u],
            [-sigma_u, -sigma_u],
            [sigma_u, -sigma_u],
            [sigma_u, sigma_u],
        ]
    )

    fig, ax = plt.subplots()
    ax.plot(surface_rankine[:, 0], surface_rankine[:, 1], label="Rankine")
    ax.plot([sigma1], [sigma2], "bo", markersize=4)
    ax.set_aspect("equal")
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")
    ax.spines[["right", "top"]].set_visible(False)
    ax.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncols=2, frameon=False)
    ax.set_xlabel("$\sigma_1$", loc="right")
    ax.set_ylabel("$\sigma_2$", loc="top", rotation=0)
    # Hide tick labels at 0
    for label in ax.get_xticklabels():
        if label.get_text() == "0":
            label.set_visible(False)

    for label in ax.get_yticklabels():
        if label.get_text() == "0":
            label.set_visible(False)
    st.pyplot(fig)

elif seleccion_material == "Frágil - Mohr":
    fig, ax = plt.subplots()
    x_axis_label = "$\sigma$"
    y_axis_label = "$\\tau$"

    # calculo de radios y linea de envolvente.
    r_c = sigma_uc / 2.0
    r_t = sigma_ut / 2.0
    cos_alpha = (r_c - r_t) / (r_c + r_t)
    sin_alpha = 2.0 * np.sqrt(r_c * r_t) / (r_c + r_t)
    x_line = [-r_c * (1.0 - cos_alpha), r_t * (1 + cos_alpha)]
    y_line = [r_c * sin_alpha, r_t * sin_alpha]

    failure_mohr_bool, fs_mohr = mohr(sigma1, sigma2, sigma_uc, sigma_ut)

    with st.container(border=True):
        st.write("Falla y factor de seguridad")
        cols = st.columns(2)
        with cols[0]:
            if failure_mohr_bool:
                st.error("Falla!")
            else:
                st.success("No hay falla")
        with cols[1]:
            st.metric("$FS_{Mohr}$", f"{fs_mohr:.2f}")

    plot_mohrs_circle(-sigma_uc, 0, "Ensayo a compresión", ax)
    plot_mohrs_circle(sigma_ut, 0, "Ensayo a tension", ax)
    plot_mohrs_circle(sigma1, sigma2, "Estado de esfuerzos", ax)

    # Set axis labels manually at top and right
    ax.annotate(
        x_axis_label,
        xy=(ax.get_xlim()[1], 0),
        xytext=(5, -15),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=12,
    )

    ax.annotate(
        y_axis_label,
        xy=(0, ax.get_ylim()[1]),
        xytext=(5, 0),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=12,
    )

    ax.plot(
        x_line,
        y_line,
        label="Envolvente de falla",
        color="black",
        linewidth=1.0,
        linestyle="--",
    )

    ax.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncols=2, frameon=False)

    st.pyplot(fig)

else:
    pass
