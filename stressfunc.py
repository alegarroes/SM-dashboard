import numpy as np
import matplotlib.pyplot as plt

# En este módulo se definen funciones para transformación de esfuerzos y deformaciones
# además de funciones para graficar el círculo de Mohr y el elemento rotando en matplotlib


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


def plot_mohrs_circle(sigma_x, sigma_y, tau_xy, theta, x_axis_label, y_axis_label, ax):

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

    # Hide tick labels at 0
    for label in ax.get_xticklabels():
        if label.get_text() == "0":
            label.set_visible(False)

    for label in ax.get_yticklabels():
        if label.get_text() == "0":
            label.set_visible(False)

    ax.set_aspect("equal")
    # ax.set_title("Mohr’s Circle")


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
