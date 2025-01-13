
import re
from typing import Callable, List

import pandas as pd

from difflib import SequenceMatcher


def group_similar(names: List[str], strip_func: Callable, clean_cache_thresh: int = None, tolerance: float = 0.85, preset: List[str] = None):
    """ Groups synthatically similar text according to Sequence Matcher

    Args:
        names: list of strings to be matched against each other
        strip_func: Function used to clean the new version of the name
        clean_cache_thresh: how many names should be procesed before removing very low count names from the match list
        tolerance: how good the match must be
    """

    names = sorted(names)
    n = len(names)
    print(f"Processing {len(names)} Names")

    if preset is None:
        new_names = [names[0]]
        results = {names[0]: names[0]}
    else:
        new_names = preset.copy()
        results = {}


    for i, name in enumerate(names):
        clean_name = strip_func(name)

        found = False
        for new_name in new_names:
            if re.search(fr'\b{clean_name}\b', new_name) or re.search(fr'\b{new_name}\b', clean_name):
                results[name] = new_name
                found = True
                break

            ratio = SequenceMatcher(None, clean_name, new_name).ratio()
            if ratio > tolerance:
                results[name] = new_name
                found = True
                break

        if not found:
            new_names.append(clean_name)
            results[name] = clean_name

        if clean_cache_thresh is not None and i % clean_cache_thresh == 0:
            counts = pd.Series(list(results.values())).value_counts()
            counts = counts[counts > 3]

            if len(counts) == 0:
                new_names = [names[i+1]]
            else:
                new_names = counts.index.to_list()

            print(f"Done {round(100 * i/n, 2)}%", end='\r')

    print("Done 100.00%")
    return results
