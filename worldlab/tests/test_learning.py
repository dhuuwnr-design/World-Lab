from worldlab.social.learning import LearningState, update_estimate


def test_learning_reduces_prediction_error():
    estimate = 0.0
    for _ in range(5):
        estimate = update_estimate(estimate, 1.0, 0.5)
    assert estimate > 0.9


def test_learning_records_direction_of_surprise():
    state = LearningState()
    errors = state.learn_from_outcome({"price": 100.0}, {"price": 130.0}, 0.5)
    assert errors["price"] == 30.0
    assert state.prediction_errors["price"] == 15.0
    assert state.experience_count == 1
