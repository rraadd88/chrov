import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from chrov.viz.chrom import _get_pi_range,to_polar,_format_polar_subplot,_concat_chroms

def plot_seaborn(
    data: pd.DataFrame,
    kind: str, # seaborn function name
    colx: str,
    coly: str,
    range1_chroms: list,
    arc: bool=True,
    pi_span: float=1,
    pi_start: int=0,
    pi_end: int=None,
    figsize: list=None,
    ax: plt.Axes=None,
    fig: plt.Figure=None,
    **kws_plot,
    ) -> tuple:
    """plot_seaborn _summary_

    Args:
        data (pd.DataFrame): input data
        kind (str): kind of plot, seaborn function name
        coly (str): column with y values
        range1_chroms (list): input range of chromosomes
        arc (bool, optional): arc/polar or linear/rectangular plots. Defaults to True.
        pi_span (float, optional): pi span. Defaults to 1.
        pi_start (int, optional): pi start position. Defaults to 0.
        pi_end (int, optional): pi end position. Defaults to None.
        figsize (list, optional): figure size. Defaults to None.
        ax (plt.Axes, optional): subplot. Defaults to None.
        fig (plt.Figure, optional): figure. Defaults to None.

    Returns:
        tuple: subplot and data

    TODOs:
        1. set rlabel position.
    """
    ## plot
    if ax is None:
        # if not arc:
        #     fig,ax=plt.subplots(figsize=figsize)
        #     df0=data.copy()
        # else:
        #     fig=plt.figure(figsize=figsize)
        if fig is None:
            fig=plt.gcf()
        ax=fig.add_axes(
            [0, 1, 1, 0.6],
            polar=arc,
            )
        ## TODO: in python>=3.8 with matplotlib>=3.7 used mosaic to make subplots: https://matplotlib.org/stable/gallery/subplots_axes_and_figures/mosaic.html#per-axes-subplot-keyword-arguments
    if ax.name=='polar':       
        xlim=_get_pi_range(pi_start=pi_start,pi_end=pi_end,pi_span=pi_span)
        
    df0=data.copy()
    if ax.name=='polar':
        # to_polar([df0[colx].min(),df0[colx].max()],
        #          range1=range1,
        #          range2=xlim,
        #         )
        df0=df0.assign(**{
            colx:lambda df: to_polar(df[colx],
                                     range1=range1_chroms,
                                     range2=xlim)
            # col_labelx:lambda df: to_polar(df[colx],range1=[df[colx].min(),df[colx].max()],range2=xlim)
        })
    if kind=='stem':
        ax.stem(df0[colx].tolist(),
                df0[coly].tolist(),
            basefmt='',
            **kws_plot,
            )
        if ax.name!='polar':
            ax.set(
                ylabel=coly,
                ylim=[kws_plot['bottom'] if 'bottom' in kws_plot else df0[coly].min(),df0[coly].max()]
            )        
    else:
        getattr(sns,kind)(
            data=df0,
            x=colx,
            y=coly,
            color='k',
            # clip_on = False,
            ax=ax,
            **kws_plot,
        )

    ax.set_clip_on(False)
    if ax.name!='polar':
        ax.margins(x=0.01)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
    else:
        if pi_start==0 and pi_span==2:
            ax.set_rlabel_position(0)            
        if pi_start==0 and pi_span>=1:
            ax.set_rlabel_position(180)
        else:
            ax.set_rlabel_position(0)
            
        label_position=ax.get_rlabel_position()
        import numpy as np
        ax.text(
                x=np.radians(label_position),
                y=ax.get_rmax()/2.,
                s=coly,
                rotation=label_position if label_position!=180 else 0,
                ha='center',va='top'
               )
        _format_polar_subplot(ax=ax,
                              xlim=xlim,
                              # xlim=[xlim[0]-0.1,xlim[1]+0.1],
                             )
        ax.set(xticklabels=[],
               xlabel=None,ylabel=None,
              )
        ax.xaxis.grid(False)
        ax.yaxis.grid(color='whitesmoke',zorder=-1) # < lightgray connectors
        ax.spines['polar'].set_visible(False)
        ax.set_frame_on(False)
        # ax.text(0.25, 0.15, coly, transform=ax.transAxes,ha='center')
        
    return ax,df0

def heatmaps_strips(
    data: pd.DataFrame,
    strips_kws: dict,
    fig: plt.Figure=None,
    axs: list=None,
    kws_subplots: list={},
    ) -> tuple:
    """Plot heatmap strips

    Args:
        data (pd.DataFrame): input data
        strips_kws (dict): keyword arguments provided to strips
        fig (plt.Figure, optional): figure. Defaults to None.
        axs (list, optional): subplots. Defaults to None.
        kws_subplots (list, optional): keyword arguments provided to subplots. Defaults to {}.

    Returns:
        tuple: figure and subplots
    """
    if fig is None:
        fig,axs=plt.subplots(
            len(strips_kws),1,
            **kws_subplots
            )
    from roux.lib.str import linebreaker
    for axi,(ax,c) in enumerate(zip(axs,strips_kws.keys())):
        sns.heatmap(
            data.set_index('gene symbol label').loc[:,[c]].T,
            ax=ax,
            cbar_kws=dict(
                aspect=10,
            ),
            **strips_kws[c],
            )
        cbar = ax.collections[0].colorbar
        cbar.ax.tick_params(labelsize=11)
        cbar.set_label(
                linebreaker(c,20),
                       rotation=0,
                        # loc='center',
                        ha='left',
                        va='center',
                      )
        # cbar.ax.yaxis.set_label_coords(15,0.5)
        # cbar_ax.yaxis.label.set_size(20)
        ax.set(
            xlabel=None,
            ylabel=None,
            yticks=[],
            yticklabels=[],
        # **set_kws,
        )
        if len(data)>20 or axi!=len(strips_kws)-1:
            ax.set(        
                xticklabels=[]
            )        
    return fig,axs