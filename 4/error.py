import numpy as np

# Python 3.5's standard library has versions for these two in `statistics`
def mean(data, axis = 0):
    return data.sum(axis = axis) / data.shape[axis]

# TODO: check out whether this naive version is numerically sound
def variance(data, average = None, axis = 0):
    N = data.shape[axis]
    if average is None:
        average = mean(data, axis = axis)
    return ( (data - average) ** 2 ).sum(axis = axis) / (N - 1)

def autocorrelation_function(observable, k, average, measurement_variance):
    """
    Compute the autocorrelation function for an observable with the argument k.

    Sample mean and variance have to given.
    """

    if k == 0:
        if observable.ndim > 1:
            return np.ones(observable.shape[1])
        else:
            return 1.

    m = mean(observable[:-k] * observable[k:])
    return (m - average**2) / measurement_variance

def autocorrelation_analysis(observable,
                             average = None, measurement_variance = None):
    """
    Run complete autocorrelation analysis on the given time series.
    Returns the average, its error, the autocorrelation time, its error and the
    effective sampling size in a numpy array.
    """

    if average is None:
        average = mean(observable)
    if measurement_variance is None:
        measurement_variance = variance(observable, average = average)

    N = len(observable)
    if observable.ndim > 1:
        n = observable.shape[1]
        tau = np.empty(n)
        tau[:] = .5
        for i in range(n):
            k = 1
            while k < 6 * tau[i] or k > N:
                tau[i] += autocorrelation_function(observable[:,i], k, average[i],
                                                   measurement_variance[i])
                k += 1
    else:
        tau = .5
        k = 1
        while k < 6 * tau or k > N:
            tau += autocorrelation_function(observable, k, average,
                                            measurement_variance)
            k += 1

    N_eff = N / tau
    e_obs = np.sqrt(measurement_variance / N_eff)
    e_tau = np.sqrt(12 * tau / N)

    return np.array( (average, e_obs, tau, e_tau, N_eff) )

def binning_analysis(observable, bin_width, average = None, measurement_variance = None):
    """
    Computes binning \\tau and error estimate \\epsilon^2 from time series and
    given bin width, returns (\\tau, \\epsilon^2).

    If the bin width does not divide the series length, the series will be
    truncated to the next smallest length that is a multiple of the given width.
    If sample average and variance are already computed, they can be given as
    keyword arguments. It is not checked whether these values are actually
    correct.
    """

    k = bin_width
    N = series_length = len(observable)
    N_b = N // k

    bins = np.array([observable[i * k : (i + 1) * k] for i in range(N_b)])
    bin_averages = mean(bins, axis = 1)
    if average is None:
        average = mean(bin_averages)

    bin_variance = variance(bin_averages, average = average)
    if measurement_variance is None:
        measurement_variance = variance(observable, average = average)

    auto_correlation_time = k / 2 * (bin_variance / measurement_variance)
    binning_error = bin_variance / N_b
    return auto_correlation_time, binning_error

def jackknife_analysis(observable, bin_width, average = None):
    """
    Compute jackknife error for an observable.
    `observable` can be a two dimensional array in which case the analysis is
    performed for two or more time series of the same length simultaneously.

    If the bin width does not divide the series length, the series will be
    truncated to the next smallest length that is a multiple of the given width.
    If sample average and variance are already computed, they can be given as
    keyword arguments. It is not checked whether these values are actually
    correct.
    """

    k = bin_width
    N = series_length = len(observable)
    N_b = N // k

    if average is None:
        average = mean(bin_averages)

    bins = np.array([observable[i * k : (i + 1) * k] for i in range(N_b)])
    bin_averages = mean(bins, axis = 1)

    jackknife_averages = (N * average - k * bin_averages) / (N - k)
    # fuck python2 up its fucking ass
    jackknife_error = (N_b - 1) / float(N_b) \
                    * ( (jackknife_averages - average)**2 ).sum(axis = 0)
    return jackknife_error