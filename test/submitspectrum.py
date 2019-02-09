import json
import requests


spectrum = {}
spectrum["peaks"] = [[100, 100], [101, 90]]
spectrum["MZ"] = 70
spectrum["CHARGE"] = 1
spectrum["COMPOUND_NAME"] = "A"
spectrum["MOLECULEMASS"] = "0"
spectrum["INSTRUMENT"] = "qTof"
spectrum["IONSOURCE"] = "LC-ESI"
spectrum["SMILES"] = "N/A"
spectrum["INCHI"] = "N/A"
spectrum["INCHIAUX"] = "N/A"
spectrum["CHARGE"] = "1"
spectrum["IONMODE"] = "Positive"
spectrum["PUBMED"] = "N/A"
spectrum["ACQUISITION"] = "Crude"
spectrum["EXACTMASS"] = "0"
spectrum["DATACOLLECTOR"] = "Ming"
spectrum["ADDUCT"] = "M+H"
spectrum["CASNUMBER"] = "N/A"
spectrum["PI"] = "Ming"

username = "YOURUSERNAME"
password = "YOURPASSWORD"

r = requests.post("http://localhost:5050/depostsinglespectrum", data = {"spectrum" : json.dumps(spectrum), "username" : username, "password" : password})

print(r.text)
