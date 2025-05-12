from app.modules.sber_extract.pdf2txtev import pdf_2_text
from app.modules.sber_extract.sberbankPDFtext2Excel import sberbankPDFtext2Excel


def sberbankPDF2Excel(input_file_name: str,
                      format: str = 'auto', ) -> str:
    """function converts pdf or text file with Sperbank extract to Excel or CSV format

    Args:
        input_file_name (str): _description_
        format (str, optional): _description_. Defaults to 'auto'.

    Raises:
        exceptions.InputFileStructureError: _description_

    Returns:

    """

    pdf_text = pdf_2_text(input_file_name)

    df = sberbankPDFtext2Excel(pdf_text)

    return df
