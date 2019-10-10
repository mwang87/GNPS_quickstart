#!/usr/bin/python


import sys
import os
import argparse
import csv
import json
from vladiate import Vlad
from vladiate.validators import UniqueValidator, SetValidator, Ignore, NotEmptyValidator, FloatValidator, IntValidator
from vladiate.inputs import LocalFile

def perform_batch_validation(filename):
    validators = {
        'FILENAME': [
            NotEmptyValidator()
        ],
        'SEQ': [
            SetValidator(valid_set=["*..*", "*.*"])
        ],
        'COMPOUND_NAME': [
            NotEmptyValidator()
        ],
        'MOLECULEMASS': [
            FloatValidator()
        ],
        'INSTRUMENT': [
            SetValidator(valid_set=["qTof", "QQQ", "Ion Trap", "Hybrid FT", "Orbitrap", "ToF"])
        ],
        'IONSOURCE': [
            SetValidator(valid_set=["LC-ESI", "DI-ESI", "EI", "APCI", "ESI"])
        ],
        'EXTRACTSCAN': [
            IntValidator()
        ],
        'SMILES': [
            NotEmptyValidator()
        ],
        'INCHI': [
            NotEmptyValidator()
        ],
        'INCHIAUX': [
            NotEmptyValidator()
        ],
        'CHARGE': [
            IntValidator()
        ],
        'IONMODE': [
            SetValidator(valid_set=["Positive", "Negative"])
        ],
        'PUBMED': [
            NotEmptyValidator()
        ],
        'ACQUISITION': [
            SetValidator(valid_set=["Crude", "Lysate", "Commercial", "Isolated", "Other"])
        ],
        'EXACTMASS': [
            FloatValidator()
        ],
        'DATACOLLECTOR': [
            NotEmptyValidator()
        ],
        'ADDUCT': [
            NotEmptyValidator()
        ],
        'INTEREST': [
            NotEmptyValidator()
        ],
        'LIBQUALITY': [
            SetValidator(valid_set=["1", "2", "3"])
        ],
        'GENUS': [
            NotEmptyValidator()
        ],
        'SPECIES': [
            NotEmptyValidator()
        ],
        'STRAIN': [
            NotEmptyValidator()
        ],
        'CASNUMBER': [
            NotEmptyValidator()
        ],
        'PI': [
            NotEmptyValidator()
        ]
    }

    my_validator = Vlad(source=LocalFile(filename),delimiter="\t",ignore_missing_validators=True,validators=validators)
    passes_validation = my_validator.validate()

    errors_list = []
    for column in my_validator.failures:
        for line_number in my_validator.failures[column]:
            error_dict = {}
            error_dict["header"] = column
            error_dict["line_number"] = line_number + 1 #0 Indexed with 0 being the header row
            error_dict["error_string"] = str(my_validator.failures[column][line_number])

            errors_list.append(error_dict)

    for missing_field in my_validator.missing_fields:
        error_dict = {}
        error_dict["header"] = "Missing Header"
        error_dict["line_number"] = "N/A"
        error_dict["error_string"] = "Missing column %s" % (missing_field)

        errors_list.append(error_dict)

    valid_rows = []
    row_count = 0
    #Read in the good rows
    try:
        no_validation_lines = [int(error["line_number"]) for error in errors_list]
        row_count = 0
        with open(filename) as csvfile:
            reader = csv.DictReader(csvfile, delimiter="\t")
            for row in reader:
                row_count += 1
                if row_count in no_validation_lines:
                    continue
                valid_rows.append(row)
    except:
        #raise
        print("error reading file")


    return passes_validation, my_validator.failures, errors_list, valid_rows, row_count

def perform_summary(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter="\t")

        summary_dict = {}
        summary_dict["row_count"] = sum([1 for row in reader])

        summary_list = []
        summary_list.append({"type" : "row_count", "value" : summary_dict["row_count"]})

        return summary_dict, summary_list

def main():
    parser = argparse.ArgumentParser(description='Validate Stuff.')
    parser.add_argument('inputmetadata', help='inputmetadata')
    args = parser.parse_args()

    passes_validation, failures, errors_list, valid_rows, total_rows = perform_batch_validation(args.inputmetadata)
    no_validation_lines = [int(error["line_number"]) for error in errors_list]

    output_list = ["SUMMARY", os.path.basename(args.inputmetadata), str(total_rows), str(len(valid_rows))]
    print("\t".join(output_list))


if __name__ == "__main__":
    main()