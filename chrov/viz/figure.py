import pandas as pd
import matplotlib.pyplot as plt

from chrov.viz.plot import plot_seaborn
from chrov.viz.chrom import annot_chroms, _concat_chroms
from chrov.viz.annot import annot_labels

def plot_with_chroms(
    data: pd.DataFrame,
    cytobands: pd.DataFrame,
    kind: str,
    colx: str,
    coly: str,
    col_label: str,
    va: str,
    col_start: str=None,
    xkind: str='loci', # colx contains coordinates
    coffy: str=None,
    off: float=None,
    offy: float=None,
    chrom_y: float=0,
    show_genome: bool=False,
    arc: bool=True,
    pi_span: float=1,
    pi_start: int=0,
    pi_end: int=None,
    fig: plt.Figure=None,
    figsize: list=None,
    ax_data: plt.Axes=None,
    kws_seaborn: dict={},
    kws_annot_chroms: dict={},
    kws_annot_labels: dict={},
    test: bool=False,
    ) -> plt.Figure:
    """Plot with chromosomes.

    Args:
        data (pd.DataFrame): input table
        cytobands (pd.DataFrame): cytobands
        kind (str): kind of plot
        colx (str): column with x values
        coly (str): column with y values
        col_label (str): column with labels
        va (str): vertical alignment
        col_start (str, optional): column with start positions. Defaults to None.
        xkind (str, optional): kind of x values. Defaults to 'loci'.
        off (float, optional): offset scale of the chromosome plot. Defaults to None.
        offy (float, optional): offset y of the chromosome plot. Defaults to None.
        chrom_y (float, optional): chromosome y-position. Defaults to 0.
        arc (bool, optional): arc/polar plot or linear/rectangular one. Defaults to True.
        pi_span (float, optional): pi span. Defaults to 1.
        pi_start (int, optional): pi start. Defaults to 0.
        pi_end (int, optional): pi end. Defaults to None.
        fig (plt.Figure, optional): figure. Defaults to None.
        figsize (list, optional): figure size. Defaults to None.
        ax_data (plt.Axes, optional): subplot with the data plot. Defaults to None.
        kws_seaborn (dict, optional): keyword parameters to seaborn plot. Defaults to {}.
        kws_annot_chroms (dict, optional): keyword parameters to the chromosome plot. Defaults to {}.
        kws_annot_labels (dict, optional): keyword parameters to the annotations of the labels. Defaults to {}.
        test (bool, optional): test mode. Defaults to False.

    Returns:
        plt.Figure: figure
    """
    if fig is None and not figsize is None:
        fig=plt.figure(figsize=figsize)
    else:
        fig=plt.gcf()
    if ax_data is None:
        ax_data=plt.subplot(polar=arc)
        ax_data_external=False
    else:
        ax_data_external=True
    if col_start is None and xkind=='loci':
        col_start=colx
        
    if not show_genome:
        cytobands=cytobands.query(expr=f"`chromosome` == {data['chromosome'].drop_duplicates().tolist()}")
    
    # if off is None:
    #     if not arc:
    #         off=0.9
    #     else:
    #         off=0.1
    data=data.astype({'chromosome':str})
    ## background
    ax_chrom,df1=annot_chroms(
        # ax=ax_data, # data
        data=cytobands,
        chromosomes=data['chromosome'].unique(),
        ax_chrom=None,
        chrom_y=chrom_y,
        out_data=True,
        pi_span=pi_span,
        # **kws_plot,
        kws_add_ax=dict(
            arc=arc,
            off=off,
            offy=offy,
            va=va,
            ax_with=ax_data,
            ),
        **kws_annot_chroms,
    )
    ax_chrom.set(ylim=[-0.6,0.1])
    # return
        
    if xkind=='loci':
        ## get coordinates of the labels on the joined chromosomes
        colx_data=colx+' chroms'
        col_start=colx_data
        df2=_concat_chroms(
                data,
                col_start=colx,
                col_end=colx,
                col_chroms_start=colx_data,
                col_chroms_end=colx_data,
                genome_ends=df1.set_index('chromosome')['genome end'],
            )
    else:
        colx_data=colx
        _col_start=col_start
        col_start+=' chroms'
        data=_concat_chroms(
                data,
                col_start=_col_start,
                col_end=_col_start,
                col_chroms_start=col_start,
                col_chroms_end=col_start,
                genome_ends=df1.set_index('chromosome')['genome end'],
            )
        
    if not ax_data_external:
        ## plot: middle
        ax_data,df3=plot_seaborn(
            df2,
            colx=colx_data,
            coly=coly,
            kind=kind,
            range1_chroms=[1, ## for polar
                           (cytobands
                           .groupby('chromosome',sort=False)['end']
                           .max().sum())
                          ],
            arc=arc,
            pi_span=pi_span,
            pi_start=pi_start,
            pi_end=pi_end,
            figsize=None,
            ax=ax_data,
            # fig=fig,
            **kws_seaborn,
            )
        df3=df3 if coffy is None else df3.query(expr=f"`{coly}` > {coffy}")
    else:
        if xkind=='loci':
            df3=df2.copy()
        else:
            df3=data.copy()            
    ax_data.set(zorder=1)
    ## labels: top
    ## filter for labels
    annot_labels(
        ax_chrom=ax_chrom, # A
        ax=ax_data, # B:data
        colx=colx_data,
        col_start=col_start,
        coly=coly,
        data=df3,
        chrom_y=chrom_y,
        col_label=col_label,
        fig=fig,
        **kws_annot_labels,
        test=test,
        )
    # return fig
    return {"chrom":ax_chrom,'data': ax_data,}

from functools import partial
plot_with_genome=partial(plot_with_chroms, show_genome=True,)