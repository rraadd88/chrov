from testbook import testbook
    
import os
from os import makedirs
from os.path import exists
assert len(set(['modules','examples','tests']) - set(os.listdir('.')))==0
assert exists('./modules/inputs')
makedirs('./examples/outputs',exist_ok=True)
    
@testbook('examples/viz_annot.ipynb', execute=True)
def test_chrov_viz_annot(tb):
    pass # execute only because tests are present in the notebook itself
    return

@testbook('examples/viz_chrom.ipynb', execute=True)
def test_chrov_viz_chrom(tb):
    pass # execute only because tests are present in the notebook itself
    return

@testbook('examples/viz_chrom_custom.ipynb', execute=True)
def test_chrov_viz_chrom_custom(tb):
    pass # execute only because tests are present in the notebook itself
    return

@testbook('examples/viz_figure_custom.ipynb', execute=True)
def test_chrov_viz_figure_custom(tb):
    pass # execute only because tests are present in the notebook itself
    return

@testbook('examples/viz_figure_stem.ipynb', execute=True)
def test_chrov_viz_figure_stem(tb):
    pass # execute only because tests are present in the notebook itself
    return

@testbook('examples/viz_ranges.ipynb', execute=True)
def test_chrov_viz_ranges(tb):
    pass # execute only because tests are present in the notebook itself
    return

@testbook('examples/viz_tests.ipynb', execute=True)
def test_chrov_viz_tests(tb):
    pass # execute only because tests are present in the notebook itself
    return
