import numpy as np

from ensemble_predict import (
    ensemble_predict
)

sample = np.random.rand(
    1,
    10
)

result = ensemble_predict(
    sample
)

print(result)