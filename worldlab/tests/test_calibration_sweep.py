from worldlab.calibration.sweep import CalibrationSweep

def test_sweep_finds_best_explicit_parameters():
    sweep=CalibrationSweep({"employment":.70,"health":.80})
    result=sweep.run({"employment_bias":[-.1,0,.1],"health_bias":[-.1,0,.1]},lambda p:{"employment":.70+p["employment_bias"],"health":.80+p["health_bias"]})
    assert result.best.parameters=={"employment_bias":0.0,"health_bias":0.0}
    assert result.best.report.passed
    assert len(result.trials)==9

def test_sweep_does_not_hide_unobserved_metrics():
    sweep=CalibrationSweep({"employment":.7})
    result=sweep.run({"bias":[.0]},lambda p:{"employment":.9,"health":.2})
    assert result.best.simulated["health"]==.2
