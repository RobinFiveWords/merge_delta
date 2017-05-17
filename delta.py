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