from DocumentParser import DocumentParser
from tqdm import tqdm
from Utils import Utils
import pandas as pd
from os import listdir
from os.path import join, isfile

config = Utils.load_settings()

path = config["input_files_directory"]
supported_documents_list = []
discarded_documents_list = []

document_parser = DocumentParser()
files_in_directory = listdir(path)
for filename in tqdm(files_in_directory, total=len(files_in_directory)):  # iterates over all the files in 'path'

    full_path = join(path, filename)  # joins the path with the filename

    if isfile(full_path):

        is_document_supported, document_type = document_parser.is_document_supported(file_path=full_path)
        if is_document_supported:
            extracted_values = document_parser.extract_data(full_path, document_type)
            supported_documents_list.append(extracted_values)
        else:
            discarded_documents_list.append(full_path)
            print("{} discarded!".format(full_path))


dataframe = pd.DataFrame(supported_documents_list)
dataframe.to_csv("output/test.csv")
print("Data extracted for {} files.".format(len(supported_documents_list)))
if len(discarded_documents_list)>1:
    print("Discarded {} documents. List is available in '{}' file".format(len(discarded_documents_list)))