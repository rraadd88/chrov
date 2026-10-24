"""Tests of the packaging and of the package-level paths."""

import subprocess
import zipfile
from pathlib import Path


def test_wheel_contents(tmp_path):
    repo_dir_path = Path(__file__).resolve().parents[1]
    subprocess.run(
        f"uv build --wheel --out-dir {tmp_path}",
        shell=True,
        check=True,
        cwd=repo_dir_path,
    )
    names = zipfile.ZipFile(next(tmp_path.glob("*.whl"))).namelist()
    for name in [
        "chrov/viz/chrom.py",
        "chrov/fig/mat.py",
        "chrov/plot/mat.py",
        "chrov/inputs/cytobands.tsv",
    ]:
        assert name in names, name


def test_cache_dir_independent_of_cwd(monkeypatch, tmp_path):
    from chrov.utils import get_cache_dir, get_pkg_name

    monkeypatch.chdir(tmp_path)
    assert get_pkg_name() == "chrov"
    assert Path(get_cache_dir()).name == "chrov"
