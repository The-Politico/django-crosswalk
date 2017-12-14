from fuzzywuzzy import fuzz, process


def default_process(query_value, block_values):
    return process.extractOne(
        query_value,
        block_values,
    )


def partial_ratio_process(query_value, block_values):
    return process.extractOne(
        query_value,
        block_values,
        scorer=fuzz.partial_ratio
    )


def token_sort_ratio_process(query_value, block_values):
    return process.extractOne(
        query_value,
        block_values,
        scorer=fuzz.token_sort_ratio
    )


def token_set_ratio_process(query_value, block_values):
    return process.extractOne(
        query_value,
        block_values,
        scorer=fuzz.token_set_ratio
    )
