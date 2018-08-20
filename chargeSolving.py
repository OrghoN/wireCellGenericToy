# External Dependencies
import numpy as np
from sklearn import linear_model

# Internal Dependencies
from dataTypes import *

def solve(wireMatrix, geometryMatrix, alpha = 1):
    chargeSolving = linear_model.Lasso(positive = True, alpha=alpha)
    chargeSolving.fit(geometryMatrix,wireMatrix)

    solved = np.reshape(np.matrix(chargeSolving.coef_),(geometryMatrix.shape[1],1))

    return solved
