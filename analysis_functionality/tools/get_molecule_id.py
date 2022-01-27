# fileName1="20200303-195240 DHFR_1-127_NOTF_TICO_pH_745_TROLOX_pH_740 #009-001"
# fileName2="20200303-203233 DHFR_1-127_NOTF_TICO_pH_745_TROLOX_pH_740 #009-002"
# fileNameList=[fileName1, fileName2]

def get_molecule_id(fileName, fileNameList):
    indices = [i for i, name in enumerate(fileNameList) if name in fileName] #only one hopefully
    return indices[0]
# from analysis_functionality.tools.get_molecule_id import get_molecule_id
# print(get_molecule_id(fileName2, fileNameList))