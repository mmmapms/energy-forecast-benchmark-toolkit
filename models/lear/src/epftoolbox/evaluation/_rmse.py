"""
Function that implements the root mean square error (RMSE) metric.
"""

# Author: Jesus Lago

# License: AGPL-3.0 License

import numpy as np
from epftoolbox.evaluation._ancillary_functions import _process_inputs_for_metrics


def RMSE(p_real, p_pred):
    """Function that computes the root mean square error (RMSE) between two forecasts

    .. math:: \\mathrm{RMSE} = \\frac{1}{N}\\sum_{i=1}^N \\sqrt{\\bigl(p_\\mathrm{real}[i]−p_\\mathrm{pred}[i]\\bigr)^2}

    ``p_real`` and ``p_pred`` can either be of shape
    :math:`(n_\\mathrm{days}, n_\\mathrm{prices/day})`,
    :math:`(n_\\mathrm{prices}, 1)`, or :math:`(n_\\mathrm{prices}, )` where
    :math:`n_\\mathrm{prices} = n_\\mathrm{days} \\cdot n_\\mathrm{prices/day}`.

    Parameters
    ----------
    p_real : numpy.ndarray, pandas.DataFrame
        Array/dataframe containing the real prices.
    p_pred : numpy.ndarray, pandas.DataFrame
        Array/dataframe containing the predicted prices.

    Returns
    -------
    float
        The root mean square error (RMSE).

    Example
    -------

    >>> from epftoolbox.data import read_data
    >>> import pandas as pd
    >>>
    >>> # Download available forecast of the NP market available in the library repository
    >>> # These forecasts accompany the original paper
    >>> forecast = pd.read_csv('https://raw.githubusercontent.com/jeslago/epftoolbox/master/' +
    ...                       'forecasts/Forecasts_NP_DNN_LEAR_ensembles.csv', index_col=0)
    >>>
    >>> # Transforming indices to datetime format
    >>> forecast.index = pd.to_datetime(forecast.index)
    >>>
    >>> # Reading data from the NP market
    >>> _, df_test = read_data(path='.', dataset='NP', begin_test_date=forecast.index[0],
    ...                        end_test_date=forecast.index[-1])
    Test datasets: 2016-12-27 00:00:00 - 2018-12-24 23:00:00
    >>>
    >>> # Extracting forecast of DNN ensemble and display
    >>> fc_DNN_ensemble = forecast.loc[:, ['DNN Ensemble']]
    >>>
    >>> # Extracting real price and display
    >>> real_price = df_test.loc[:, ['Price']]
    >>>
    >>> # Building the same datasets with shape (ndays, n_prices/day) instead
    >>> # of shape (nprices, 1) and display
    >>> fc_DNN_ensemble_2D = pd.DataFrame(fc_DNN_ensemble.values.reshape(-1, 24),
    ...                                   index=fc_DNN_ensemble.index[::24],
    ...                                   columns=['h' + str(hour) for hour in range(24)])
    >>> real_price_2D = pd.DataFrame(real_price.values.reshape(-1, 24),
    ...                              index=real_price.index[::24],
    ...                              columns=['h' + str(hour) for hour in range(24)])
    >>> fc_DNN_ensemble_2D.head()
                       h0         h1         h2  ...        h21        h22        h23
    2016-12-27  24.349676  23.127774  22.208617  ...  27.686771  27.045763  25.724071
    2016-12-28  25.453866  24.707317  24.452384  ...  29.424558  28.627130  27.321902
    2016-12-29  28.209516  27.715400  27.182692  ...  28.473288  27.926241  27.153401
    2016-12-30  28.002935  27.467572  27.028558  ...  29.086532  28.518688  27.738548
    2016-12-31  25.732282  24.668331  23.951569  ...  26.965008  26.450995  25.637346

    According to the paper, the RMSE of the DNN ensemble for the NP market is 3.333.
    Let's test the metric for different conditions

    >>> # Evaluating RMSE when real price and forecasts are both dataframes
    >>> RMSE(p_pred=fc_DNN_ensemble, p_real=real_price)
    3.3331928060389995
    >>>
    >>> # Evaluating RMSE when real price and forecasts are both numpy arrays
    >>> RMSE(p_pred=fc_DNN_ensemble.values, p_real=real_price.values)
    3.3331928060389995
    >>>
    >>> # Evaluating RMSE when input values are of shape (ndays, n_prices/day) instead
    >>> # of shape (nprices, 1)
    >>> # Dataframes
    >>> RMSE(p_pred=fc_DNN_ensemble_2D, p_real=real_price_2D)
    3.3331928060389995
    >>> # Numpy arrays
    >>> RMSE(p_pred=fc_DNN_ensemble_2D.values, p_real=real_price_2D.values)
    3.3331928060389995
    >>>
    >>> # Evaluating RMSE when input values are of shape (nprices,)
    >>> # instead of shape (nprices, 1)
    >>> # Pandas Series
    >>> RMSE(p_pred=fc_DNN_ensemble.loc[:, 'DNN Ensemble'],
    ...      p_real=real_price.loc[:, 'Price'])
    3.3331928060389995
    >>> # Numpy arrays
    >>> RMSE(p_pred=fc_DNN_ensemble.values.squeeze(),
    ...      p_real=real_price.values.squeeze())
    3.3331928060389995

    """

    # Checking if inputs are compatible
    p_real, p_pred = _process_inputs_for_metrics(p_real, p_pred)

    return np.sqrt(np.mean((p_real - p_pred) ** 2))
