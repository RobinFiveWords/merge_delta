import pandas as pd
import numpy as np
if pd.__version__ >= '0.21':
    from pandas.api.types import CategoricalDtype


def delta(df1, df2, index_cols=None, suffixes=('_1', '_2'),
          reset_indexes=True, value_counts=True):
    if isinstance(index_cols, pd.Index):
        index_cols = list(index_cols)
    if index_cols:
        df1 = df1.set_index(index_cols)
        df2 = df2.set_index(index_cols)
    full = (pd.merge(df1, df2, left_index=True, right_index=True,
                     how='outer', suffixes=suffixes, indicator=True)
            .astype({'_merge': object}))
    index_both = full[full._merge == 'both'].index
    df1b = df1.reindex(index_both)
    df2b = df2.reindex(index_both)
    mask_match = (((pd.isnull(df1b) & pd.isnull(df2b)) | (df1b == df2b))
                  .all(axis=1))
    index_changes = mask_match[~mask_match].index
    if index_changes.size > 0:
        full.loc[index_changes, '_merge'] = 'c'
    mappings = {
        'both': 'm',        # match
        'right_only': 'a',  # add
        'c': 'c',           # change
        'left_only': 'd',   # delete
    }
    full._merge = full._merge.map(mappings)
    add = df2.reindex(full.loc[full._merge == 'a'].index)
    change = full.loc[full._merge == 'c'].drop('_merge', axis=1)
    delete = df1.reindex(full.loc[full._merge == 'd'].index)
    if reset_indexes:
        full = full.reset_index()
        add = add.reset_index()
        change = change.reset_index()
        delete = delete.reset_index()
    if value_counts:
        remappings = {
            'm': 'match',
            'a': 'add',
            'c': 'change',
            'd': 'delete',
        }
        print()
        print(full._merge.value_counts().rename(index=remappings))
    return full, add, change, delete


def delta_robust(df1, df2, index_cols, **kwargs):
    """Compute delta between two files while encoding index_cols
    to prevent hash collision.

    Use `delta_robust2` for pandas v0.21 onward."""
    df1 = df1.copy()
    df2 = df2.copy()
    if isinstance(index_cols, pd.Index):
        index_cols = list(index_cols)
    kwargs.pop('reset_indexes', None)
    cats = [pd.Categorical(np.union1d(*[df[col].values for df in [df1, df2]]))
              .categories
            for col in index_cols]
    types = [df1[col].dtype for col in index_cols]

    for i, col in enumerate(index_cols):
        df1.loc[:, col] = df1[col].astype('category', categories=cats[i]).cat.codes
        df2.loc[:, col] = df2[col].astype('category', categories=cats[i]).cat.codes
    f, a, c, d = delta(df1, df2, index_cols, **kwargs)
    for i, col in enumerate(index_cols):
        f[col] = pd.Categorical.from_codes(f[col], cats[i]).astype(types[i])
        a[col] = pd.Categorical.from_codes(a[col], cats[i]).astype(types[i])
        c[col] = pd.Categorical.from_codes(c[col], cats[i]).astype(types[i])
        d[col] = pd.Categorical.from_codes(d[col], cats[i]).astype(types[i])
    return f, a, c, d


def delta_robust2(df1, df2, index_cols, **kwargs):
    """Compute delta between two files while encoding index_cols
    to prevent hash collision.

    Use `delta_robust` before pandas v0.21."""
    df1 = df1.copy()
    df2 = df2.copy()
    if isinstance(index_cols, pd.Index):
        index_cols = list(index_cols)
    kwargs.pop('reset_indexes', None)
    cats = [pd.Categorical(np.union1d(*[df[col].values for df in [df1, df2]]))
              .categories
            for col in index_cols]
    types = [df1[col].dtype for col in index_cols]

    for i, col in enumerate(index_cols):
        cat_dtype = CategoricalDtype(categories=cats[i])
        df1.loc[:, col] = df1[col].astype(cat_dtype).cat.codes
        df2.loc[:, col] = df2[col].astype(cat_dtype).cat.codes
    f, a, c, d = delta(df1, df2, index_cols, **kwargs)
    for i, col in enumerate(index_cols):
        f[col] = pd.Categorical.from_codes(f[col], cats[i]).astype(types[i])
        a[col] = pd.Categorical.from_codes(a[col], cats[i]).astype(types[i])
        c[col] = pd.Categorical.from_codes(c[col], cats[i]).astype(types[i])
        d[col] = pd.Categorical.from_codes(d[col], cats[i]).astype(types[i])
    return f, a, c, d
