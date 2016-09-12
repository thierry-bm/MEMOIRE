import datetime as dt

import numpy as np

import process_data as pd
import model.problem as pr
import model.utility as ut


def get_train_test(samples,shuffle=True):
    if shuffle:
        samples = samples.sample(frac=1)
    train_sz = int(0.8*len(samples))
    train,test = samples[:train_sz],samples[train_sz:]
    X_train,X_test = train.X.values,test.X.values
    X_mean = np.mean(X_train,axis=0)
    X_std = np.std(X_train,axis=0)
    X_train = (X_train - X_mean)/X_std
    X_test = (X_test - X_mean)/X_std
    train.X = X_train
    test.X = X_test
    train[('X','bias')] = np.ones(len(train))
    test[('X','bias')] = np.ones(len(test))
    return train,test


def get_optimal_decision(X,r,λ,u):
    problem = pr.Problem(X,r,λ,u)
    problem.solve()
    return problem


def get_CE(train,test,λ,u):
    X_train,r_train = train.X.values,train.r.values.flatten()
    X_test,r_test = test.X.values,test.r.values.flatten()
    problem = pr.Problem(X_train,r_train,λ,u)
    problem.solve()
    insample_CE = problem.insample_CE()
    outsample_CE = problem.outsample_CE(X_test,r_test)
    return insample_CE,outsample_CE


if (__name__ == '__main__'):
    switch = False
    if switch:
        start_date = dt.date(2010,1,1)
        end_date = dt.date(2015,12,31)
        mkt = pd.get_market(start_date,end_date)
        samples = pd.get_samples(mkt)
        train,test = get_train_test(samples)

        u = ut.LinearPlateauUtility(0.6,0.03)
        λ = 1
