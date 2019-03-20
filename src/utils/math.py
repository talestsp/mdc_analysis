def normalize(col_series):
    return (col_series - col_series.min()) / (col_series.max() - col_series.min())

