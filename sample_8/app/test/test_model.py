"""
Test module for Model.
"""

import pytest

from app.model import validate_str, Step, Job

# test constants.
TEST_STEP_ID1 = 'test_step_id1'
TEST_STEP_ID2 = 'test_step_id2'
TEST_STEP_ID3 = 'test_step_id3'
TEST_STEP_ID4 = 'test_step_id4'
TEST_PRECEDENCE_10 = 10
TEST_PRECEDENCE_50 = 50
TEST_PRECEDENCE_100 = 100


def test_validate_str():

    # empty string 1
    with pytest.raises(ValueError):
        validate_str(value=None)

    # empty string 2
    with pytest.raises(ValueError):
        validate_str(value='')

    # whitespace string
    with pytest.raises(ValueError):
        validate_str(value='  ')

    # string with newline
    with pytest.raises(ValueError):
        validate_str(value=' \n ')

    valid_test_string = 'valid_test_string'
    assert valid_test_string == validate_str(value=valid_test_string)


def test_step_invalid():

    # step with empty id
    with pytest.raises(ValueError):
        Step(**{'dependencies': [], 'precedence': 100})

    # step with empty id2
    with pytest.raises(ValueError):
        Step(**{'step': '', 'dependencies': [], 'precedence': 100})

    # step with no precedence
    with pytest.raises(ValueError):
        Step(**{'step': 'TEST_STEP_ID1', 'dependencies': []})

    # step with negative precedence
    with pytest.raises(ValueError):
        Step(**{'step': '', 'dependencies': [], 'precedence': -10})

    # step with invalid dependencies 1
    with pytest.raises(ValueError):
        Step(**{'step': 'TEST_STEP_ID1', 'dependencies': ['  '], 'precedence': 100})

    # step with invalid dependencies 2
    with pytest.raises(ValueError):
        Step(**{'step': 'TEST_STEP_ID1', 'dependencies': ['a\nb'], 'precedence': 100})


def test_step_valid():

    # valid - regular step case
    test_step = Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': TEST_PRECEDENCE_100})
    assert TEST_STEP_ID1 == test_step.id
    assert [] == test_step.dependencies
    assert TEST_PRECEDENCE_100 == test_step.precedence

    # valid - whitespace around step id.
    test_step = Step(**{'step': f' {TEST_STEP_ID1} ', 'dependencies': [], 'precedence': TEST_PRECEDENCE_100})
    assert TEST_STEP_ID1 == test_step.id
    assert [] == test_step.dependencies
    assert TEST_PRECEDENCE_100 == test_step.precedence

    # valid - regular step with dependency case
    test_step = Step(**{'step': TEST_STEP_ID1, 'dependencies': [TEST_STEP_ID2], 'precedence': TEST_PRECEDENCE_100})
    assert TEST_STEP_ID1 == test_step.id
    assert [TEST_STEP_ID2] == test_step.dependencies
    assert TEST_PRECEDENCE_100 == test_step.precedence

    # valid - whitespace around dependency id.
    test_step = Step(**{'step': TEST_STEP_ID1, 'dependencies': [f' {TEST_STEP_ID2} '], 'precedence': TEST_PRECEDENCE_100})
    assert TEST_STEP_ID1 == test_step.id
    assert [TEST_STEP_ID2] == test_step.dependencies
    assert TEST_PRECEDENCE_100 == test_step.precedence


def test_step_comparison():

    test_precedence1 = 50
    test_precedence2 = 100

    test_step = Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': test_precedence1})
    test_step2 = Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': test_precedence1})
    assert test_step == test_step2

    # step comparison based on precedence.
    lower_order_step = Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': test_precedence1})
    higher_order_step = Step(**{'step': TEST_STEP_ID2, 'dependencies': [], 'precedence': test_precedence2})
    assert lower_order_step < higher_order_step

    # step comparison based on id.
    lower_order_step2 = Step(**{'step': TEST_STEP_ID2, 'dependencies': [], 'precedence': test_precedence1})
    higher_order_step2 = Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': test_precedence1})
    assert lower_order_step2 < higher_order_step2


def test_validate_step_uniqueness():

    # duplicate step ids error
    test_steps_duplicate = [
        Step(**{'step': 'TEST_STEP_ID1', 'dependencies': [], 'precedence': TEST_PRECEDENCE_100}),
        Step(**{'step': 'TEST_STEP_ID1', 'dependencies': [], 'precedence': TEST_PRECEDENCE_100})
    ]

    with pytest.raises(ValueError):
        Job.validate_step_uniqueness(steps=test_steps_duplicate)

    # valid -no duplicate step ids
    test_steps_valid = [
        Step(**{'step': 'TEST_STEP_ID1', 'dependencies': [], 'precedence': TEST_PRECEDENCE_100}),
        Step(**{'step': 'TEST_STEP_ID2', 'dependencies': [], 'precedence': TEST_PRECEDENCE_100})
    ]

    Job.validate_step_uniqueness(steps=test_steps_valid)


def test_validate_step_existence():

    # non-existent dependency id error
    test_step_invalid_dependency = [
        Step(**{'step': 'TEST_STEP_ID1', 'dependencies': [], 'precedence': TEST_PRECEDENCE_100}),
        Step(**{'step': 'TEST_STEP_ID2', 'dependencies': ['invalid_step_id'], 'precedence': TEST_PRECEDENCE_100})
    ]

    with pytest.raises(ValueError):
        Job.validate_step_existence(steps=test_step_invalid_dependency)

    # valid dependency - all exists.
    test_steps_valid = [
        Step(**{'step': 'TEST_STEP_ID1', 'dependencies': [], 'precedence': TEST_PRECEDENCE_100}),
        Step(**{'step': 'TEST_STEP_ID2', 'dependencies': ['TEST_STEP_ID1'], 'precedence': TEST_PRECEDENCE_100})
    ]

    Job.validate_step_existence(steps=test_steps_valid)


def test_validate_non_cyclic():

    # valid - no circular dependency.
    test_steps_nocycle = [
        Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': TEST_PRECEDENCE_50}),
        Step(**{'step': TEST_STEP_ID2, 'dependencies': [TEST_STEP_ID1], 'precedence': TEST_PRECEDENCE_100})
    ]

    Job.validate_non_cyclic(steps=test_steps_nocycle)

    # dependency - circular dependency input error.
    test_steps_cycle = [
        Step(**{'step': TEST_STEP_ID1, 'dependencies': [TEST_STEP_ID2], 'precedence': TEST_PRECEDENCE_50}),
        Step(**{'step': TEST_STEP_ID2, 'dependencies': [TEST_STEP_ID1], 'precedence': TEST_PRECEDENCE_100}),
    ]
    with pytest.raises(ValueError):
        Job.validate_non_cyclic(steps=test_steps_cycle)

    # dependency - circular dependency input error 2.
    test_steps_cycle = [
        Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': TEST_PRECEDENCE_50}),
        Step(**{'step': TEST_STEP_ID2, 'dependencies': [TEST_STEP_ID4], 'precedence': TEST_PRECEDENCE_100}),
        Step(**{'step': TEST_STEP_ID3, 'dependencies': [TEST_STEP_ID2], 'precedence': TEST_PRECEDENCE_100}),
        Step(**{'step': TEST_STEP_ID4, 'dependencies': [TEST_STEP_ID3], 'precedence': TEST_PRECEDENCE_100}),
    ]
    with pytest.raises(ValueError):
        Job.validate_non_cyclic(steps=test_steps_cycle)


def test_job():

    # no dependency - based on precedence.
    test_steps = [
        Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': TEST_PRECEDENCE_100}),
        Step(**{'step': TEST_STEP_ID2, 'dependencies': [], 'precedence': TEST_PRECEDENCE_50})
    ]

    assert [TEST_STEP_ID1, TEST_STEP_ID2] == Job(steps=test_steps).generate_schedule()

    # no dependency - based on step id.
    test_steps = [
        Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': TEST_PRECEDENCE_100}),
        Step(**{'step': TEST_STEP_ID2, 'dependencies': [], 'precedence': TEST_PRECEDENCE_100})
    ]
    assert [TEST_STEP_ID1, TEST_STEP_ID2] == Job(steps=test_steps).generate_schedule()

    # dependency - overrides precedence.
    test_steps = [
        Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': TEST_PRECEDENCE_50}),
        Step(**{'step': TEST_STEP_ID2, 'dependencies': [TEST_STEP_ID1], 'precedence': TEST_PRECEDENCE_100})
    ]
    assert [TEST_STEP_ID1, TEST_STEP_ID2] == Job(steps=test_steps).generate_schedule()

    # dependency - precedence enforced among dependents.
    test_steps = [
        Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': TEST_PRECEDENCE_50}),
        Step(**{'step': TEST_STEP_ID2, 'dependencies': [TEST_STEP_ID1], 'precedence': TEST_PRECEDENCE_10}),
        Step(**{'step': TEST_STEP_ID3, 'dependencies': [TEST_STEP_ID1], 'precedence': TEST_PRECEDENCE_100})
    ]
    assert [TEST_STEP_ID1, TEST_STEP_ID3, TEST_STEP_ID2] == Job(steps=test_steps).generate_schedule()

    # dependency - precedence tie among dependents.
    test_steps = [
        Step(**{'step': TEST_STEP_ID1, 'dependencies': [], 'precedence': TEST_PRECEDENCE_50}),
        Step(**{'step': TEST_STEP_ID2, 'dependencies': [TEST_STEP_ID1], 'precedence': TEST_PRECEDENCE_100}),
        Step(**{'step': TEST_STEP_ID3, 'dependencies': [TEST_STEP_ID1], 'precedence': TEST_PRECEDENCE_100})
    ]
    assert [TEST_STEP_ID1, TEST_STEP_ID2, TEST_STEP_ID3] == Job(steps=test_steps).generate_schedule()