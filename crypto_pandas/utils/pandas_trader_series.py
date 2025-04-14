from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import ttest_1samp


@pd.api.extensions.register_series_accessor("pt")
class PandasTraderSeriesAccessor:
    def __init__(self, pandas_obj):
        self.data = pandas_obj

    def floor_series(self, digits: int = 0) -> pd.Series:
        return np.floor(self.data * 10**digits) / 10**digits

    def ceil_series(self, digits: int = 0) -> pd.Series:
        return np.ceil(self.data * 10**digits) / 10**digits

    def t_test(self) -> Any:
        return ttest_1samp(self.data, self.data.mean())
