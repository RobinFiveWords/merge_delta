## merge_delta
### pandas merge that identifies rows added, changed, and deleted

### Use

`full, add, change, delete = delta(df1, df2, index_cols=None, suffixes=('_1', '_2'),
                                   reset_indexes=True, value_counts=True)`

If `index_cols` is None, the dataframes are assumed to already be indexed by the
columns on which they are to be joined. `index_cols` will accept an Index, such as
`delta(df1, df2, df1.columns[:4])`, in addition to a list or single column name.
