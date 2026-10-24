"""Tests of the chromosome plots."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pandas as pd  # noqa: E402


def test_plot_arm_draws_gvar_and_stalk_bands():
    from chrov.viz.chrom import plot_arm

    cytobands = pd.read_table(
        f"{Path(__file__).resolve().parents[1]}/modules/inputs/cytobands.tsv",
        index_col=[0],
    )
    data = cytobands.query(expr="`chromosome arm` == 'chr13p'")
    band_count = data["cytoband type"].isin(["gvar", "stalk"]).sum()
    assert band_count == 3
    ax = plot_arm(data=data)
    alphas = [line.get_alpha() for line in ax.get_lines()]
    assert alphas.count(0.6) == 2  # gvar
    assert alphas.count(0.15) == 1  # stalk


def test_plot_chrom_shows_both_arms():
    from chrov.viz.chrom import plot_chrom

    cytobands = pd.read_table(
        f"{Path(__file__).resolve().parents[1]}/modules/inputs/cytobands.tsv",
        index_col=[0],
    )
    data = cytobands.query(expr="`chromosome` == '13'")
    ax = plot_chrom(data=data)
    assert list(ax.get_xlim()) == [data["start"].min(), data["end"].max()]
