import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from stressfunc import (
    transform_stress,
    principal_stress,
    plot_mohrs_circle,
    draw_stress,
)


def sync_from_text():
    st.session_state.slider_theta = st.session_state.text_theta


def sync_from_slider():
    st.session_state.text_theta = st.session_state.slider_theta


## ----- Aqui inicia el codigo del dashboard streamlit -----

plt.rcParams["font.family"] = "monospace"

st.title("Transformación de deformaciones")
st.set_page_config(page_title="Transformación de deformaciones", layout="wide")

tmp1, col_data, col_graphs, tmp2 = st.columns([1, 20, 16, 1], width=1000)

with col_data:
    with st.form("form_stresses"):
        st.write("Ingresar los valores del estado de deformaciones")
        col1, col2, col3 = st.columns(3)
        with col1:
            sigma_x = st.number_input(
                "$\epsilon_{x}\space(\mu)$", value=100.0, step=10.0, format="%0f"
            )
        with col2:
            sigma_y = st.number_input(
                "$\epsilon_{y}\space(\mu)$", step=10.0, format="%0f"
            )
        with col3:
            tau_xy = st.number_input(
                "$\gamma_{xy}\space(\mu)$", value=50.0, step=10.0, format="%0f"
            )
        st.form_submit_button("Calcular")

    # se divide tau_xy entre dos para considerar que es deformación, no esfuerzo
    sigma_1, sigma_2, theta_1, theta_2, tau_max, sigma_tau, theta_tau = (
        principal_stress(sigma_x, sigma_y, tau_xy / 2.0)
    )

    # container deformaciones principales
    with st.container(border=True):
        st.write("Deformaciones principales")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("$\epsilon_1\space(\mu)$", f"{sigma_1:.2f}")
            st.metric("$\epsilon_2\space(\mu)$", f"{sigma_2:.2f}")
        with col2:
            st.metric("$\\theta_1$", f"{theta_1:.2f}°")
            st.metric("$\\theta_2$", f"{theta_2:.2f}°")

    # container cortante máximo
    with st.container(border=True):
        st.write("Deformación cortante máxima")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("$\gamma_{max}\space(\mu)$", f"{tau_max:.2f}")
        with col2:
            st.metric("$\epsilon_\gamma\space(\mu)$", f"{sigma_tau:.2f}")
        with col3:
            st.metric("$\\theta_\gamma$", f"{theta_tau:.2f}°")

    col1, col2 = st.columns([0.7, 0.3])

    if "slider_theta" not in st.session_state:
        st.session_state["slider_theta"] = 0.0
    if "text_theta" not in st.session_state:
        st.session_state["text_theta"] = 0.0

    with col1:
        # slider para el angulo
        theta = st.slider(
            "Ángulo $\\theta$",
            min_value=-180.0,
            max_value=180.0,
            format="%.2f°",
            step=1.0,
            key="slider_theta",
            value=st.session_state["slider_theta"],
            # on_change=sync_from_slider,
        )

    # corregir para que acepte mas de un numero
    with col2:
        theta_text = st.number_input(
            label="Ángulo $\\theta$",
            label_visibility="hidden",
            key="text_theta",
            min_value=-180.0,
            max_value=180.0,
            step=1.0,
            value=st.session_state["slider_theta"],
            on_change=sync_from_text,
        )

    sigma_x_prime, sigma_y_prime, tau_x_y_prime = transform_stress(
        sigma_x, sigma_y, tau_xy / 2.0, theta
    )

    # container esfuerzos en un angulo
    with st.container(border=True):
        st.write(f"Deformaciones en el angulo {theta:.1f}°")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("$\epsilon_{x'}\space(\mu)$", f"{sigma_x_prime:.2f}")
        with col2:
            st.metric("$\epsilon_{y'}\space(\mu)$", f"{sigma_y_prime:.2f}")
        with col3:
            st.metric("$\gamma_{xy'}\space(\mu)$", f"{tau_x_y_prime:.2f}")

with col_graphs:
    fig, ax_mohr = plt.subplots()
    plt.subplots_adjust(bottom=0.25)
    x_axis_label = "$\epsilon$"
    y_axis_label = "$\gamma/2$"

    # # Initial Mohr's Circle plot
    plot_mohrs_circle(
        sigma_x, sigma_y, tau_xy / 2.0, theta, x_axis_label, y_axis_label, ax_mohr
    )

    # ojo que se cambia el signo del cortante para coincidir con el metodo I del Popov
    (punto,) = ax_mohr.plot(
        [sigma_x_prime], [-tau_x_y_prime], "bo", markersize=4, label="Transformado"
    )
    ax_mohr.plot(
        [sigma_x, sigma_x_prime],
        [tau_xy / 2.0, -tau_x_y_prime],
        linewidth=1.0,
        color="b",
    )
    ax_mohr.legend(loc=8, bbox_to_anchor=(0.5, -0.2), ncols=2, frameon=False)

    st.pyplot(fig)

    # dibujo de elemento en rotacion
    fig2, ax_square = plt.subplots()
    puntos = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]])
    theta_rad = np.radians(-theta)
    rotmat = np.array(
        [
            [np.cos(theta_rad), -np.sin(theta_rad)],
            [np.sin(theta_rad), np.cos(theta_rad)],
        ]
    )

    # calculo de puntos del elemento cuadrado según la rotación theta
    puntos_rot = np.dot(puntos, rotmat)

    # ejes que rotan
    padding = 0.2
    ejes_prima = np.array([[2, 0], [0, 0], [0, 2]])
    ejes_text_prima = np.array(
        [
            [ejes_prima[0][0], ejes_prima[0][1] - padding / 2.0],
            [ejes_prima[2][0] + padding / 4.0, ejes_prima[2][1]],
        ]
    )
    ejes_prima = np.dot(ejes_prima, rotmat)
    ejes_text_prima = np.dot(ejes_text_prima, rotmat)

    ax_square.plot(puntos_rot[:, 0], puntos_rot[:, 1])
    ax_square.plot(ejes_prima[:, 0], ejes_prima[:, 1], color="r", linewidth="1")

    ax_square.text(
        ejes_text_prima[0][0],
        ejes_text_prima[0][1],
        "x'",
        rotation=theta,
        color="r",
    )
    ax_square.text(
        ejes_text_prima[1][0],
        ejes_text_prima[1][1],
        "y'",
        rotation=theta,
        color="r",
    )

    # draw normal stresses
    arrow_len_max = 0.5
    x_ini = 1
    y_ini = 0
    max_normal = max(abs(sigma_1), abs(sigma_2))

    # sigma_x_prime, right
    draw_stress(
        padding,
        arrow_len_max,
        theta,
        x_ini,
        y_ini,
        max_normal,
        sigma_x_prime,
        "right",
        "normal",
        ax_square,
    )

    # sigma_y_prime, top
    draw_stress(
        padding,
        arrow_len_max,
        theta,
        x_ini,
        y_ini,
        max_normal,
        sigma_y_prime,
        "top",
        "normal",
        ax_square,
    )

    # sigma_x_prime, left
    draw_stress(
        padding,
        arrow_len_max,
        theta,
        x_ini,
        y_ini,
        max_normal,
        sigma_x_prime,
        "left",
        "normal",
        ax_square,
    )

    # sigma_y_prime, bottom
    draw_stress(
        padding,
        arrow_len_max,
        theta,
        x_ini,
        y_ini,
        max_normal,
        sigma_y_prime,
        "bottom",
        "normal",
        ax_square,
    )

    # draw shear stresses
    padding = 0.1
    arrow_len_max = 1.5
    x_ini = 1
    y_ini = 0

    # tay_xy_prime, right
    draw_stress(
        padding,
        arrow_len_max,
        theta,
        x_ini,
        y_ini,
        abs(tau_max),
        tau_x_y_prime,
        "right",
        "shear",
        ax_square,
    )

    # tay_xy_prime, top
    draw_stress(
        padding,
        arrow_len_max,
        theta,
        x_ini,
        y_ini,
        abs(tau_max),
        tau_x_y_prime,
        "top",
        "shear",
        ax_square,
    )

    # tay_xy_prime, left
    draw_stress(
        padding,
        arrow_len_max,
        theta,
        x_ini,
        y_ini,
        abs(tau_max),
        tau_x_y_prime,
        "left",
        "shear",
        ax_square,
    )

    # tay_xy_prime, bottom
    draw_stress(
        padding,
        arrow_len_max,
        theta,
        x_ini,
        y_ini,
        abs(tau_max),
        tau_x_y_prime,
        "bottom",
        "shear",
        ax_square,
    )

    ax_square.set_aspect("equal")
    ax_square.set(xlim=(-2, 2))
    ax_square.set(ylim=(-2, 2))
    ax_square.spines[["right", "top"]].set_visible(False)
    ax_square.spines["left"].set_position("zero")
    ax_square.spines["bottom"].set_position("zero")
    ax_square.xaxis.set_ticks([])
    ax_square.yaxis.set_ticks([])
    st.pyplot(fig2)
