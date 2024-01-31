"""Annotations."""
import logging
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from roux.stat.transform import rescale

def _set_text(
    ax: plt.Axes,
    ha: str='center',
    va: str='center',
    # off_text=0,
    **kws,
    ) -> plt.Axes:
    """Set text on the plot

    Args:
        ax (plt.Axes): subplot
        ha (str, optional): horizontal alignment. Defaults to 'center'.
        va (str, optional): vertical alignment. Defaults to 'center'.

    Returns:
        plt.Axes: subplot
    """
    if ax.name!='polar':
        ax.text(
            # y=0,
            rotation=90,
            ha=ha,
            va=va,
            **kws,
        )    
    else:
        angle=kws['x']
        rotation = np.rad2deg(angle)

        if angle <= np.pi/2:
            # alignment = "center"
            rotation = rotation + 180 + 2*abs(rotation-90)            
        elif angle < 3*(np.pi/2):
            # alignment = "center"
            rotation = rotation - 2*abs(rotation-90)
        else: 
            # alignment = "center"
            rotation = rotation + 180 -  2*abs(rotation-270)#2*abs(rotation-90)# + 2*abs(rotation-90)            
            
        # logging.info(f"{angle:.1f} {ha},{va},{rotation}")
        ax.text(
            ha=ha, 
            va=va, 
            rotation=rotation, 
            rotation_mode="anchor",
            **kws,
        )
    return ax

def annot_labels(
    ax_chrom: plt.Axes, # A
    data: pd.DataFrame, # coordinates
    colx: str, # coordinates data
    chrom_y: float,
    col_label: str,
    loc: str='out', # out in
    col_start: str=None, # coordinates chrosomome plots
    ax: plt.Axes=None, # B:data
    coly: str=None, # data
    col_labelx: str='label x', 
    color: str='darkgray',
    yoff_scales: float=None,
    off_labels_segments: float=20,
    scale_polar: float=1.5,
    fig: plt.Figure=None,
    test: bool=False,
    ) -> plt.Axes:
    """Annot labels e.g. gene names

    Args:
        ax_chrom (plt.Axes): subplot with the chromosome plot
        col_label (str): column with the labels
        loc (str, optional): locations. Defaults to 'out'.
        color (str, optional): color. Defaults to 'darkgray'.
        yoff_scales (float, optional): y offset. Defaults to None.
        off_labels_segments (float, optional): offset for the label segments. Defaults to 20.
        scale_polar (float, optional): scale for the polar plot. Defaults to 1.5.
        fig (plt.Figure, optional): figure. Defaults to None.
        test (bool, optional): test-mode. Defaults to False.

    Returns:
        plt.Axes: subplot
    """
    if fig is None:
        fig=plt.gcf()                
    if col_start is None:
        col_start=colx
    ## labels
    ### rescale coordinates
    # data=data.assign(**{colx:lambda df: to_polar(df[colx],range1=[df[colx].min(),df[colx].max()],range2=xlim)})
    if ax_chrom.name != 'polar':
        df1=(data
            .sort_values(colx)
            .assign(**{col_labelx:lambda df: rescale(df[colx].rank(),range2=ax_chrom.get_xlim())})    
            )
    else:
        df1=(data
            .sort_values(colx)
            .assign(**{
                f'{colx} quadrant': lambda df : pd.cut(df[colx],bins=np.linspace(ax_chrom.get_xlim()[0],ax_chrom.get_xlim()[1],
                                                                                 off_labels_segments, ## shrink the spacing between the labels
                                                                                ),include_lowest=True),
            })
        )
        l1=[]
        for name,df in df1.groupby(f'{colx} quadrant',observed=False):
            # print(name.left,name.right,df[colx].nunique())
            if df[colx].nunique()==0:
                continue
            elif df[colx].nunique()==1:
                l1+=df[colx].tolist()
                continue
            range2=(name.left,name.right-((name.right-name.left)/df[colx].nunique()))
            # print(range2)
            l1+=rescale(
                    df[colx].rank(),
                    range2=range2
                       ).tolist()
            del range2
        assert len(l1)==len(df1)
        df1[col_labelx]=l1
        del l1
        # print(df1)
    ## annotations
    # scaled by the distance between the data plot and the cromosomes
    dist=chrom_y-ax_chrom.get_ylim()[0]
    chrom_yoff=-0.1 if loc=='out' else 0
    line1B_yoff=dist*(0.03 if loc=='out' else 0.95) if yoff_scales is None else yoff_scales[0]
    line2B_yoff=dist*(0.06 if loc=='out' else 0.85) if yoff_scales is None else yoff_scales[1]
    ## because the polar plots overlap, rectilinear stack
    line3A_yoff=dist*(0.09 if loc=='out' else 0.65) if yoff_scales is None else yoff_scales[2]
    # if not coly is None:
    #     line3B_yoff= data[coly].max()## TODO
    line3B_yoff=0
    if loc=='out':
        label_yoff =dist*(0.12*(scale_polar if ax_chrom.name=='polar' else 0.8) if yoff_scales is None else yoff_scales[3])
    else:
        label_yoff =(line3A_yoff+line2B_yoff)/2
    # print(dist*0.12)
    # print(f"label_yoff={label_yoff}")
    
    from matplotlib.patches import ConnectionPatch
    if loc=='out':
        # default
        # # -..to gene
        if test:
            logging.info(df1)
        _=df1.apply(lambda x:  fig.add_artist(
            ConnectionPatch(
                xyA=[x[col_start],chrom_y+chrom_yoff], 
                xyB=[x[col_start],ax_chrom.get_ylim()[1]+line1B_yoff], 
                coordsA=ax_chrom.transData,#"data", 
                coordsB=ax_chrom.transData,#"data",
                # axesA=ax_chrom,
                # axesB=ax,
                color=color,
                alpha=0.5,
                zorder=2,
                clip_on=False
            ),
            ),
            axis=1)
        # .-. chromosome
        _=df1.apply(lambda x:  fig.add_artist(
            ConnectionPatch(
                xyA=[x[col_start],ax_chrom.get_ylim()[1]+line1B_yoff], 
                xyB=[x[col_labelx],ax_chrom.get_ylim()[1]+line2B_yoff], 
                coordsA=ax_chrom.transData,#"data", 
                coordsB=ax_chrom.transData,#"data",
                # axesA=ax_chrom,
                # axesB=ax,
                color=color,
                alpha=0.5,
                zorder=2,
                clip_on=False
            ),
            ),
            axis=1)
        _=df1.apply(lambda x: fig.add_artist(
            ConnectionPatch(
                xyA=[x[col_labelx],ax_chrom.get_ylim()[1]+line2B_yoff], 
                xyB=[x[col_labelx],ax_chrom.get_ylim()[1]+line3A_yoff], 
                coordsA=ax_chrom.transData,#"data", 
                coordsB=ax_chrom.transData,#"data",
                # axesA=ax_chrom,
                # axesB=ax,
                color=color,
                alpha=0.5,
                zorder=2,
                clip_on=False
            ),
            ),
            axis=1)
        #..- to data
        if not coly is None:
            _=df1.apply(lambda x:  fig.add_artist(
                ConnectionPatch(
                    xyA=[x[col_start],chrom_y+chrom_yoff], 
                    xyB=[x[colx],ax.get_ylim()[1]+line3B_yoff], 
                    coordsA=ax_chrom.transData,#"data", 
                    coordsB=ax.transData,#"data",
                    axesA=ax_chrom,
                    axesB=ax,
                    color=color,
                    alpha=0.5,
                    zorder=2,
                    clip_on=False
                ),
                ),
                axis=1)
            _=df1.apply(lambda x:  fig.add_artist(
                ConnectionPatch(
                    xyA=[x[colx],ax.get_ylim()[1]+line3B_yoff], 
                    xyB=[x[colx],x[coly]], 
                    coordsA=ax.transData,#"data", 
                    coordsB=ax.transData,#"data",
                    axesA=ax,
                    axesB=ax,
                    color=color,
                    alpha=0.5,
                    zorder=2,
                    clip_on=False
                ),
                ),
                axis=1)
    else:
        # # -.. chromosome
        if test:
            logging.info(df1)
        _=df1.apply(lambda x:  fig.add_artist(
            ConnectionPatch(
                xyA=[x[col_start],chrom_y+chrom_yoff], 
                xyB=[x[col_start],ax_chrom.get_ylim()[0]+line1B_yoff], 
                coordsA=ax_chrom.transData,#"data", 
                coordsB=ax_chrom.transData,#"data",
                # axesA=ax_chrom,
                # axesB=ax,
                color=color,
                alpha=0.5,
                zorder=2,
                clip_on=False
            ),
            ),
            axis=1)
        # .-. gene
        _=df1.apply(lambda x:  fig.add_artist(
            ConnectionPatch(
                xyA=[x[col_start],ax_chrom.get_ylim()[0]+line1B_yoff], 
                xyB=[x[col_labelx],ax_chrom.get_ylim()[0]+line2B_yoff], 
                coordsA=ax_chrom.transData,#"data", 
                coordsB=ax_chrom.transData,#"data",
                # axesA=ax_chrom,
                # axesB=ax,
                color=color,
                alpha=0.5,
                zorder=2,
                clip_on=False
            ),
            ),
            axis=1)
        _=df1.apply(lambda x:  fig.add_artist(
            ConnectionPatch(
                xyA=[x[col_labelx],ax_chrom.get_ylim()[0]+line2B_yoff], 
                xyB=[x[col_labelx],ax_chrom.get_ylim()[0]+line3A_yoff], 
                coordsA=ax_chrom.transData,#"data", 
                coordsB=ax_chrom.transData,#"data",
                # axesA=ax_chrom,
                # axesB=ax,
                color=color,
                alpha=0.5,
                zorder=2,
                clip_on=False
            ),
            ),
            axis=1)
        # ..- data
        if not coly is None:
            _=df1.apply(lambda x:  fig.add_artist(
                ConnectionPatch(
                    xyA=[x[col_labelx],ax_chrom.get_ylim()[0]+line3A_yoff], 
                    xyB=[x[colx],ax.get_ylim()[1]+line3B_yoff], 
                    coordsA=ax_chrom.transData,#"data", 
                    coordsB=ax.transData,#"data",
                    axesA=ax_chrom,
                    axesB=ax,
                    color=color,
                    alpha=0.5,
                    zorder=2,
                    clip_on=False
                ),
                ),
                axis=1)
            _=df1.apply(lambda x:  fig.add_artist(
                ConnectionPatch(
                    xyA=[x[colx],ax.get_ylim()[1]+line3B_yoff], 
                    xyB=[x[colx],x[coly]], 
                    coordsA=ax.transData,#"data", 
                    coordsB=ax.transData,#"data",
                    axesA=ax,
                    axesB=ax,
                    color=color,
                    alpha=0.5,
                    zorder=2,
                    clip_on=False
                ),
                ),
                axis=1)
    if ax is None:
        ax=ax_chrom
    if ax.name !='polar':
        ax_chrom.axhspan(
            ymin=ax_chrom.get_ylim()[0],
            ymax=0,
             color='w',
             # zorder=0,
            )
    else:
        # print(
        #     ax_chrom.get_ylim(),
        #     ax_chrom.get_ylim()[1]-ax_chrom.get_ylim()[0],
        #     ax_chrom.get_ylim()[0]+line1B_yoff,
        #     (ax_chrom.get_ylim()[0]+line1B_yoff)-ax_chrom.get_ylim()[0],
        #     ((ax_chrom.get_ylim()[0]+line1B_yoff)-ax_chrom.get_ylim()[0])/(ax_chrom.get_ylim()[1]-ax_chrom.get_ylim()[0]),
        # )
        from chrov.viz.chrom import _set_span_polar 
        # print(ax_chrom.get_ylim())
        # print(((ax_chrom.get_ylim()[0]+line1B_yoff)-ax_chrom.get_ylim()[0])/(ax_chrom.get_ylim()[1]-ax_chrom.get_ylim()[0]))
        _set_span_polar(
            ax=ax_chrom,
            span_type='v',
            start=ax.get_xlim()[0],
            end=ax.get_xlim()[1],
            intervals=100,
            # ymin=0 if loc!='out' else ((ax_chrom.get_ylim()[0]+line1B_yoff)-ax_chrom.get_ylim()[0])/(ax_chrom.get_ylim()[1]-ax_chrom.get_ylim()[0]),
            ymax=0.85,# if loc=='out' else ((ax_chrom.get_ylim()[0])-ax_chrom.get_ylim()[0])/(ax_chrom.get_ylim()[1]-ax_chrom.get_ylim()[0]),
            color='w',
            )
    _=df1.drop_duplicates(subset=[col_label,col_labelx]).apply(lambda x: _set_text(
        ax=ax_chrom,
        x=x[col_labelx],
        y=(ax_chrom.get_ylim()[1 if loc=='out' else 0]+label_yoff),
        s=x[col_label],
        ha='center',# if loc!='out' and not ax_chrom.name=='polar' else 'left',
        va='bottom' if loc=='out' and ax_chrom.name!='polar' else 'center',
        ),axis=1)
    if ax.name == 'polar':
        ax.set(
            # xlabel=None,
            ylabel=None
        )
    return ax
    
def show_segments(
    ax: plt.Axes,
    y: float,
    offy: float,
    kind: str='arrows',
    segments: dict=None,
    segments_kws: dict={},
    offytext: float=0.2,
    arrow_kws: dict=dict(
        color='k',
        lw=1,    
        alpha=1,
        arrowstyle='<->',
        ),
    test: bool=False,
    **kws_annotate,
    )->plt.Axes:
    """Show segments aligned to chromosome arm.

    Args:
        ax (plt.Axes): subplot
        data (pd.DataFrame): input data
        size (int): size of the segments
    """    
    if segments is None:
        ## get the boundaries
        from roux.lib.set import get_windows
        df0=get_windows(
            **segments_kws,
            )
    else:
        def to_df(segments):
            if isinstance(segments,list):
                df0=pd.DataFrame(segments,columns=['start','end']).sort_values('start').reset_index(drop=True)
                df0.index.name='label'
                df0=df0.reset_index().assign(label=lambda df: df['label'].apply(lambda x: f"segment{x+1}"))
            elif isinstance(segments,dict):            
                df0=pd.DataFrame(segments,
                    index=['start','end']
                    ).T
            elif isinstance(segments,pd.DataFrame):            
                df0=segments
            else:
                raise ValueError(segments)
            ## post-processing
            return df0 
        df0=to_df(segments)
    if kind=='arrows':
        _=(df0
            .apply(lambda x: ax.annotate(
                text='', 
                xy=(x['start'],
                    y if (x.name%2)==0 else y-offy), 
                xytext=(x['end'],
                        y if (x.name%2)==0 else y-offy), 
                arrowprops=dict(
                    shrinkA=0,shrinkB=0,
                    **arrow_kws,
            ),
            **kws_annotate,
            ),
            axis=1)
        )
    elif kind=='bands':
        _=df0.apply(lambda x: ax.plot(
                [x['start'],x['end']],
                [y if (x['window#']%2)==0 else y-offy,y if (x['window#']%2)==0 else y-offy],
                solid_capstyle='butt',
                lw=10,#color='gray',
                # alpha=0.3,
            ),
            axis=1)
    else:
        raise ValueError(kind) 
        
    ## labels    
    if 'label' in df0:
        _=(df0
            .apply(lambda x: ax.text(
                x=np.mean([x['start'],x['end']]),
                y=y+offytext,
                s=x['label'] if 'label' in x else '', 
                ha='center',
                va='bottom',
            ),
            axis=1)
        )
    if not test:
        ax.axis('off')
    return ax    
