from scripts.serve_prototype import build_run, interpret_prompt

def test_prompt_interpretation_is_explicit():
    assert interpret_prompt("make education available to more people")[0] == "education"

def test_unknown_prompt_is_rejected_instead_of_inventing_a_mechanism():
    try:
        build_run({"prompt":"invent an entirely new civilization mechanism","people":50,"years":2,"seed":1})
    except ValueError as exc:
        assert "could not map" in str(exc)
    else:
        raise AssertionError("unknown scenario was silently executed")

def test_scenario_run_is_deterministic_and_has_trajectory():
    payload={"prompt":"expand access to education","people":80,"years":4,"seed":7}
    left=build_run(payload)
    right=build_run(payload)
    assert left["fingerprint"] == right["fingerprint"]
    assert len(left["trajectory"]) == 5
    assert 0 < sum(left["exposure"].values()) <= 80

def test_prompt_scope_can_be_natural_language():
    out=build_run({"prompt":"give everyone access to healthcare","people":60,"years":2,"seed":3})
    assert out["exposure"].get("adopted",0) > 0
