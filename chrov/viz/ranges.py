import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

import roux.lib.dfs as rd

from chrov.viz.chrom import plot_arm

def plot_ranges(
    data:pd.DataFrame,
    col_id: str,
    col_start: str,
    col_end: str,
    start: int=None,
    end: int= None,
    hue: str= None,
    y=None, # rank
    kind=None,
    strand: str='+',
    cytobands: dict=None,
    cytobands_y: float = None,
    col_groupby: str=None,
    group_x: float=-0.22,
    # col_sortby: str=None,
    sort_ascending: bool=False,
    show_labels: str= True,
    col_label: str=None,
    col_label_right: str=None,
    color: str='b',
    colors: dict=None,
    palette: str= 'Set2',
    hue_lim: list= [],
    lw: int = 10,
    zorders: dict=None,
    show_segments: bool=False,
    xtick_interval:float=None,
    unit: str='Coordinate (bp)',
    test: bool=False,
    kws_legend:dict={},
    kws_hlines:dict={}, 
    ax: plt.Axes=None,
    )-> plt.Axes:
    """Plot ranges.

    Args:
        data (pd.DataFrame): input data.
        col_id (str): column with ids.
        col_start (str): column with start co-ordinates.
        col_end (str): column with end co-ordinates.
        end (int): end position for the plot
        start (int, optional): start position for the plot. Defaults to 0.
        hue (str, optional): column with color. Defaults to None.
        y (_type_, optional): column with y positions. Defaults to None.
        cytobands (dict, optional): cytobands to plot the chromosomes. Defaults to None.
        cytobands_y (float, optional): cytobands y-position. Defaults to None.
        col_groupby (str, optional): column to group by. Defaults to None.
        col_sortby (str, optional): column to sort by. Defaults to None.
        col_label (str, optional): column with labels. Defaults to None.
        col_label_right (str, optional): column with labels to be shown on the right side of the ranges. Defaults to None.
        colors (dict, optional): colors. Defaults to None.
        lw (int, optional): line width. Defaults to 10.
        zorders (dict, optional): z-orders. Defaults to None.
        show_segments (bool, optional): show segments. Defaults to False.
        xtick_interval (float, optional): x tick intervals. Defaults to None.
        test (bool, optional): test-mode. Defaults to False.
        ax (plt.Axes, optional): subplot. Defaults to None.

    Raises:
        ValueError: if kind is not 'split','separate' or 'joined'

    Returns:
        plt.Axes: subplot
    """
    assert len(data)!=0
    
    if ax is None:
        # fig,ax=plt.subplots(figsize=[3,len(data)*0.05])
        ax=plt.gca()
    from roux.viz.colors import saturate_color
    from roux.viz.ax_ import set_legend_custom
    
    if start is None:
        start=data[col_start].min()
    if end is None:
        end=data[col_end].max()

    assert not all(data[col_start]==data[col_end]), "lengths of all ranges is 0."
    ## trim data
    df1=(data
        .log.dropna(
            subset=[col_id,col_start,col_end]
        )
        # .sort_values(col_start,ascending=False)
        .assign(
        **{
            col_start: lambda df: df[col_start].apply(lambda x: x if x >= start else start), # trim
            col_end: lambda df: df[col_end].apply(lambda x: x if x <= end else end), # trim
        }
    ))    
    ## test for unique ids
    if kind is not None:
        if kind.lower().startswith('join'):
            col_label=None
    if col_label is None:
        col_label=col_id
        
    # if not col_sortby is None:
    #     df1=df1.sort_values(col_sortby,ascending=sort_ascending)
        
    if y is None:
        y='y'
        if kind in [None,'split','separate']: 
            df1=(df1
                .rd.assert_no_dups(col_id)
                .assign(
                    **{
                        y:np.arange(len(df1)),
                    }
                )
                )
        elif kind=='joined':
            df1=(
                df1
                .assign(
                    **{
                        y:lambda df: df.groupby(col_id,sort=False)[col_id].ngroup()
                    }#.transform(lambda x: range(len(x))))
                    )
            )
        else:
            raise ValueError(kind)
        assert y in df1
    if not hue is None:
        if df1[hue].dtype=='float':
            from roux.viz.colors import get_val2color
            # get_val2color?
            colors,colors_legend=get_val2color(
                df1[hue],
                vmin=hue_lim[0],
                vmax=hue_lim[1],
                cmap=palette,
            )
        else:
            if colors is None:
                from roux.viz.colors import get_ncolors
                colors=get_ncolors(
                    df1[hue].nunique(),
                    cmap=palette,
                    )
            if isinstance(colors,list):
                colors=dict(zip(df1[hue].unique(),colors))        
    if zorders is None:
        zorders={}

    ## lines
    _=df1.apply(lambda x: 
        ax.hlines(
            y=x[y],
            xmin=x[col_start],
            xmax=x[col_end],
            color=colors[x[hue]] if not hue is None else color,
            lw=lw,
            **kws_hlines,
            ) if not pd.isnull(x[y]) else None,
            axis=1,
           )
    ax.invert_yaxis()
    # labels
    if show_labels:
        if kind in [None,'split','separate']:            
            _=df1.apply(lambda x: ax.text(
                x=x[col_start],
                y=x[y],
                s=f"{x[col_label]} ",
                ha='right',va='center',
                # color=x['label_color'],
                ) if not pd.isnull(x[y]) else None,
            axis=1)
            if not col_label_right is None:
                _=df1.apply(lambda x: ax.text(
                        x=x[col_end],
                        y=x[y],
                        s=f"{x[col_label_right]} ",
                        ha='left',
                        va='center',
                        # color=x['label_color'],
                        ),
                        axis=1,
                       )                
        elif kind.lower().startswith('join'):
            _=(
                df1
                .loc[:,[col_label,y]]
                .drop_duplicates()
                .apply(lambda x: ax.text(
                    x=start if strand!='-' else end,
                    y=x[y],
                    s=f"{x[col_label]} ",
                    ha='right',
                    va='center',
                    # color=x['label_color'],
                    ),
                    axis=1)
              )        
    # _=df1.apply(lambda x: ax.plot(
    #     [x['start'],x['end']],[x[y],x[y]],
    #     color=colors[x[hue]] if x[hue] in colors else 'w',
    #     # alpha=1,
    #     solid_capstyle='butt',
    #     # zorder=2,
    #     zorder=zorders[x[hue]] if x[hue] in zorders else 2,
    #     lw=lw,
    #     ),
    #     axis=1)
    if not cytobands is None:
        if cytobands_y is None:
            cytobands_y=df1['y'].max()+1
        plot_arm(
            cytobands,
            y=cytobands_y,
            lw=lw,
            ax=ax,
            test=True,
        )
    if show_segments:
        from chrov.viz.chr import plot_segments
        plot_segments(ax)

    if not hue is None:    
        set_legend_custom(
            ax,
            legend2param=colors_legend if df1[hue].dtype=='float' else colors,
            param='color',
            lw=lw,
            marker=None,
            markerfacecolor=True,
            size=10,
            color='k',
            linestyle='-',
            **{
                **dict(
                    title=hue,
                    frameon=False,
                    bbox_to_anchor=[0.5,0],
                    loc='upper center',
                    ncol=3,
                    handlelength=0.1,
                ),
                **kws_legend,
            }
        )
    
    ## show groups
    if col_groupby in df1:
        df_=df1.loc[:,[y,col_groupby]].drop_duplicates()
        ax.set(
            yticks=df_[y].tolist(),
            yticklabels=df_.apply(
                lambda x: f"{x[col_groupby]}:{x[y]}",
                axis=1,
            ),
        )
        from roux.viz.ax_ import split_ticklabels
        split_ticklabels(
            ax=ax,
            axis='y',
            fmt='group',
            sep=":",
            group_x=group_x, ## todo: infer
            test=test,
        )
    # else:
    if not test:
        ax.axes.yaxis.set_visible(test)
    
    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    ax.spines['top'].set_color('k')
    if not cytobands_y is None:
        ax.spines['top'].set_position(('data', cytobands_y+0.25))
        
    # removing the ax box lines
    _=plt.setp(
        ax.spines.values(),
        zorder=0,
        color='none',
    )
    # _=plt.setp([ax.get_xticklines(), ax.get_yticklines()], zorder=0)
    
    if not xtick_interval is None:
        ## set tick intervals
        import matplotlib.ticker as plticker
        loc = plticker.MultipleLocator(base=xtick_interval) # this locator puts ticks at regular intervals
        ax.xaxis.set_major_locator(loc)
    
    ax.set(
        xlim=[start,end],
        ylim=[df1[y].min()-0.5,df1[y].max()+1.5],
        xlabel=unit,
    )
    if strand=='-':
        ax.invert_xaxis()    
    return ax