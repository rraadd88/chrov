from pathlib import Path
import logging


def setup():
    from chrov.utils import get_src_path

    get_src_path()


def plot(
    gene_id: str,
    outd: str,
    levels_path: str,  # =None,
    species: str = "homo sapiens",
    ensembl_release: int = 112,
    ## ints
    height_ratios: list = [3, 1],
    show_title: bool = False,
    figsize: list = [2, 1],
    cmap: str = "Reds_r",
    log_level="WARNING",
    force: bool = False,
):
    """
    Plots the level-wise interaction heatmaps.

    Args:
        gene_id: str: Ensembl gene id,
        outd: str: Output directory path,
        levels_path: str: level-wise data paths provided through a yaml file,
        species: str='homo sapiens': species name,
        ensembl_release: int=112: Ensembl release,
        height_ratios: list=[3,1]: ratio of the heatmap and the chrov plot,
        show_title: bool=False: show title of the level,
        figsize: list=[2,1]: figure size,
        cmap: str='Reds_r': colormap,
        force: bool = False: Over-write,

    Examples:

        CLI:
            chrov plot ENSG00000187634 examples/outputs/ints_levels examples/inputs/ints.yaml

        Format of the level-wise data:

            levels.yaml (levels_path)
            ├── genome.pqt
            ├── ..
            └── protein.pqt

            where, pqt is Apache parquete format (ideal for large data).
    """
    logging.basicConfig(level=log_level)
    ## inputs
    # assert Path(outd).is_dir(),outd
    assert Path(levels_path).exists(), levels_path

    from chrov.fig.mat import Plot_levels

    plot_levels = Plot_levels(
        gene_id=gene_id,
        species=species,
        ensembl_release=ensembl_release,
        # force=force,
    )
    # from roux.lib.io import read_tables
    # dfs_mats=read_tables(levels_path)
    from roux.lib.io import read_table

    dfs_mat = {
        Path(p).with_suffix("").stem: read_table(str(p))
        for p in list(Path(levels_path).with_suffix("").glob("*.pqt"))
    }
    if "examples/" in levels_path:
        logging.warning("this is example data ..")
    # if levels is not None:
    # assert levels is not None, "proide out. dir."
    (
        plot_levels.plot(
            dfs_mat,
            figsize=[3, 1.5],
            height_ratios=[3, 1],
            cmap=cmap,
            outd=outd,
            # **kws
        )
    )
    # from roux.lib.sys import read_ps
    # read_ps(outd)
    from roux.lib.sys import tree

    print(
        "Outputs: ",
        tree(
            folder_path=outd,
            tree_depth=1,
            log=False,
        ),
    )


import argh

parser = argh.ArghParser()
parser.add_commands(
    [
        plot,
        # gui,
        setup,
    ]
)

if __name__ == "__main__":
    # from datetime import datetime
    # _start_time = datetime.now()

    parser.dispatch()

    # logging.info(f"Time taken: {datetime.now()-_start_time}")
