import os
from typing import Tuple
from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from Utils import Utils


def trim_text(text: str):
    """
    Remove extra space characters from text (blank, newline, tab, etc.)
    """
    return text.strip().replace("\n", " ")


class DocumentParser:
    project_id = ''
    location = ''
    ocr_processor_id = ''
    processor_version = ''

    def __init__(self):
        self.config = Utils.load_settings()
        self.project_id = self.config['project_id']
        self.location = self.config['location']
        self.ocr_processor_id = self.config['ocr_processor_id']
        self.form_processor_id = self.config['form_processor_id']
        self.processor_version = self.config['processor_version']

    def is_document_supported(
            self,
            file_path: str
    ) -> Tuple[bool, str]:
        # Online processing request to Document AI
        document = self.process_document(file_path, self.ocr_processor_id)

        text = document.text

        supported_documents = self.config["supported_documents"]
        for supported_document in supported_documents:
            if supported_document in text:
                return True, str(supported_document)
        return False, ""

    def process_document(
            self,
            file_path: str, processor_id: str
    ) -> documentai.Document:
        # You must set the api_endpoint if you use a location other than 'us'.
        opts = ClientOptions(api_endpoint=f"{self.location}-documentai.googleapis.com")
        mime_type_map = {'pdf': 'application/pdf',
                         'tif': 'image/tiff'}
        if file_path.endswith(".pdf"):
            mime_type = mime_type_map['pdf']
        elif file_path.endswith(".tif"):
            mime_type = mime_type_map['tif']
        else:
            print("Unsupported file: {}.".format(file_path))
            return None

        client = documentai.DocumentProcessorServiceClient(client_options=opts)

        name = client.processor_version_path(
            self.project_id, self.location, processor_id, self.processor_version
        )

        # Read the file into memory
        with open(file_path, "rb") as image:
            image_content = image.read()

        # Load Binary Data into Document AI RawDocument Object
        raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

        # Configure the process request
        request = documentai.ProcessRequest(name=name, raw_document=raw_document)

        result = client.process_document(request=request)

        return result.document

    def extract_data(self, file_path, document_type):
        document = self.process_document(file_path, self.form_processor_id)
        file_name = os.path.basename(file_path).split(".")[0]
        document_data = {"file": file_name, "type": document_type}

        for page in document.pages:
            for field in page.form_fields:
                key = (trim_text(field.field_name.text_anchor.content))
                value = (trim_text(field.field_value.text_anchor.content))
                if "DATED" in key:
                    document_data["date"] = value
                elif "Name" in key:
                    document_data["name"] = value
                elif "Address" in key:
                    document_data["address"] = value
                elif "Amount" in key:
                    document_data["amount"] = value
                elif "FILED WITH" in key:
                    document_data["state"] = value

        return document_data
