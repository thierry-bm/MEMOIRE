import warnings

import cvxpy as cvx
import numpy as np

import model.distrs as ds

from .math_ops import *
from .lipschitzexp import LipschitzExp

class Utility(Function):
    pass

class ExpUtility(Utility):
    def __init__(self,β):
        self.β = β
        self.k = 1

    def __str__(self):
        return 'u(r) = -exp(-%2.2fr + 1)' % self.β

    def _call(self,r):
        if isinstance(r,ds.Distribution):
            return self._create_distribution(r)
        β = self.β
        exp = np.exp
        return 1/β * (1 - exp(-β*r))

    def cvx_util(self,r):
        β = self.β
        exp = cvx.exp
        return 1/β * (1 - exp(-β*r))

    def _derive(self,r):
        return np.exp(-β*r)

class LipschitzExpUtility(Utility):
    def __init__(self,β,r0):
        self.β = β
        self.r0 = r0
        self.k = 1

    def _call(self,r):
        β,r0 = self.β,self.r0
        exp = np.exp
        return (r >= r0)* (1/β * (1 - exp(-β*r))) + (r<r0) * (r*exp(-β*r0) + 1/β*(1-(1+β*r0)*exp(-β*r0)))

    def cvx_util(self,r):
        return LipschitzExp(r,self.β,self.r0)

    @property
    def γ(self):
        return np.exp(-self.β * self.r0)

class LinearUtility(Utility):
    def __init__(self,β):
        self.β = β
        self.k=1
        self.gamma_lipschitz = β

    def __str__(self):
        return 'u(r) = min(r,%2.2fr)' % self.β

    def cvx_util(self,r):
        return cvx.min_elemwise(r, self.β * r)

    def _call(self,r):
        # TODO Rewrite the method
        return np.amin(np.array([r,self.β*r]),axis=0)

    def _derive(self,r):
        return (r<=0)*1 + (r>0)*self.β


class LinearPlateauUtility(Utility):
    '''Piecewise linear utility such that ∂u(x) = 1 for x ∈ (-∞,0), ∂u(x) = β for x ∈ [0,x0]
    and ∂u(x) = 0 for x>x0.
    '''
    def __init__(self,β,x0):
        '''Instantiates the LinearPlateauUtility class.

        Args:
            β: second branch slope
            x0: break-off point
        '''
        if β > 1:
            raise ValueError('β must be lower than 1.')
        if x0 <= 0:
            raise ValueError('x0 must be higher or equal to 0.')
        self.β = β
        self.x0 = x0
        self.k = 1
        
    def __str__(self):
        return 'u(r) = min(β*r,r,x0)'

    def cvx_util(self,r):
        return cvx.min_elemwise(r, self.β*r, self.β*self.x0)

    def _call(self,r):
        r = np.array(r)
        return np.minimum(np.minimum(self.β*r,r),self.β*self.x0)

    def inverse(self,r):
        x0,β = self.x0,self.β
        if isinstance(r,list) or isinstance(r,np.ndarray):
            r = np.array(r)
            inv = (r < 0) * r + \
                  (r >= 0) * 1/β*r
            inv[r>self.x0] = np.infty
            return inv
        else:
            if r < 0:
                return r
            elif r <= self.x0:
                return 1/β*r
            else:
                return np.infty                
    
    @property
    def γ(self):
        return self.β