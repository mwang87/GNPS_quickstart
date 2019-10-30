import pandas as pd
import sys
sys.path.insert(0, "..")

def test_datat1_failure():
    import batch_validator
    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/bile_acid_ref_failure.tsv")
    assert(passes_validation == False)

def test_datat2():
    import batch_validator
    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/GNPS00001_output_batch.tsv")
    assert(passes_validation == True)

    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/GNPS00002_output_batch.tsv")
    assert(passes_validation == True)

    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/GNPS00003_output_batch.tsv")
    assert(passes_validation == False)

    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/GNPS00004_output_batch.tsv")
    assert(passes_validation == False)

    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/GNPS00005_output_batch.tsv")
    assert(passes_validation == False)

    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/GNPS00006_output_batch.tsv")
    assert(passes_validation == False)

def test_dataset3():
    import batch_validator
    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/library_batch_full_test.tsv")
    assert(passes_validation == True)

    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/smalltest.tsv")
    assert(passes_validation == True)

    passes_validation, failures, errors_list, valid_rows, total_rows = batch_validator.perform_batch_validation("reference_data/smalltest_failing.tsv")
    assert(passes_validation == True)