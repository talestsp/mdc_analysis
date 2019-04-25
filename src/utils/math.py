def normalize(col_series, complement=False):
    if complement:
        return 1 - ((col_series - col_series.min()) / (col_series.max() - col_series.min()))
    else:
        return (col_series - col_series.min()) / (col_series.max() - col_series.min())
