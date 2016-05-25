import unittest

import numpy as np
import numpy.testing as np_test
from scipy.stats import gamma,expon

from pgmpy.factors import ContinuousFactor
from pgmpy.continuous.discretize import BaseDiscretizer
from pgmpy.continuous.discretize import RoundingDiscretizer
from pgmpy.continuous.discretize import UnbiasedDiscretizer


class TestBaseDiscretizer(unittest.TestCase):
    def setUp(self):
        self.normal_pdf = lambda x : np.exp(-x*x/2) / (np.sqrt(2*np.pi))
        gamma_rv = gamma(3)
        self.gamma_pdf = gamma_rv.pdf
        exp_rv = expon(7)
        self.exp_pdf = exp_rv.pdf

        self.normal_factor = ContinuousFactor(self.normal_pdf)
        self.gamma_factor = ContinuousFactor(self.gamma_pdf, lb=0)
        self.exp_factor = ContinuousFactor(self.exp_pdf, lb=0)

        self.normal_discretizer = BaseDiscretizer(self.normal_factor, -10, 10, 1)
        self.gamma_discretizer = BaseDiscretizer(self.gamma_factor, 0, 10, 1)
        self.exp_discretizer = BaseDiscretizer(self.exp_factor, 0, 5, 0.5)

    def test_base_init(self):
        self.assertEqual(self.normal_discretizer.factor, self.normal_factor)
        self.assertEqual(self.normal_discretizer.frm, -10)
        self.assertEqual(self.normal_discretizer.to, 10)
        self.assertEqual(self.normal_discretizer.step, 1)

        self.assertEqual(self.gamma_discretizer.factor, self.gamma_factor)
        self.assertEqual(self.gamma_discretizer.frm, 0)
        self.assertEqual(self.gamma_discretizer.to, 10)
        self.assertEqual(self.gamma_discretizer.step, 1)

        self.assertEqual(self.exp_discretizer.factor, self.exp_factor)
        self.assertEqual(self.exp_discretizer.frm, 0)
        self.assertEqual(self.exp_discretizer.to, 5)
        self.assertEqual(self.exp_discretizer.step, 0.5)

    def test_get_labels(self):
        o1 = ['x=-10', 'x=-9', 'x=-8', 'x=-7', 'x=-6', 'x=-5', 'x=-4', 'x=-3',
              'x=-2', 'x=-1', 'x=0', 'x=1', 'x=2', 'x=3', 'x=4', 'x=5', 'x=6',
              'x=7', 'x=8', 'x=9']
        o2 = ['x=0', 'x=1', 'x=2', 'x=3', 'x=4', 'x=5', 'x=6', 'x=7', 'x=8', 'x=9']
        o3 = ['x=0.0', 'x=0.5', 'x=1.0', 'x=1.5', 'x=2.0', 'x=2.5', 'x=3.0', 'x=3.5', 'x=4.0', 'x=4.5']

        self.assertListEqual(self.normal_discretizer.get_labels(), o1)
        self.assertListEqual(self.gamma_discretizer.get_labels(), o2)
        self.assertListEqual(self.exp_discretizer.get_labels(), o3)

    def tearDown(self):
        del self.normal_pdf
        del self.gamma_pdf
        del self.exp_pdf
        del self.normal_factor
        del self.gamma_factor
        del self.exp_factor
        del self.normal_discretizer
        del self.gamma_discretizer
        del self.exp_discretizer


class TestRoundingDiscretizer(unittest.TestCase):
    def setUp(self):
        self.normal_pdf = lambda x : np.exp(-x*x/2) / (np.sqrt(2*np.pi))
        gamma_rv = gamma(3)
        self.gamma_pdf = gamma_rv.pdf
        exp_rv = expon()
        self.exp_pdf = exp_rv.pdf

        self.normal_factor = ContinuousFactor(self.normal_pdf)
        self.gamma_factor = ContinuousFactor(self.gamma_pdf, lb=0)
        self.exp_factor = ContinuousFactor(self.exp_pdf, lb=0)

        self.normal_discretizer = RoundingDiscretizer(self.normal_factor, -5, 5, 1)
        self.gamma_discretizer = RoundingDiscretizer(self.gamma_factor, 0, 5, 1)
        self.exp_discretizer = RoundingDiscretizer(self.exp_factor, 0, 5, 0.5)

    def test_get_discrete_values(self):
        # The output for the get_discrete_values method has been cross checked
        # using discretize {actuar} package in R, assuming that it gives correct results.
        # The required R commands to reproduce the results have also been added.

        # library(actuar);discretize(pnorm(x), method = "rounding", from = -5, to = 5, step = 1)
        normal_desired_op = np.array([3.111022e-06, 2.292314e-04, 5.977036e-03, 6.059754e-02,
                              2.417303e-01, 3.829249e-01, 2.417303e-01, 6.059754e-02,
                              5.977036e-03, 2.292314e-04])
        normal_obtained_op = np.array(self.normal_discretizer.get_discrete_values())
        np_test.assert_almost_equal(normal_desired_op, normal_obtained_op)

        # library(actuar);discretize(pgamma(x, 3), method = "rounding", from = 0, to = 5, step = 1)
        gamma_desired_op = np.array([0.01438768, 0.17676549, 0.26503371, 0.22296592, 0.14726913])
        gamma_obtained_op = np.array(self.gamma_discretizer.get_discrete_values())
        np_test.assert_almost_equal(gamma_desired_op, gamma_obtained_op)

        # library(actuar);discretize(pexp(x), method = "rounding", from = 0, to = 5, step = 0.5)
        exp_desired_op = np.array([0.221199217, 0.306434230, 0.185861756, 0.112730853, 0.068374719, 0.041471363,
                                    0.025153653, 0.015256462, 0.009253512, 0.005612539])
        exp_obtained_op = np.array(self.exp_discretizer.get_discrete_values())
        np_test.assert_almost_equal(exp_desired_op, exp_obtained_op)

        # Note, for the cases when step cannot divide the (frm,to) interval into
        # equal bins, the R commands might produce one less probability mass (for the last label).

    def tearDown(self):
        del self.normal_pdf
        del self.gamma_pdf
        del self.exp_pdf
        del self.normal_factor
        del self.gamma_factor
        del self.exp_factor
        del self.normal_discretizer
        del self.gamma_discretizer
        del self.exp_discretizer


class TestUnbiasedDiscretizer(unittest.TestCase):
    def setUp(self):
        gamma_rv = gamma(3)
        self.gamma_pdf = gamma_rv.pdf
        exp_rv = expon()
        self.exp_pdf = exp_rv.pdf

        self.gamma_factor = ContinuousFactor(self.gamma_pdf, lb=0)
        self.exp_factor = ContinuousFactor(self.exp_pdf, lb=0)

        self.gamma_discretizer = UnbiasedDiscretizer(self.gamma_factor, 0, 5, 1)
        self.exp_discretizer = UnbiasedDiscretizer(self.exp_factor, 0, 5, 0.5)

    def test_get_discrete_values(self):
        # The output for the get_discrete_values method has been cross checked
        # using discretize {actuar} package in R, assuming that it gives correct results.
        # The required R commands to reproduce the results have also been added.

        # library(actuar);discretize(pgamma(x, 3), method = "unbiased", lev = levgamma(x, 3), from = 0, to = 5, step = 1)
        gamma_desired_op = np.array([0.02333693, 0.17134370, 0.25942725, 0.22176384, 0.14794879, 0.05152747])
        gamma_obtained_op = np.array(self.gamma_discretizer.get_discrete_values())
        np_test.assert_almost_equal(gamma_desired_op, gamma_obtained_op)

        # library(actuar);discretize(pexp(x), method = "unbiased", lev = levexp(x), from = 0, to = 5, step = 0.5)
        exp_desired_op = np.array([0.213061319, 0.309636243, 0.187803875, 0.113908808, 0.069089185, 0.041904709,
                                    0.025416491, 0.015415881, 0.009350204, 0.005671186, 0.002004152])
        exp_obtained_op = np.array(self.exp_discretizer.get_discrete_values())
        np_test.assert_almost_equal(exp_desired_op, exp_obtained_op)

        # Note, for the cases when step cannot divide the (frm,to) interval into
        # equal bins, the R commands might produce one less probability mass (for the last label).

    def tearDown(self):
        del self.gamma_pdf
        del self.exp_pdf
        del self.gamma_factor
        del self.exp_factor
        del self.gamma_discretizer
        del self.exp_discretizer
