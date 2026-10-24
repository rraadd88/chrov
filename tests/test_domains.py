"""Offline tests of the protein-to-genome coordinate mapping in `chrov.domains`."""

import pandas as pd
import pytest

import chrov.domains as domains


class _Transcript:
    """Minimal stand-in for `pyensembl.Transcript`."""

    def __init__(self, strand, cds_ranges, protein_sequence, coding_sequence):
        self.biotype = "protein_coding"
        self.contig = "1"
        self.strand = strand
        self.coding_sequence_position_ranges = cds_ranges
        self.protein_sequence = protein_sequence
        self.coding_sequence = coding_sequence
        self.complete = True
        self.contains_start_codon = True
        self.contains_stop_codon = True


class _Annots:
    def __init__(self, transcripts):
        self.transcripts = transcripts

    def transcript_by_protein_id(self, protein_id):
        return self.transcripts[protein_id]


## protein 'MKV' (9 nt) + stop codon (3 nt), CDS split across two exons
_CODING_SEQUENCE = "ATGAAAGTGTAA"
_TRANSCRIPTS = {
    # with stop codon in the ranges (pyensembl>=2.7)
    "P+stop": _Transcript("+", [(100, 104), (200, 206)], "MKV", _CODING_SEQUENCE),
    # without stop codon in the ranges (pyensembl<2.7)
    "P+": _Transcript("+", [(100, 104), (200, 203)], "MKV", _CODING_SEQUENCE),
    "P-stop": _Transcript("-", [(100, 106), (200, 204)], "MKV", _CODING_SEQUENCE),
    "P-": _Transcript("-", [(103, 106), (200, 204)], "MKV", _CODING_SEQUENCE),
}


@pytest.mark.parametrize("protein_id", ["P+stop", "P+"])
def test_get_protein_cds_coords_plus_strand(protein_id):
    df = domains.get_protein_cds_coords(
        annots=_Annots(_TRANSCRIPTS), protein_id=protein_id
    )
    assert df["pos"].tolist() == [100, 101, 102, 103, 104, 200, 201, 202, 203]
    assert "".join(df["base"]) == "ATGAAAGTG"
    assert df["aa pos"].tolist() == [1, 1, 1, 2, 2, 2, 3, 3, 3]


@pytest.mark.parametrize("protein_id", ["P-stop", "P-"])
def test_get_protein_cds_coords_minus_strand(protein_id):
    df = domains.get_protein_cds_coords(
        annots=_Annots(_TRANSCRIPTS), protein_id=protein_id
    )
    assert df["pos"].tolist() == [204, 203, 202, 201, 200, 106, 105, 104, 103]
    assert df["aa pos"].tolist() == [1, 1, 1, 2, 2, 2, 3, 3, 3]


def test_get_protein_cds_coords_incompatible_length():
    annots = _Annots({"P": _Transcript("+", [(100, 110)], "MKV", _CODING_SEQUENCE)})
    with pytest.raises(AssertionError):
        domains.get_protein_cds_coords(annots=annots, protein_id="P")


@pytest.mark.parametrize(
    "strand,pstart,expected",
    [("+", True, 1), ("+", False, 3), ("-", True, 3), ("-", False, 1)],
)
def test_get_p_bounds(strand, pstart, expected):
    assert domains.get_p_bounds(pos=[1, 2, 3], pstart=pstart, strand=strand) == expected


def test_get_p_bounds_unknown_strand():
    with pytest.raises(ValueError):
        domains.get_p_bounds(pos=[1, 2, 3], pstart=True, strand=".")


@pytest.mark.parametrize(
    "protein_id,expected",
    [
        # residues 2-3 ('KV') span the exon junction
        ("P+stop", (103, 203)),
        ("P-stop", (103, 201)),
    ],
)
def test_to_gpos(monkeypatch, protein_id, expected):
    monkeypatch.setattr(domains, "get_annots", lambda **kws: _Annots(_TRANSCRIPTS))
    df = pd.DataFrame(
        {
            "t.id": ["T"],
            "p.id": [protein_id],
            "d.id": ["D"],
            "d.start": [2],
            "d.end": [3],
        }
    )
    df1 = domains.to_gpos(df, ensembl_release=112, species="homo sapiens")
    ## only genome coordinates are returned
    assert len(df1) == 1
    assert (df1.loc[0, "d.start"], df1.loc[0, "d.end"]) == expected


def test_to_gpos_missing_column():
    df = pd.DataFrame({"t.id": ["T"], "p.id": ["P"], "d.id": ["D"], "d.start": [2]})
    assert domains.to_gpos(df, ensembl_release=112, species="homo sapiens") is None
