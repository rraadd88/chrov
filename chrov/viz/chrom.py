"""Chromosome plots"""
import logging
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

import roux.lib.df as rd
from roux.stat.transform import rescale
from roux.viz.ax_ import get_line_cap_length

def _to_polar_intrapolate(
    start: int,
    end: int,
    interval: int=None,
    intervals: int=None,
    ) -> list:
    """Interpolate polar for smoothing.

    Args:
        start (int): start position
        end (int): end position
        interval (int, optional): interval size. Defaults to None.
        intervals (int, optional): number of intervals. Defaults to None.

    Raises:
        ValueError: either interval or intervals should be provided.

    Returns:
        list: interpolated positions
    """
    if not intervals is None:
        interval=(end-start)/intervals
    if interval is None and intervals is None:
        raise ValueError('either interval or intervals should be provided.')
    if end-start > interval:
        a1=np.append(np.arange(start,end,interval),end)
    else:
        a1=np.array([start,end])
    return a1

def _to_polar_chrom(
    range1_local: list,
    range1_global: list,    
    kws_plot_arm: dict,
    ax: plt.Axes,
    ):
    """To polar chromosome.

    Args:
        range1_local (list): local coordinates e.g. chrom
        range2_global (list): global coordinates e.g. genome
        kws_plot_arm (dict): keywords provided to `plot_arm` function
        ax (plt.Axes): plt.Axes
    """
    if ax.name=='polar':
        return {k:{k1:range1_local if k1=='range1' else rescale(a=range1_local,range1=range1_global,range2=kws_plot_arm['kws_pre_xys']['range2']) if k1=='range2' else v1 for k1,v1 in v.items()} if k=='kws_pre_xys' else v for k,v in kws_plot_arm.items()}
    else:
        return kws_plot_arm
    
def to_polar(
    a: list,
    range1: list=None,
    range2: list=None,
    interval: int=None,
    # test=False,
    ) -> list:
    """To polar coordinates

    Args:
        a (list): Coordinates
        range1 (list, optional): range1. Defaults to None.
        range2 (list, optional): range2. Defaults to None.
        interval (int, optional): interval size. Defaults to None.

    Raises:
        ValueError: Coordinates format

    Returns:
        list: rescaled coordinates
    """
    if not interval is None:
        a=sorted(a)
        if len(a)==2:
            start,end=a
        elif len(a)>2:
            start,end=a[0],a[-1]
        else:
            raise ValueError(a)
        a=_to_polar_intrapolate(
            start,
            end,
            interval,
        )
    range1=range1 if not range1 is None else [min(a),max(a)]
    return rescale(
        a,
        range1=range1,
        range2=[0,2*np.pi] if range2 is None else range2,
        )
            
def _pre_xys(
    xs: list,
    ys: list=None,
    polar: bool=False,
    **kws_to_polar,
    ) -> list:
    """Pre-process coordinates.

    Args:
        xs (list): x coordinates
        ys (list, optional): y coordinates. Defaults to None.
        polar (bool, optional): polar coordinates or not. Defaults to False.

    Returns:
        list: coordinates
    """
    if not polar:
        return xs,ys
    else:
        xs=to_polar(
            a=xs,
            **kws_to_polar,
        )
        assert len(set(ys))==1
        ys=np.repeat(ys[0],len(xs))
        return xs,ys
    
def _get_pi_range(
    pi_span: float=1,
    pi_start: int=0,
    pi_end: int=None,
    ) -> list:
    """Get pi range

    Args:
        pi_span (float, optional): pi span. Defaults to 1.
        pi_start (int, optional): pi start. Defaults to 0.
        pi_end (int, optional): pi end. Defaults to None.

    Returns:
        list: pi range
    """
    return [pi_start*np.pi,
            (pi_start+pi_span)*np.pi if pi_end is None else pi_end*np.pi]

def _format_polar_subplot(
    ax: plt.Axes,
    xlim: list,
    **kws_set
    ) -> plt.Axes:
    """Format polar subplot

    Args:
        ax (plt.Axes): plt.Axes
        xlim (list): x axis limits

    Returns:
        plt.Axes: subplot
    """
    if ax.name=='polar':
        if ax.get_theta_offset()!=np.pi:
            # ax.set_theta_zero_location("W")
            ax.set_theta_offset(np.pi)
        if ax.get_theta_direction()!=-1:
            ax.set_theta_direction(-1)      
        ax.set(xlim=xlim,**kws_set)
    return ax

def plot_arm(
    data: pd.DataFrame,
    arc: bool=False,
    col_start: str='start',
    col_end: str='end',
    y: float = 0,
    lw: float = 10,
    ec: str='k',
    color_centromer='#dbc1c1',
    pi_span: float=1,
    pi_start: int=0,
    pi_end: int=None,
    polar_smoothness_scale: float=1,
    kws_pre_xys: dict=None,
    figsize: list=None,
    ax: plt.Axes=None,
    test: bool=False,
    solid_capstyle='round',
    )->plt.Axes:
    """Plot chromosome arm.

    Args:
        data (pd.DataFrame): input table.
        y (float, optional): y position. Defaults to 0.
        lw (float, optional): line width. Defaults to 20.
        ec (str, optional): edge color. Defaults to 'k'.
        ax (plt.Axes, optional): subplot. Defaults to None.
        test (bool, optional): test-mode. Defaults to False.
    
    Returns:
        plt.Axes: subplot
    """
    ## subplot
    ax=_get_ax(ax=ax,arc=arc,figsize=figsize)
    
    if isinstance(data,dict):
        data=pd.DataFrame(data)
    assert data['chromosome'].nunique()==1, f"multiple chromosomes provided: {data['chromosome'].unique()}"
    start,end=data[col_start].min(),data[col_end].max()
    if ax is None:
        fig,ax=plt.subplots(figsize=[5,1])
    # to_set the line width
    if kws_pre_xys is None:
        kws_pre_xys={}
    ax.set(
        xlim=_pre_xys([start,end],['tmp'],**{k:v for k,v in kws_pre_xys.items() if k!='interval'})[0]
        )
    if solid_capstyle=='round':
        offx=get_line_cap_length(ax,linewidth=lw)[0]
    else:
        offx=0
    # print('kws_pre_xys',kws_pre_xys)
    if ax.name=='polar':
        kws_pre_xys['polar']=True
        if solid_capstyle!='butt':
            logging.info("For curcular/polar plot, `solid_capstyle` can only be set to 'butt'. Other styles are currently not supported.")
            solid_capstyle='butt'
        if not 'range1' in kws_pre_xys:
            kws_pre_xys['range1']=start,end
        if not 'range2' in kws_pre_xys:
            assert pi_span>0 and pi_span<=2 
            kws_pre_xys['range2']=_get_pi_range(pi_span=pi_span,pi_start=pi_start,pi_end=pi_end)
        if not 'interval' in kws_pre_xys:
            kws_pre_xys['interval']=(end-start)/(100*polar_smoothness_scale)
    else:
        kws_pre_xys['polar']=False
    if not 'cytoband type' in data:
        logging.warning('cytoband type not found in the data')
    else:
        ## cytobands
        data.loc[data['cytoband type'].str.startswith('gpos'),:].apply(lambda x: ax.plot(
            *_pre_xys(
                [x[col_start],x[col_end]],[y,y],**kws_pre_xys),

            lw=lw,solid_capstyle='butt',
            alpha=int(x['cytoband type'].replace('gpos',''))*0.01,
            color='k',zorder=2,clip_on=False,
            ),axis=1)
        data.loc[data['cytoband type'].str.startswith('gneg'),:].apply(lambda x: ax.plot(
            *_pre_xys(
                [x[col_start],x[col_end]],[y,y],**kws_pre_xys),

            lw=lw,solid_capstyle='butt',
            color='w',alpha=1,
            zorder=1,clip_on=False,
            ),axis=1)
        ## centromere
        data.loc[(data['cytoband type']=='acen'),:].log().apply(lambda x: ax.plot(
            *_pre_xys([x[col_start],x[col_end]],[y,y],**kws_pre_xys),

            lw=lw*0.75,solid_capstyle='butt',
            color=color_centromer,#'lightcoral', ##F5B8B7
            zorder=2,clip_on=False,
            ),axis=1)
        ## outlines
        start_line,end_line=data.query("`cytoband type`!='acen'").agg({col_start:'min',col_end:'max'}).tolist()
        ax.plot(
            *_pre_xys([start_line+offx,end_line-offx],[y,y],**kws_pre_xys),
            lw=lw+2, solid_capstyle=solid_capstyle,
            color=ec,zorder=1,clip_on=False
            )
        ax.plot(
            *_pre_xys([start_line+offx,end_line-offx],[y,y],**kws_pre_xys),
            lw=lw, solid_capstyle=solid_capstyle,
            color='w',zorder=1,clip_on=False
            )
    if not test:
        ax.axis('off')
    _format_polar_subplot(
        ax=ax,
        xlim=kws_pre_xys['range2'] if 'range2' in kws_pre_xys else None,
    )
    return ax

def plot_chrom(
    data: pd.DataFrame,
    arc: bool=False,
    col_start: str='start',
    col_end: str='end',
    col_arm: str='arm',
    pi_span: float=1,
    pi_start: int=0,
    pi_end: int=None,
    ax: plt.Axes=None,
    figsize: list=None,
    **kws_plot_arm,
    ) -> plt.Axes:
    """Plot a chromosome

    Args:
        data (pd.DataFrame): cytobands
        arc (bool, optional): arc/polar mode. Defaults to False.
        col_start (str, optional): column with start positions. Defaults to 'start'.
        col_end (str, optional): column with end positions. Defaults to 'end'.
        col_arm (str, optional): column with arm names. Defaults to 'arm'.
        pi_span (float, optional): pi span. Defaults to 1.
        pi_start (int, optional): pi start. Defaults to 0.
        pi_end (int, optional): pi end. Defaults to None.
        ax (plt.Axes, optional): subplot. Defaults to None.
        figsize (list, optional): sigure size. Defaults to None.

    Returns:
        plt.Axes: subplot
    """
    ## subplot
    ax=_get_ax(ax=ax,arc=arc,figsize=figsize)
    if not 'kws_pre_xys' in kws_plot_arm:
        kws_plot_arm['kws_pre_xys']={}
    if not 'range2' in kws_plot_arm['kws_pre_xys']:
        assert pi_span>0 and pi_span<=2 
        kws_plot_arm['kws_pre_xys']['range2']=_get_pi_range(pi_span=pi_span,pi_start=pi_start,pi_end=pi_end)
    _=data.sort_values(col_start).groupby(col_arm,sort=False,observed=False).apply(lambda df: plot_arm(
        data=df,
        col_start=col_start,
        col_end=col_end,
        **_to_polar_chrom(
            range1_local=[df[col_start].min(),df[col_end].max()],
            range1_global=[data[col_start].min(),data[col_end].max()],
            kws_plot_arm=kws_plot_arm,
            ax=ax,
        ),
        ax=ax
        ))
    if ax.name=='polar':
        try:
            ax.set(xlim=rescale(
                [data[col_start].min(),data[col_end].max()],
                range2=kws_plot_arm['kws_pre_xys']['range2'],
            ))    
        except:
            print(
            [data[col_start].min(),data[col_end].max()],
             kws_plot_arm['kws_pre_xys']['range2'],
        )

    return ax

def _rescale_to_chroms(
    df: pd.DataFrame,
    col_start: str,
    col_chrom_start: str,
    col_chroms_start: str,
    col_end: str=None,
    col_chroms_end: str=None,
    ) -> pd.DataFrame:
    """Rescale coordinates to joined chromosomes.

    Args:
        df (pd.DataFrame): cytobands
        col_start (str): column with gene start position
        col_chrom_start (str): column with chromosome start position
        col_chroms_start (str): column with chromosomes start position
        col_end (str, optional): column with end position. Defaults to None.
        col_chroms_end (str, optional): column with chromosomes end position. Defaults to None.

    Returns:
        pd.DataFrame: rescaled positions
    """
    df=df.assign(
        **{
            col_chroms_start:lambda df: df.apply(lambda x: x[col_chrom_start]-1+x[col_start]  ,axis=1),
        }
        )
    if not col_chroms_end is None:
        df=df.assign(
            **{
                col_chroms_end:lambda df: df.apply(lambda x: x[col_chrom_start]-1+x[col_end]  ,axis=1),
            }
            )
    return df

def _sort_chroms(
    data: pd.DataFrame,
    col_start: str=None,
    chromosomes: list=None,
    ) -> pd.DataFrame:
    """Sort chromosome.

    Args:
        data (pd.DataFrame): cytoband
        col_start (str, optional): column with start position. Defaults to None.
        chromosomes (list, optional): list of chromosomes. Defaults to None.

    Returns:
        pd.DataFrame: table with sorted chromosomes.
    """
    def _format_chrom_names(x): return int(x) if isinstance(x,float) else x if isinstance(x,int) else int(x) if x.isnumeric() else x
    ## sort chroms
    data=(data
        .assign(
            **{
            'chromosome': lambda df: df['chromosome'].apply(
                # lambda x: int(x) if x.isnumeric() else x
                _format_chrom_names,
            ),
            'chrom name instance': lambda df: df['chromosome'].apply(lambda x: not isinstance(x,int)),
        }
        )
        .sort_values(['chrom name instance','chromosome'],ascending=[True,True])
    )
    chromosomes_all=data['chromosome'].drop_duplicates().tolist()
    if chromosomes is None:
        # sort chromosomes
        chromosomes=list(map(_format_chrom_names,chromosomes_all))
        if len(chromosomes)>1 and len(chromosomes)!=len(chromosomes_all):
            logging.warning(f"chromosomes order not provided. inferred one: {chromosomes}")
    else:
        chromosomes=list(map(lambda x: _format_chrom_names(x), chromosomes))
        from roux.lib.set import assert_overlaps_with
        assert_overlaps_with(chromosomes,chromosomes_all)
        ## sort
        chromosomes=[k for k in chromosomes_all if k in chromosomes]
        ## filter
        data=(data.log.query(expr=f"`chromosome` == {chromosomes}"))   
    assert len(data)!=0, (chromosomes)
    # print(data)
    data.rd.assert_no_na(subset=['chromosome'])
    
    # sort loci
    data=(data
        .rd.astype_cat(col='chromosome', cats=chromosomes)
        .sort_values(['chromosome']+([] if col_start is None else [col_start]))
        )
    return data

def _concat_chroms(
    data: pd.DataFrame,
    col_start: str,
    col_end: str,
    col_chroms_start: str,
    col_chroms_end: str,
    col_chrom_start: str='col_chrom_start',
    col_chrom_end: str='col_chrom_end',
    # chromosomes=None,
    genome_ends: pd.Series=None, ## reference genome ends based on cytobands for e.g. 
    test: bool=False,
    ) -> pd.DataFrame:
    """Concat chromosomes by calculating global start and end positions.

    Args:
        data (pd.DataFrame): cytobands for multiple chromosomes
        col_start (str): column with start positions
        col_end (str): column with end positions
        col_chroms_start (str): column with start positions for chromosomes
        col_chroms_end (str): column with end positions for chromosomes
        col_chrom_start (str, optional): column with start positions for a chromosome. Defaults to 'col_chrom_start'.
        col_chrom_end (str, optional): column with end positions for a chromosome. Defaults to 'col_chrom_end'.
        genome_ends (pd.Series, optional): genome end positions. Defaults to None.

    Returns:
        pd.DataFrame: concatenated positions of the chromosomes
    """
    data=_sort_chroms(
        data,
        col_start,
        chromosomes=None,
    )
    ## end positions in the order along genome (contatenated chroms)
    if genome_ends is None:
        genome_ends=data.groupby('chromosome',sort=False,observed=False)[col_end].max().cumsum()
        
    ### .. of previous chromosome
    _genome_ends=genome_ends.shift(fill_value=0).to_dict()

    if test:
        print(data.groupby('chromosome',sort=False,observed=False)[col_end].max())
        print(_genome_ends)

    df1=(data
        .assign(
            **{
                'chrom i': lambda df: df.groupby('chromosome',sort=False,observed=False).ngroup(), 
                col_chrom_start: lambda df: df['chromosome'].map(_genome_ends).astype(int)+1,
                col_chrom_end: lambda df: df['chromosome'].map(genome_ends),        
            }
        )
        .pipe(lambda df: _rescale_to_chroms(
             df,
             col_start=col_start,col_end=col_end,
             col_chrom_start=col_chrom_start,
             col_chroms_start=col_chroms_start,col_chroms_end=col_chroms_end,
       ))
       )
    return df1

def _get_ax(
    ax: plt.Axes,
    arc: bool,
    **kws_subplots,
    ) -> plt.Axes:
    """Get subplot object

    Args:
        ax (plt.Axes): subplot
        arc (bool): arc/polar mode.

    Returns:
        plt.Axes: subplot
    """
    if ax is None:
        _,ax=plt.subplots(
        subplot_kw=dict(projection='polar' if arc else  'rectilinear'), 
        **kws_subplots,
        )
    return ax

def _set_span_polar(
    ax: plt.Axes,
    span_type: str,
    start: int,
    end: int,
    intervals: int=5,
    **kws,
    ):
    """Set span polar

    Args:
        ax (plt.Axes): subplot
        span_type (str): span type
        start (int): start position
        end (int): end position
        intervals (int, optional): number of intervals. Defaults to 5.
    """
    intervals=_to_polar_intrapolate(
        start=start,
        end=end,
        intervals=intervals, ## parameterise
        )
    for xrange in np.column_stack([intervals[:-1], intervals[1:]]):
        getattr(ax,f"ax{span_type}span")(
            *xrange,
            **kws
            )

def plot_chroms(
    data: pd.DataFrame,
    arc=True,
    chromosomes: list=None,
    col_start='start',
    col_end='end',
    col_arm='arm',
    span_color: str ='#dcdcdc',
    span_color_alpha_scale: float =1,
    pi_span: float=1,
    pi_start: int=0,
    pi_end: int=None,
    show_labels: bool=True,
    show_vline: bool=True,
    label_y: str=None,
    test: bool=False,
    ax: plt.Axes=None,
    figsize: list=None,
    out_data: bool=False,
    **kws_plot_arm,    
    ):
    """Plot chromosomes joined.

    Args:
        data (pd.DataFrame): cytonbands
        arc (bool, optional): arc/polar mode. Defaults to True.
        chromosomes (list, optional): chromosomes. Defaults to None.
        col_start (str, optional): column with start position. Defaults to 'start'.
        col_end (str, optional): column with end position. Defaults to 'end'.
        col_arm (str, optional): column with chromosome arm names. Defaults to 'arm'.
        span_color (str, optional): span color. Defaults to 'whitesmoke'.
        span_color_alpha_scale (float, optional): span color transparency scale. Defaults to 1.
        pi_span (float, optional): pi span. Defaults to 1.
        pi_start (int, optional): pi start angle. Defaults to 0.
        pi_end (int, optional): pi end angle. Defaults to None.
        show_labels (bool, optional): show labels. Defaults to True.
        show_vline (bool, optional): show vertical line. Defaults to True.
        label_y (str, optional): label y. Defaults to None.
        test (bool, optional): test-mode. Defaults to False.
        ax (plt.Axes, optional): subplot. Defaults to None.
        figsize (list, optional): figure size. Defaults to None.
        out_data (bool, optional): output data. Defaults to False.
    """
    ## subplot
    ax=_get_ax(ax=ax,arc=arc,figsize=figsize)
    
    if not 'kws_pre_xys' in kws_plot_arm:
        kws_plot_arm['kws_pre_xys']={}
    if not 'range2' in kws_plot_arm['kws_pre_xys']:
        if ax.name=='polar':
            assert pi_span>0 and pi_span<=2, pi_span
            kws_plot_arm['kws_pre_xys']['range2']=_get_pi_range(pi_span=pi_span,pi_start=pi_start,pi_end=pi_end)
    df1=_concat_chroms(
        data,
        col_start=col_start,
        col_end=col_end,
        col_chrom_start='genome chrom start',
        col_chrom_end='genome chrom end',
        col_chroms_start='genome start',
        col_chroms_end='genome end',
        test=test,
        )
    
    start,end=df1.agg({'genome start':'min','genome end':'max'}).tolist()
    ## chromosomes
    _=(df1
       .groupby('chromosome',sort=False,observed=False)
       .apply(lambda df: plot_chrom(
            data=df,
            col_start='genome start',
            col_end='genome end',
            col_arm=col_arm,
            solid_capstyle='butt' if df1['chromosome'].nunique()>1 else 'round',
            **_to_polar_chrom(
                range1_local=[df['genome start'].min(),df['genome end'].max()],
                range1_global=[start,end],
                kws_plot_arm=kws_plot_arm.copy(),
                ax=ax,
            ),
            test=test,
            ax=ax
        ))
      )

    ## vspans
    _xlim=df1.agg({'genome start':'min','genome end':'max'}).tolist()
    ax.set(xlim=_xlim if not ax.name=='polar' else rescale(_xlim,range2=kws_plot_arm['kws_pre_xys']['range2']))

    df2=df1.groupby('chromosome',sort=False,observed=False).agg({'genome start':'min','genome end':'max','chrom i':'min'}).reset_index()
    if ax.name=='polar':
        df_=df2.apply(lambda x: rescale([x['genome start'],x['genome end']],range1=[start,end],range2=kws_plot_arm['kws_pre_xys']['range2'],),axis=1).apply(pd.Series)
        df_.columns=['genome start theta','genome end theta']
        df2=df2.join(df_)
        if show_vline and (kws_plot_arm['kws_pre_xys']['range2'][1]-kws_plot_arm['kws_pre_xys']['range2'][0])%(2*np.pi) != 0:
            ## vline
            ax.axvline(x=kws_plot_arm['kws_pre_xys']['range2'][0],color='k')
            ax.axvline(x=kws_plot_arm['kws_pre_xys']['range2'][1],color='k')
    if ax.name!='polar':
        _=(df2
            .apply(lambda x: ax.axvspan(
                *[x["genome start"],x["genome end"]],
                color=span_color,
                alpha=span_color_alpha_scale*(x['chrom i']%2),
                zorder=-1,
                ),
            axis=1)
        )    
    else:
        _=(df2
            .apply(lambda x: _set_span_polar(
                ax=ax,
                span_type='v',
                start=x["genome start theta"],
                end=x["genome end theta"],
                color=span_color,
                alpha=span_color_alpha_scale*(x['chrom i']%2),
                zorder=-1,
            ),
            axis=1)
        )    
    
    if show_labels:
        if label_y is None:
            ## infer label_y 
            if 'y' in kws_plot_arm:
                label_y=kws_plot_arm['y']
            else:
                if ax.name=='polar':
                    label_y=0.1*1.5
                else:
                    label_y=0.1*0.8
        df2.apply(lambda x: ax.text(
            x=np.mean([x[f"genome start{' theta' if ax.name=='polar' else ''}"],x[f"genome end{' theta' if ax.name=='polar' else ''}"]]),
            y=label_y,
            s=x['chromosome'] if isinstance(x['chromosome'],(int,str)) else f"{x['chromosome']:.0f}",
            ha='center',
            va='center' if ax.name=='polar' else 'bottom',
        ),axis=1)
    if out_data:
        return ax,df2
    else:
        return ax
    
def _add_ax(
    off: float,
    va: str,
    offy: float=None,
    arc: bool=None,
    fig: plt.Figure=None,
    rect: list=None,
    ax_with: plt.Axes=None,
    zorder: int=0,
    # test: bool=False,
    ) -> plt.Axes:
    """Create the subplot for the chromosomes.


    Args:
        off (float): offset scale
        va (str): vertical alignment
        offy (float, optional): offset y. Defaults to None.
        arc (bool, optional): arc/polar mode. Defaults to None.
        fig (plt.Figure, optional): figure. Defaults to None.
        rect (list, optional): rectangle positions. Defaults to None.
        ax_with (plt.Axes, optional): subplot to relate with. Defaults to None.
        zorder (int, optional): z-order. Defaults to 0.

    Returns:
        plt.Axes: subplot
    """
    assert not (ax_with is None and arc is None)
    if fig is None:
        fig=plt.gcf()    
    if not ax_with is None:
        rect=ax_with.get_position().bounds
        if arc is None:
            arc=ax_with.name=='polar'
    if offy is None:
        offy=off
    if not rect is None:
        if va=='center':
            rect=[ 
                rect[0]+(off*-0.5),
                rect[1]+(offy*-0.5),
                rect[2]+off,
                rect[3]+off,
                ]
        elif va=='center bottom':
            rect=[
                rect[0],
                rect[1]+offy,
                rect[2]+off,
                rect[3]+off,
                ]
        elif va=='bottom':
            rect=[
                rect[0],
                rect[1]+offy,
                rect[2],
                rect[3]+off,
                ]
        else:
            raise ValueError(va)
    else:
        ## fail-safe inference
        if arc:
            ## experimental
            if offy==0:
                rect=[
                    -(off*0.5),
                    -(off*0.5),
                    1+off,
                    1+off,
                ] #(left, bottom, width, height)
            else:
                if offy is None:
                    offy=off*0.5
                rect=[-1*off,
                      (1-offy),
                      1+(2*off),
                      1+(2*off)]
        else:
            rect=[0,1,1,1*(off+0.3)]
    # if test:
    logging.info(f"rect={rect}")
    ax=fig.add_axes(
        rect=rect,#(left, bottom, width, height),
        zorder=zorder,
        polar=arc,
        )
    return ax

def annot_chroms(
    data: pd.DataFrame,
    chromosomes: list,
    ax_chrom: plt.Axes=None,
    chrom_y: float=0,
    kws_add_ax: dict={},
    test: bool=False,
    **kws_plot,
    ) -> plt.Axes:
    """Add a subplot with the chromosome.


    Args:
        data (pd.DataFrame): table with cytobands
        chromosomes (list): chromosomes
        ax_chrom (plt.Axes, optional): subplot with chromosome plot. Defaults to None.
        chrom_y (float, optional): chromosome y-position. Defaults to 0.
        kws_add_ax (dict, optional): keyword parameters provided to `_add_ax`. Defaults to {}.
        test (bool, optional): test mode. Defaults to False.

    Returns:
        plt.Axes: subplot
    """
    ## chromosomes
    if ax_chrom is None:            
        ax_chrom=_add_ax(
            # fig,
            # arc=arc,
            # scale=scale,
            # rect=rect,
            # offy=offy,
            **kws_add_ax,
            )
    
    ax=plot_chroms(
        data=data,
        chromosomes=chromosomes,
        show_labels=True,
        test=test,
        y=chrom_y,
        label_y=.05,
        ax=ax_chrom,
        # out_data=True,
        show_vline=False,
        **kws_plot,
        )
    if not isinstance(ax,tuple):
        _=ax.set(ylim=[-1,0.1])
    else:
        _=ax[0].set(ylim=[-1,0.1])
    # ax.ticklabel_format(style='plain')
    return ax