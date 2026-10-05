from worldlab.core.evidence import EvidenceRecord, weighted_value

def test_evidence_preserves_provenance_and_uncertainty():
    record = EvidenceRecord("obs-1", "https://example.org/dataset/1", "observation", variable="temperature", value=31.5, unit="degC", uncertainty=0.4, location_id=7, confidence=0.9)
    record.validate()
    assert record.uncertainty == 0.4

def test_evidence_rejects_invalid_confidence():
    record = EvidenceRecord("bad", "https://example.org", "archive", confidence=1.2)
    try: record.validate()
    except ValueError: pass
    else: raise AssertionError("invalid confidence must fail validation")

def test_weighted_value_keeps_source_disagreement_available():
    records = [EvidenceRecord("a", "https://a", "observation", variable="x", value=10, confidence=0.8), EvidenceRecord("b", "https://b", "model", variable="x", value=14, confidence=0.2)]
    assert weighted_value(records) == 10.8
    assert records[1].source_type == "model"
