# AUTOGENERATED! DO NOT EDIT! File to edit: ../05_viz.ipynb.

# %% auto 0
__all__ = ["get_plot_path", "get_data_byeids", "plot_forms", "get_labels_pos"]

# %% ../05_viz.ipynb 5
## helper functions
import logging

logging.basicConfig(level=logging.INFO)

import pandas as pd

import roux.lib.df as rd  # noqa

from roux.viz.io import begin_plot, to_plot, read_plot
import matplotlib.pyplot as plt

from pathlib import Path

from .utils import get_cache_dir
from .domains import plot_domains


# from roux.lib.io import read_table,to_table
def get_plot_path(
    gene_id=None,  # kws_plot['gene_id']
    species=None,  # kws_plot['species']
    ensembl_release=None,  # kws_plot['ensembl_release']
    biotype=None,  # kws_plot['biotype']
    layout=None,  # kws_plot['layout']
    kws_plot={},
    # protein_coding=False,
    cache_dir_path=None,  #'pkg',
):
    if isinstance(kws_plot, dict):
        if gene_id is None and "gene_id" in kws_plot:
            gene_id = kws_plot["gene_id"]
        if species is None and "species" in kws_plot:
            species = kws_plot["species"]
        if ensembl_release is None and "ensembl_release" in kws_plot:
            ensembl_release = kws_plot["ensembl_release"]
        if biotype is None and "biotype" in kws_plot:
            biotype = kws_plot["biotype"]
        if layout is None and "layout" in kws_plot:
            layout = kws_plot["layout"]
        # protein_coding=kws_plot['protein_coding']
    if biotype.lower().startswith("p"):
        biotype = "protein"
    elif biotype.lower().startswith("t"):
        biotype = "transcript"
        # if protein_coding:
        #     biotype+='_protein_coding'
    else:
        raise ValueError(biotype)

    # if cache_dir_path=='pkg':
    cache_dir_path = get_cache_dir(
        # cache_dir_path
    )
    from roux.lib.str import encode

    outp = f"{cache_dir_path}/plot_domains/{species.replace(' ', '_')}/{ensembl_release}/{gene_id}/{biotype}/layout={layout}/{encode(kws_plot, short=True)}.pdf"
    return outp


## for mapping to the plots
def get_data_byeids(
    data,
):
    from roux.lib.set import list2str

    return (
        data.loc[
            :,
            data.filter(regex="^b.*").columns.tolist()
            + data.filter(regex="^eb.*").columns.tolist()
            + ["e.id"],
        ]
        .sort_values("b.id")
        .dropna(
            # subset=['e.id']
        )
        .drop_duplicates()
        .assign(
            **{
                "e.ids": lambda df: df.groupby("b.id")["e.id"].transform(
                    lambda x: list2str(
                        x.unique(),
                        fmt="id",
                    ),
                ),
                "b.xmin": lambda df: df.groupby("b.id")["eb.start"].transform("min"),
                "b.xmax": lambda df: df.groupby("b.id")["eb.end"].transform("max"),
                "b.x": lambda df: df.loc[:, ["b.xmin", "b.xmax"]].mean(axis=1),
            }
        )
        .drop(
            [
                "e.id",
                "eb.overlap",
                "eb.start",
                "eb.end raw",
                "eb.end",
                "eb.id",
                "eb.length",
            ],
            axis=1,
        )
        .drop_duplicates()
    )


def plot_forms(
    gene_id,
    species,
    ensembl_release,
    biotype,
    layout,
    protein_coding,
    return_data_for_mapping: bool = False,
    force=False,
    validate=False,
    ax=None,
    # kws_plot={},
    **kws_plot_domains,
):
    ## parameters
    kws_plot = dict(
        plot=dict(
            gene_id=gene_id,
            species=species,
            ensembl_release=ensembl_release,
            biotype=biotype,
            layout=layout,
            # protein_coding=protein_coding,
        ),
        plot_extra={
            **dict(
                return_data=True,
            ),
            **kws_plot_domains,
        },
    )

    outp = get_plot_path(
        gene_id=gene_id,
        species=species,
        ensembl_release=ensembl_release,
        biotype=biotype,
        layout=layout,
        kws_plot=kws_plot,
    )
    if "return_data" in kws_plot_domains:
        return_data = kws_plot_domains["return_data"]
    else:
        return_data = False
    if return_data_for_mapping:
        assert layout.lower().startswith("b"), (
            "return_data_for_mapping is only developed for blocks"
        )
        return_data = True
    if not Path(outp).exists() or force:
        data = None

        ## plot
        begin_plot()
        if ax is None:
            _, ax = plt.subplots(
                figsize=[4, 2],
            )
        data = plot_domains(
            **kws_plot["plot"],
            **kws_plot["plot_extra"],
            kws_legend=dict(
                title="Domains",
                ncol=2,
            ),
            data=data,
            ax=ax,
        )

        logging.info(f"saving cache to {outp}")
        try:
            to_plot(
                outp,
                kws_plot=kws_plot,
                data=data,
                validate=validate,
            )
        except:
            logging.warning("install roux[all] for to_plot to work")
    else:
        logging.info(f"reading cache from {outp}")
        ax = read_plot(
            outp,
            ax=ax,
            # kws_plot=kws_plot,
        )
        if return_data:
            from roux.lib.io import read_table

            data = read_table(Path(outp).with_suffix("").as_posix() + "/data.tsv")
    if not return_data:
        return ax
    else:
        if not return_data_for_mapping:
            return data
        else:
            return get_data_byeids(data)


def get_labels_pos(ax_gv):
    return (
        pd.DataFrame(
            # if t.get_position()[0]==1
            {
                t.get_text().strip(): t.get_position()
                for t in ax_gv.get_children()
                if isinstance(t, plt.Text)
                if t.get_text() != ""
                if "-" not in t.get_text()
            }
        )
        .T.rename(
            columns={
                0: "x",
                1: "y",
            },
            errors="raise",
        )
        .rename_axis(
            "t.id",
            axis=0,
        )
        .reset_index()
        .sort_values("y")
    )
