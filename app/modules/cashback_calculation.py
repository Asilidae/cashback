import numpy as np

def cashback_calculation(df, name_col, cashback_params):
    conditions = [
        (df['type_transaction'] == 'buy') & (df['category'] != 'Other') & (df['cost'] > 10000),
        (df['type_transaction'] == 'buy') & (df['category'] != 'Other') & (df['cost'] <= 10000),
        (df['type_transaction'] == 'buy') & (df['category'] == 'Other')
    ]
    choices = [df['cost'] * cashback_params["partner"]["over10"],
               df['cost'] * cashback_params["partner"]["default"],
               df['cost'] * cashback_params["not_partner"]]

    df[name_col] = np.select(conditions, choices, default=0)
    return df