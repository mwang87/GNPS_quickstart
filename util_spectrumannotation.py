
import util


def save_spectrum(spectrum_json, output_filename):

    output_list = []
    output_list.append("BEGIN IONS")
    output_list.append("PEPMASS=%s" % (str(spectrum_json["MZ"])))
    output_list.append("CHARGE=%s" % (str(spectrum_json["CHARGE"])))
    output_list.append("MSLEVEL=2")
    output_list.append("PRECURSORINTENSITY=0")
    output_list.append("SCANS=1")
    for peak in spectrum_json["peaks"]:
        output_list.append("%s %s" % (str(peak[0]), str(peak[1])))
    output_list.append("END IONS")

    with open(output_filename, "w") as output_file:
        output_file.write("\n".join(output_list))


def launch_addreferencespectrum_workflow(spectrum_json, local_filename, remote_filename, username, password, email, test=True):
    invokeParameters = get_referencespectra_parameters()
    invokeParameters["email"] = email

    invokeParameters["spec_on_server"] = remote_filename
    invokeParameters["ADDSPECTRA_COMPOUND_NAME"] = spectrum_json["COMPOUND_NAME"]
    invokeParameters["ADDSPECTRA_CHARGE"] = spectrum_json["CHARGE"]
    invokeParameters["ADDSPECTRA_MOLECULEMASS"] = "0"
    invokeParameters["ADDSPECTRA_INSTRUMENT"] = spectrum_json["INSTRUMENT"]
    invokeParameters["ADDSPECTRA_IONSOURCE"] = spectrum_json["IONSOURCE"]
    invokeParameters["ADDSPECTRA_SMILES"] = spectrum_json["SMILES"]
    invokeParameters["ADDSPECTRA_INCHI"] = spectrum_json["INCHI"]
    invokeParameters["ADDSPECTRA_INCHIAUX"] = spectrum_json["INCHIAUX"]
    invokeParameters["ADDSPECTRA_IONMODE"] = spectrum_json["IONMODE"]
    invokeParameters["ADDSPECTRA_PUBMED"] = spectrum_json["PUBMED"]
    invokeParameters["ADDSPECTRA_ACQUISITION"] = spectrum_json["ACQUISITION"]
    invokeParameters["ADDSPECTRA_EXACTMASS"] = spectrum_json["EXACTMASS"]
    invokeParameters["ADDSPECTRA_DATACOLLECTOR"] = spectrum_json["DATACOLLECTOR"]
    invokeParameters["ADDSPECTRA_ADDUCT"] = spectrum_json["ADDUCT"]
    invokeParameters["ADDSPECTRA_CASNUMBER"] = spectrum_json["CASNUMBER"]
    invokeParameters["ADDSPECTRA_PI"] = spectrum_json["PI"]

    invokeParameters["desc"] = "MZMine2 Direct Submission - "spectrum_json["description"]

    if test:
        invokeParameters["library_on_server"] = "f.%s/reference_spectra/TEST-LIBRARY.mgf;" % (username)

    task_id = util.invoke_workflow("gnps.ucsd.edu", invokeParameters, username, password)

    return task_id


def get_referencespectra_parameters():
    invokeParameters = {}
    invokeParameters["workflow"] = "ADD-SINGLE-ANNOTATED-BRONZE"
    invokeParameters["protocol"] = "None"
    invokeParameters["desc"] = "Job Description"
    invokeParameters["library_on_server"] = "f.speclibs/GNPS-LIBRARY/GNPS-LIBRARY.mgf;"


    invokeParameters["ADDSPECTRA_LIBQUALITY"] = "3"
    invokeParameters["INTEREST"] = "N/A"
    invokeParameters["ADDSPECTRA_STRAIN"] = "N/A"
    invokeParameters["ADDSPECTRA_USERGENUS"] = "N/A"
    invokeParameters["ADDSPECTRA_USERSPECIES"] = "N/A"
    invokeParameters["ADDSPECTRA_EXTRACTSCAN"] = "1"

    invokeParameters["email"] = "ccms.web@gmail.com"

    return invokeParameters
