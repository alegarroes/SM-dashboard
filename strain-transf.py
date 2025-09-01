import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "monospace"


# Function to compute transformed stresses
def transform_stress(sigma_x, sigma_y, tau_xy, theta):
    theta_rad = np.radians(theta)
    sigma_x_prime = (
        (sigma_x + sigma_y) / 2
        + (sigma_x - sigma_y) / 2 * np.cos(2 * theta_rad)
        + tau_xy * np.sin(2 * theta_rad)
    )
    sigma_y_prime = (
        (sigma_x + sigma_y) / 2
        - (sigma_x - sigma_y) / 2 * np.cos(2 * theta_rad)
        - tau_xy * np.sin(2 * theta_rad)
    )
    tau_x_y_prime = -(sigma_x - sigma_y) / 2 * np.sin(2 * theta_rad) + tau_xy * np.cos(
        2 * theta_rad
    )
    return sigma_x_prime, sigma_y_prime, tau_x_y_prime


# Function to compute principal stresses
def principal_stress(sigma_x, sigma_y, tau_xy):
    tau_max = np.sqrt((np.square((sigma_x - sigma_y) / 2) + np.square(tau_xy)))
    sigma_tau = (sigma_x + sigma_y) / 2
    sigma_1 = sigma_tau + tau_max
    sigma_2 = sigma_tau - tau_max

    # considera el caso en que se indefine atan
    if tau_xy != 0:
        theta_tau = np.atan(-(sigma_x - sigma_y) / (2 * tau_xy)) / 2
    else:
        theta_tau = np.pi / 4.0

    if (sigma_x - sigma_y) != 0:
        theta_1 = np.atan(2 * tau_xy / (sigma_x - sigma_y)) / 2
    else:
        theta_1 = np.pi / 4.0

    sigma_x_prime, sigma_y_prime, tau_x_y_prime = transform_stress(
        sigma_x, sigma_y, tau_xy, np.degrees(theta_1)
    )

    if round(sigma_x_prime) != round(sigma_1):
        theta_2 = theta_1
        theta_1 += np.pi / 2
    else:
        theta_2 = theta_1 + np.pi / 2

    sigma_x_prime, sigma_y_prime, tau_x_y_prime = transform_stress(
        sigma_x, sigma_y, tau_xy, np.degrees(theta_tau)
    )

    tau_max = tau_x_y_prime

    return (
        sigma_1,
        sigma_2,
        np.degrees(theta_1),
        np.degrees(theta_2),
        tau_max,
        sigma_tau,
        np.degrees(theta_tau),
    )


def plot_mohrs_circle(sigma_x, sigma_y, tau_xy, theta, ax):

    center = (sigma_x + sigma_y) / 2
    radius = np.sqrt(((sigma_x - sigma_y) / 2) ** 2 + tau_xy**2)

    # Mohr Circle
    theta = np.linspace(0, 2 * np.pi, 100)
    circle_x = center + radius * np.cos(theta)
    circle_y = radius * np.sin(theta)

    ax.clear()
    # circulo
    ax.plot(circle_x, circle_y, label="Circulo de Mohr")
    # punto A
    ax.scatter([sigma_x], [tau_xy], color="red", label="Estado original", s=12)
    # centro
    ax.scatter([center], [0], color="black", label="Centro", s=12)
    # radio
    ax.plot(
        [center, sigma_x],
        [0, tau_xy],
        marker=None,
        color="black",
        linewidth=0.5,
        linestyle="--",
    )
    ax.axhline(0, color="black", linewidth=0.5)
    ax.axvline(0, color="black", linewidth=0.5)

    # Move spines to center (0,0)
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")

    # Hide top and right spines (borders)
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")

    # Set ticks only on bottom and left
    ax.xaxis.set_ticks_position("bottom")
    ax.yaxis.set_ticks_position("left")

    # Set axis labels manually at top and right
    ax.annotate(
        "$\epsilon$",
        xy=(ax.get_xlim()[1], 0),
        xytext=(5, -15),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=12,
    )

    ax.annotate(
        "$\gamma/2$",
        xy=(0, ax.get_ylim()[1]),
        xytext=(5, 0),
        textcoords="offset points",
        ha="left",
        va="bottom",
        fontsize=12,
    )

    # Hide tick labels at 0
    for label in ax.get_xticklabels():
        if label.get_text() == "0":
            label.set_visible(False)

    for label in ax.get_yticklabels():
        if label.get_text() == "0":
            label.set_visible(False)

    ax.set_aspect("equal")
    # ax.set_title("Mohr’s Circle")


def sync_from_text():
    st.session_state.slider_theta = st.session_state.text_theta


def sync_from_slider():
    st.session_state.text_theta = st.session_state.slider_theta


# funcion para dibujar flechas sobre el elemento
def draw_stress(
    padding, arrow_len_max, theta, x_ini, y_ini, max_stress, stress, face, type, ax
):
    if round(stress, 1) != 0:
        # dibujar flechas
        sf_arrow = arrow_len_max / max_stress
        arrow_len = abs(stress) * sf_arrow

        if type == "normal":
            if stress > 0:
                normal1_ini = np.array([x_ini + padding, y_ini])
                normal1_fin = np.array([x_ini + padding + arrow_len, y_ini])
            else:
                normal1_ini = np.array([x_ini + padding + arrow_len, y_ini])
                normal1_fin = np.array([x_ini + padding, y_ini])
        elif type == "shear":
            if face == "right" or face == "left":
                if stress > 0:
                    normal1_ini = np.array([x_ini + padding, y_ini - arrow_len / 2.0])
                    normal1_fin = np.array([x_ini + padding, y_ini + arrow_len / 2.0])
                else:
                    normal1_ini = np.array([x_ini + padding, y_ini + arrow_len / 2.0])
                    normal1_fin = np.array([x_ini + padding, y_ini - arrow_len / 2.0])
            else:
                if stress < 0:
                    normal1_ini = np.array([x_ini + padding, y_ini - arrow_len / 2.0])
                    normal1_fin = np.array([x_ini + padding, y_ini + arrow_len / 2.0])
                else:
                    normal1_ini = np.array([x_ini + padding, y_ini + arrow_len / 2.0])
                    normal1_fin = np.array([x_ini + padding, y_ini - arrow_len / 2.0])

        if face == "right":
            theta_rad = np.radians(-theta)
        elif face == "top":
            theta_rad = np.radians(-theta - 90.0)
        elif face == "left":
            theta_rad = np.radians(-theta - 180.0)
        elif face == "bottom":
            theta_rad = np.radians(-theta - 270.0)

        rotmat = np.array(
            [
                [np.cos(theta_rad), -np.sin(theta_rad)],
                [np.sin(theta_rad), np.cos(theta_rad)],
            ]
        )

        normal1_ini_rot = np.dot(normal1_ini, rotmat)
        normal1_fin_rot = np.dot(normal1_fin, rotmat)

        dx = normal1_fin_rot[0] - normal1_ini_rot[0]
        dy = normal1_fin_rot[1] - normal1_ini_rot[1]
        ax.arrow(
            normal1_ini_rot[0],
            normal1_ini_rot[1],
            dx,
            dy,
            width=0.01,
            head_width=0.08,
            shape="full",
            length_includes_head=True,
        )

        if abs(theta_rad) < np.pi / 2.0:
            alignment = "left"
        else:
            alignment = "right"

        stress_text = np.array(
            [normal1_fin[0] + padding / 2.0, normal1_fin[1] + padding / 2.0]
        )
        stress_text = np.dot(stress_text, rotmat)

        ax.text(
            stress_text[0],
            stress_text[1],
            f"{stress:.2f}",
            horizontalalignment=alignment,
            # rotation=theta,
        )

    else:
        pass


## ----- Aqui inicia el codigo del dashboard streamlit -----

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

    # # Initial Mohr's Circle plot
    plot_mohrs_circle(sigma_x, sigma_y, tau_xy / 2.0, theta, ax_mohr)

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
