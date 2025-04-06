import marimo

__generated_with = "0.12.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy.stats import norm
    return mo, norm, np, plt


@app.cell
def _(mo):
    mean_slider = mo.ui.slider(start=-5, stop=5, step=0.1, value=0, label="Mean (μ)")
    sigma_slider = mo.ui.slider(start=0.1, stop=3, step=0.1, value=1, label="Standard Deviation (σ)")

    mean_slider, sigma_slider
    return mean_slider, sigma_slider


@app.cell
def _(mean_slider, norm, np, plt, sigma_slider):
    x = np.linspace(-10, 10, 400)
    mu = mean_slider.value
    sigma = sigma_slider.value
    y = norm.pdf(x, mu, sigma)

    fig, ax = plt.subplots()
    ax.plot(x, y, label=f'N({mu}, {sigma}^2)')
    ax.fill_between(x, y, alpha=0.2)
    ax.set_title("Normal Distribution")
    ax.set_xlabel("x")
    ax.set_ylabel("Density")
    ax.legend()

    fig
    return ax, fig, mu, sigma, x, y


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
