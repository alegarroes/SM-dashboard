import numpy as np


def tresca(sigma1, sigma2, sigma_yield):
    if np.sign(sigma1) == np.sign(sigma2):
        stress = max(abs(sigma1), abs(sigma2))
    else:
        stress = abs(sigma1) + abs(sigma2)

    if stress < sigma_yield:
        failure_bool = False
    else:
        failure_bool = True

    fs = sigma_yield / stress

    return failure_bool, fs


def von_mises(sigma1, sigma2, sigma_yield):
    stress = np.sqrt(sigma1**2 - sigma1 * sigma2 + sigma2**2)

    if stress < sigma_yield:
        failure_bool = False
    else:
        failure_bool = True

    fs = sigma_yield / stress

    return failure_bool, fs


def rankine(sigma1, sigma2, sigma_u):
    stress = max(abs(sigma1), abs(sigma2))
    if stress < sigma_u:
        failure_bool = False
    else:
        failure_bool = True

    fs = sigma_u / stress

    return failure_bool, fs


def mohr(sigma1, sigma2, sigma_uc, sigma_ut):
    r_c = sigma_uc / 2.0
    r_t = sigma_ut / 2.0
    center = (sigma1 + sigma2) / 2.0
    r = abs(sigma1 - sigma2) / 2.0
    r_max = r_c - (r_c + center) * (r_c - r_t) / (r_c + r_t)

    if r < r_max:
        failure_bool = False
    else:
        failure_bool = True

    fs = r / r_max

    return failure_bool, fs


def plot_mohrs_circle(sigma1, sigma2, plot_label, ax):

    center = (sigma1 + sigma2) / 2
    radius = (sigma1 - sigma2) / 2

    # Mohr Circle
    theta = np.linspace(0, 2 * np.pi, 100)
    circle_x = center + radius * np.cos(theta)
    circle_y = radius * np.sin(theta)

    # circulo
    ax.plot(circle_x, circle_y, label=plot_label)

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

    # Hide tick labels at 0
    for label in ax.get_xticklabels():
        if label.get_text() == "0":
            label.set_visible(False)

    for label in ax.get_yticklabels():
        if label.get_text() == "0":
            label.set_visible(False)

    ax.set_aspect("equal")
