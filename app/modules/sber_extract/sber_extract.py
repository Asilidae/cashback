from . import sberbankPDF2Excel

# SBER


def sber_extract(input_file_name):
    output_Excel_file_name = 'SBER'
    format = "auto"
    output_file_type = 'xlsx'
    reversed_transaction_order = False
    perform_balance_check = True
    leave_intermediate_txt_file = True
    sberbankPDF2Excel.sberbankPDF2Excel(input_file_name=input_file_name,
                     output_file_name=output_Excel_file_name,
                     format=format,
                     leave_intermediate_txt_file=leave_intermediate_txt_file,
                     perform_balance_check=perform_balance_check,
                     output_file_type=output_file_type,
                     reversed_transaction_order=reversed_transaction_order)


input_file_name = "statements/Сбер.pdf"
output_Excel_file_name = 'SBER'
format = "auto"
output_file_type = 'xlsx'
reversed_transaction_order = False
perform_balance_check = True
leave_intermediate_txt_file = True
sberbankPDF2Excel.sberbankPDF2Excel(input_file_name=input_file_name,
                               output_file_name=output_Excel_file_name,
                               format=format,
                               leave_intermediate_txt_file=leave_intermediate_txt_file,
                               perform_balance_check=perform_balance_check,
                               output_file_type=output_file_type,
                               reversed_transaction_order=reversed_transaction_order)