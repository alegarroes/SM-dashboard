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
