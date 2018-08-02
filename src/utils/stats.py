def quantiles(serie):
    quantiles_100 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    quantiles_dct = {}
    for quantile in quantiles_100:
        quantiles_dct[quantile] = serie.quantile(quantile)
    return quantiles_dct