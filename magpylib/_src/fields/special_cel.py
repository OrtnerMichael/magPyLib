# pylint: disable=too-many-positional-arguments

import math as m

import numpy as np


def cel0(kc, p, c, s):
    """
    complete elliptic integral algorithm vom Kirby2009
    """
    if kc == 0:
        raise RuntimeError("FAIL")
    errtol = 0.000001
    k = abs(kc)
    pp = p
    cc = c
    ss = s
    em = 1.0
    if p > 0:
        pp = np.sqrt(p)
        ss = s / pp
    else:
        f = kc * kc
        q = 1.0 - f
        g = 1.0 - pp
        f = f - pp
        q = q * (ss - c * pp)
        pp = np.sqrt(f / g)
        cc = (c - ss) / g
        ss = -q / (g * g * pp) + cc * pp
    f = cc
    cc = cc + ss / pp
    g = k / pp
    ss = 2 * (ss + f * g)
    pp = g + pp
    g = em
    em = k + em
    kk = k
    while abs(g - k) > g * errtol:
        k = 2 * np.sqrt(kk)
        kk = k * em
        f = cc
        cc = cc + ss / pp
        g = kk / pp
        ss = 2 * (ss + f * g)
        pp = g + pp
        g = em
        em = k + em
    return (np.pi / 2) * (ss + cc * em) / (em * (em + pp))


def celv(kc, p, c, s):
    """
    vectorized version of the cel integral above
    """

    # if kc == 0:
    #    return NaN
    errtol = 0.000001
    n = len(kc)

    k = np.abs(kc)
    em = np.ones(n, dtype=float)

    cc = c.copy()
    pp = p.copy()
    ss = s.copy()

    # apply a mask for evaluation of respective cases
    mask = p <= 0

    # if p>0:
    pp[~mask] = np.sqrt(p[~mask])
    ss[~mask] = s[~mask] / pp[~mask]

    # else:
    f = kc[mask] * kc[mask]
    q = 1.0 - f
    g = 1.0 - pp[mask]
    f = f - pp[mask]
    q = q * (ss[mask] - c[mask] * pp[mask])
    pp[mask] = np.sqrt(f / g)
    cc[mask] = (c[mask] - ss[mask]) / g
    ss[mask] = -q / (g * g * pp[mask]) + cc[mask] * pp[mask]

    f = cc.copy()
    cc = cc + ss / pp
    g = k / pp
    ss = 2 * (ss + f * g)
    pp = g + pp
    g = em.copy()
    em = k + em
    kk = k.copy()

    # define a mask that adjusts with every evaluation step so that only
    # non-converged entries are further iterated.
    mask = np.ones(n, dtype=bool)
    while np.any(mask):
        k[mask] = 2 * np.sqrt(kk[mask])
        kk[mask] = k[mask] * em[mask]
        f[mask] = cc[mask]
        cc[mask] = cc[mask] + ss[mask] / pp[mask]
        g[mask] = kk[mask] / pp[mask]
        ss[mask] = 2 * (ss[mask] + f[mask] * g[mask])
        pp[mask] = g[mask] + pp[mask]
        g[mask] = em[mask]
        em[mask] = k[mask] + em[mask]

        # redefine mask
        mask = np.abs(g - k) > g * errtol

    return (np.pi / 2) * (ss + cc * em) / (em * (em + pp))


def cel(kcv: np.ndarray, pv: np.ndarray, cv: np.ndarray, sv: np.ndarray) -> np.ndarray:
    """
    combine vectorized and non-vectorized implementations for improved performance

    def ellipticK(x):
        return elliptic((1-x)**(1/2.), 1, 1, 1)

    def ellipticE(x):
        return elliptic((1-x)**(1/2.), 1, 1, 1-x)

    def ellipticPi(x, y):
        return elliptic((1-y)**(1/2.), 1-x, 1, 1)
    """
    n_input = len(kcv)

    if n_input < 10:
        return np.array([cel0(kc, p, c, s) for kc, p, c, s in zip(kcv, pv, cv, sv)])

    return celv(kcv, pv, cv, sv)


def cel_iter(qc, p, g, cc, ss, em, kk):
    """
    Iterative part of Bulirsch cel algorithm
    """
    # case1: scalar input
    #   This cannot happen in core functions

    # case2: small input vector - loop is faster than vectorized computation
    n_input = len(qc)
    if n_input < 15:
        result = np.zeros(n_input)
        for i in range(n_input):
            result[i] = cel_iter0(qc[i], p[i], g[i], cc[i], ss[i], em[i], kk[i])

    # case3: vectorized evaluation
    return cel_iterv(qc, p, g, cc, ss, em, kk)


def cel_iter0(qc, p, g, cc, ss, em, kk):
    """
    Iterative part of Bulirsch cel algorithm
    """
    while m.fabs(g - qc) >= qc * 1e-8:
        qc = 2 * m.sqrt(kk)
        kk = qc * em
        f = cc
        cc = cc + ss / p
        g = kk / p
        ss = 2 * (ss + f * g)
        p = p + g
        g = em
        em = em + qc
    return 1.5707963267948966 * (ss + cc * em) / (em * (em + p))


def cel_iterv(qc, p, g, cc, ss, em, kk):
    """
    Iterative part of Bulirsch cel algorithm
    """
    while np.any(np.fabs(g - qc) >= qc * 1e-8):
        qc = 2 * np.sqrt(kk)
        kk = qc * em
        f = cc
        cc = cc + ss / p
        g = kk / p
        ss = 2 * (ss + f * g)
        p = p + g
        g = em
        em = em + qc
    return 1.5707963267948966 * (ss + cc * em) / (em * (em + p))
