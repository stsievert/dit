"""
Tests for dit.distconst.
"""

from __future__ import division

from nose.tools import assert_equal, assert_false, assert_raises, assert_true

import numpy as np
import numpy.testing as npt

from dit.exceptions import ditException, InvalidOutcome
import dit

def test_mixture_distribution_weights():
    d = dit.Distribution(['A', 'B'], [0.5, 0.5])
    d2 = dit.Distribution(['A', 'B'], [1, 0])

    assert_raises(ditException, dit.mixture_distribution, [d, d2], [1])
    assert_raises(ditException, dit.mixture_distribution2, [d, d2], [1])

def test_mixture_distribution():
    d = dit.Distribution(['A', 'B'], [0.5, 0.5])
    d2 = dit.Distribution(['A', 'B'], [1, 0])
    pmf = np.array([0.75, 0.25])

    d3 = dit.mixture_distribution([d, d2], [0.5, 0.5])
    npt.assert_allclose(pmf, d3.pmf)

def test_mixture_distribution_log():
    d = dit.Distribution(['A', 'B'], [0.5, 0.5])
    d2 = dit.Distribution(['A', 'B'], [1, 0])
    d.set_base(2)
    d2.set_base(2)
    weights = np.log2(np.array([0.5, 0.5]))
    pmf = np.log2(np.array([0.75, 0.25]))

    d3 = dit.mixture_distribution([d, d2], weights)
    npt.assert_allclose(pmf, d3.pmf)

def test_mixture_distribution2():
    # Test when pmfs are different lengths.
    d = dit.Distribution(['A', 'B'], [0.5, 0.5])
    d2 = dit.Distribution(['A', 'B'], [1, 0], sort=True, trim=True)

    # Fails when it checks that all pmfs have the same length.
    assert_raises(ValueError, dit.mixture_distribution2, [d, d2], [0.5, 0.5])

def test_mixture_distribution3():
    # Sample spaces are compatible.
    # But pmfs have a different order.
    d = dit.Distribution(['A', 'B'], [0.5, 0.5])
    d2 = dit.Distribution(['B', 'A'], [1, 0], sort=False, trim=False, sparse=False)
    pmf = np.array([0.25, 0.75])

    d3 = dit.mixture_distribution([d, d2], [0.5, 0.5])
    assert_true(np.allclose(pmf, d3.pmf))
    d3 = dit.mixture_distribution2([d, d2], [0.5, 0.5])
    assert_false(np.allclose(pmf, d3.pmf))

def test_mixture_distribution4():
    # Sample spaces are compatible.
    # But pmfs have a different lengths and orders.
    d = dit.Distribution(['A', 'B'], [0.5, 0.5])
    d2 = dit.Distribution(['B', 'A'], [1, 0], sort=False, trim=False, sparse=True)
    d2.make_sparse(trim=True)
    pmf = np.array([0.25, 0.75])

    d3 = dit.mixture_distribution([d, d2], [0.5, 0.5])
    assert_true(np.allclose(pmf, d3.pmf))
    assert_raises(ValueError, dit.mixture_distribution2, [d, d2], [0.5, 0.5])

def test_mixture_distribution5():
    # Incompatible sample spaces.
    d1 = dit.Distribution(['A', 'B'], [0.5, 0.5])
    d2 = dit.Distribution(['B', 'C'], [0.5, 0.5])
    d3 = dit.mixture_distribution([d1, d2], [0.5, 0.5], merge=True)
    pmf = np.array([0.25, 0.5, 0.25])
    assert_true(np.allclose(pmf, d3.pmf))

def test_random_scalar_distribution():
    # Test with no alpha and only an integer
    pmf = np.array([0.297492727853, 0.702444212002, 6.30601451072e-05])
    for prng in [None, dit.math.prng]:
        dit.math.prng.seed(1)
        d = dit.random_scalar_distribution(3, prng=prng)
        assert_equal(d.outcomes, (0, 1, 2))
        np.testing.assert_allclose(d.pmf, pmf)

    # Test with outcomes specified
    dit.math.prng.seed(1)
    d = dit.random_scalar_distribution([0, 1, 2])
    assert_equal(d.outcomes, (0, 1, 2))
    np.testing.assert_allclose(d.pmf, pmf)

    # Test with concentration parameters
    pmf = np.array([0.34228708, 0.52696865, 0.13074428])
    dit.math.prng.seed(1)
    d = dit.random_scalar_distribution(3, alpha=[1, 2, 1])
    assert_equal(d.outcomes, (0, 1, 2))
    np.testing.assert_allclose(d.pmf, pmf)
    assert_raises(ditException, dit.random_scalar_distribution, 3, alpha=[1])

def test_random_distribution():
    # Test with no alpha
    pmf = np.array([2.48224944e-01, 5.86112396e-01, 5.26167518e-05, 1.65610043e-01])
    outcomes = ((0, 0), (0, 1), (1, 0), (1, 1))
    for prng in [None, dit.math.prng]:
        dit.math.prng.seed(1)
        d = dit.random_distribution(2, 2, prng=prng)
        assert_equal(d.outcomes, outcomes)
        np.testing.assert_allclose(d.pmf, pmf)

    # Test with a single alphabet specified
    dit.math.prng.seed(1)
    d = dit.random_distribution(2, [[0, 1]])
    assert_equal(d.outcomes, outcomes)
    np.testing.assert_allclose(d.pmf, pmf)

    # Test with two alphabets specified
    dit.math.prng.seed(1)
    d = dit.random_distribution(2, [[0, 1], [0, 1]])
    assert_equal(d.outcomes, outcomes)
    np.testing.assert_allclose(d.pmf, pmf)

    # Test with invalid number of alphabets
    assert_raises(TypeError, dit.random_distribution, 3, [3, 2])
    assert_raises(TypeError, dit.random_distribution, 3, [3, 2, 3])

    # Test with concentration parameters
    pmf = np.array([0.15092872, 0.23236257, 0.05765063, 0.55905808])
    dit.math.prng.seed(1)
    d = dit.random_distribution(2, 2, alpha=[1, 2, 1, 3])
    assert_equal(d.outcomes, outcomes)
    np.testing.assert_allclose(d.pmf, pmf)
    assert_raises(ditException, dit.random_distribution, 2, 2, alpha=[1])

def test_simplex_grid1():
    # Test with tuple
    dists = np.asarray(list(dit.simplex_grid(2, 2, using=tuple)))
    dists_ = np.asarray([(0.0, 1.0), (0.25, 0.75), (0.5, 0.5),
                         (0.75, 0.25), (1.0, 0.0)])
    np.testing.assert_allclose(dists, dists_)

def test_simplex_grid2():
    # Test with ScalarDistribution
    dists = np.asarray([d.pmf for d in dit.simplex_grid(2, 2)])
    dists_ = np.asarray([(0.0, 1.0), (0.25, 0.75), (0.5, 0.5),
                         (0.75, 0.25), (1.0, 0.0)])
    np.testing.assert_allclose(dists, dists_)

def test_simplex_grid3():
    # Test with Distribution
    d = dit.random_distribution(1, 2)
    dists = np.asarray([x.pmf for x in dit.simplex_grid(2, 2, using=d)])
    dists_ = np.asarray([(0.0, 1.0), (0.25, 0.75), (0.5, 0.5),
                         (0.75, 0.25), (1.0, 0.0)])
    np.testing.assert_allclose(dists, dists_)

def test_simplex_grid4():
    # Test with Distribution but with wrong length specified.
    d = dit.random_distribution(2, 2)
    g = dit.simplex_grid(5, 2, using=d)
    np.testing.assert_raises(Exception, next, g)

def test_simplex_grid5():
    # Test with ScalarDistribution with inplace=True
    # All final dists should be the same.
    dists = np.asarray([d.pmf for d in dit.simplex_grid(2, 2, inplace=True)])
    dists_ = np.asarray([(1.0, 0.0)]*5)
    np.testing.assert_allclose(dists, dists_)

# These can be simple smoke test, since the random* tests hit all the branches.

def test_uniform_scalar_distribution():
    pmf = np.array([1/3] * 3)
    outcomes = (0, 1, 2)
    dit.math.prng.seed(1)
    d = dit.uniform_scalar_distribution(len(outcomes))
    assert_equal(d.outcomes, outcomes)
    np.testing.assert_allclose(d.pmf, pmf)

    dit.math.prng.seed(1)
    d = dit.uniform_scalar_distribution(outcomes)
    assert_equal(d.outcomes, outcomes)
    np.testing.assert_allclose(d.pmf, pmf)


def test_uniform_distribution():
    pmf = np.array([1/4] * 4)
    dit.math.prng.seed(1)
    d = dit.uniform_distribution(2, 2)
    assert_equal(d.outcomes, ((0, 0), (0, 1), (1, 0), (1, 1)))
    np.testing.assert_allclose(d.pmf, pmf)

def test_booleanfunctions1():
    # Smoke test
    d = dit.Distribution(['00', '01', '10', '11'], [1/4]*4)
    bf = dit.BooleanFunctions(d)
    d = dit.insert_frv(d, bf.xor([0,1]))
    d = dit.insert_frv(d, bf.xor([1,2]))
    assert_equal(d.outcomes, ('0000', '0110', '1011', '1101'))

def test_booleanfunctions2():
    # Smoke test
    d = dit.Distribution([(0,0), (0,1), (1,0), (1,1)], [1/4]*4)
    bf = dit.BooleanFunctions(d)
    d = dit.insert_frv(d, bf.xor([0,1]))
    d = dit.insert_frv(d, bf.xor([1,2]))
    assert_equal(d.outcomes, ((0,0,0,0), (0,1,1,0), (1,0,1,1), (1,1,0,1)))

def test_booleanfunctions3():
    # Smoke test
    outcomes = ['000', '001', '010', '011', '100', '101', '110', '111']
    pmf = [1/8] * 8
    d = dit.Distribution(outcomes, pmf)
    bf = dit.BooleanFunctions(d)
    d = dit.insert_frv(d, bf.from_hexes('27'))
    outcomes = ('0000', '0010', '0101', '0110', '1000', '1010', '1100', '1111')
    assert_equal(d.outcomes, outcomes)

def test_booleanfunctions4():
    # Smoke test
    outcomes = ['000', '001', '010', '011', '100', '101', '110', '111']
    outcomes = [tuple(map(int, o)) for o in outcomes]
    pmf = [1/8] * 8
    d = dit.Distribution(outcomes, pmf)
    bf = dit.BooleanFunctions(d)
    d = dit.insert_frv(d, bf.from_hexes('27'))
    outcomes = ('0000', '0010', '0101', '0110', '1000', '1010', '1100', '1111')
    outcomes = tuple(tuple(map(int, o)) for o in outcomes)
    assert_equal(d.outcomes, outcomes)

def test_insert_frv1():
    # Test multiple insertion.
    d = dit.uniform_distribution(2, 2)
    def xor(outcome):
        o = int(outcome[0] != outcome[1])
        # Here we are returning 2 random variables
        return (o,o)
    # We are also inserting two times simultaneously.
    d2 = dit.insert_frv(d, [xor, xor])
    outcomes = (
        (0, 0, 0, 0, 0, 0),
        (0, 1, 1, 1, 1, 1),
        (1, 0, 1, 1, 1, 1),
        (1, 1, 0, 0, 0, 0)
    )
    assert_equal(d2.outcomes, outcomes)

def test_insert_frv2():
    # Test multiple insertion.
    d = dit.uniform_distribution(2, 2)
    d = dit.modify_outcomes(d, lambda x: ''.join(map(str, x)))
    def xor(outcome):
        o = str(int(outcome[0] != outcome[1]))
        # Here we are returning 2 random variables
        return o*2
    # We are also inserting two times simultaneously.
    d2 = dit.insert_frv(d, [xor, xor])
    outcomes = ('000000', '011111', '101111', '110000')
    assert_equal(d2.outcomes, outcomes)
