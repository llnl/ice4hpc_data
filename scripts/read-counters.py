# std imports
from argparse import ArgumentParser
import json

# tpl imports
import hatchet as ht


def get_counter_data(fpath):
    # read in HPCToolkit profile
    gf = ht.GraphFrame.from_hpctoolkit(fpath)

    # aggregate along ranks
    gf.drop_index_levels()

    # select only the program root
    filtered_gf = gf.filter([{'name': '<program root>'}], squash=True)

    # copy the df and remove exclusive columns
    counters = filtered_gf.dataframe.copy(deep=True)
    counters = counters.loc[:, counters.columns.str.endswith(' (I)')]
    counters.rename(columns = lambda x: x[:-3] if x.endswith(' (I)') else x, inplace=True)
    counters = counters.to_dict(orient='list')
    for key, val in counters.items():
        assert len(val) == 1
        counters[key] = val[0]
    return counters


def main():
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', required=True, type=str, help='input hpctoolkit db path')
    parser.add_argument('-a', '--append', type=str, help='existing results json to append to')
    args = parser.parse_args()

    # init data dict
    results = {}
    if args.append:
        with open(args.append, 'r') as fp:
            results = json.load(fp)

    # fill in counter data
    counters = get_counter_data(args.input)
    results.update(counters)

    # write out results
    dest = 'results.json'
    if args.append:
        dest = args.append
    with open(dest, 'w') as fp:
        json.dump(results, fp)
        


if __name__ == '__main__':
    main()
