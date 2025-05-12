import logging

# importing own modules out of project
import pandas as pd

from app.modules.sber_extract.extractor import Extractor
import app.modules.sber_extract.utils as utils
import app.modules.sber_extract.extractors as extractors
import app.modules.sber_extract.exceptions as exceptions

from app.modules.sber_extract.extractors_generic import determine_extractor_auto

logger = logging.getLogger()
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def sberbankPDFtext2Excel(file_text: str,
                          format='auto',
                          perform_balance_check=True,
                          reversed_transaction_order=False) -> str:
    """ Функция конвертирует текстовый файл Сбербанка, полученный из выписки PDF в Excel или CSV форматы
        Если output_file_name не задан, то он создаётся из input_txt_file_name путём удаления расширения

    Args:
        input_txt_file_name (str): имя входного текстового файла
        output_file_name (str, optional): имя выходного файла. Defaults to None.
        format (str, optional): формат входного файла. Defaults to 'auto'.
        perform_balance_check (bool, optional): Проводить сверку баланса по трансакциям и по шапке. Defaults to True.
        output_file_type (str, optional): Тип выходного файла. Defaults to 'xlsx'.
        reversed_transaction_order (bool, optional): Изменить порядок трансакций на обратный. Defaults to False.

    Raises:
        exceptions.UserInputError: 

    Returns:
        str: file name of the created file
    """

    extractor_type: type

    if format=='auto':
        extractor_type = determine_extractor_auto(file_text)
        print(r"Формат файла определён как " + extractor_type.__name__)

    # checking whether format is one of the known formats
    else:
        for extractor in extractors.extractors_list:
            if extractor.__name__ == format:
                extractor_type = extractor
                break
        else:
            raise exceptions.UserInputError(f"Задан неизвестный формат {format}")

        print(r"Конвертируем файл как формат " + format)


    # in this case extractor_type is not a function, but a class
    # if you call it like this extractor_type() it returns an object with the type of extractor_type
    actual_extractor: Extractor = extractor_type(file_text)

    # extracting entries (operations) from big text to list of dictionaries
    individual_entries = actual_extractor.get_entries()

    # converting list of dictionaries to pandas dataframe
    df = pd.DataFrame(data = individual_entries,
                      columns=actual_extractor.get_columns_info().keys())


    # getting balance, written in the bank statement
    extracted_balance = actual_extractor.get_period_balance()

    # checking, if balance, extracted from text file is equal to the balance, found by summing column in Pandas dataframe

    error = ""

    try:
        utils.check_transactions_balance(input_pd=df,
                                         balance=extracted_balance,
                                         column_name_for_balance_calculation=actual_extractor.get_column_name_for_balance_calculation())

    except exceptions.BalanceVerificationError as e:
        if perform_balance_check:
            raise
        else:
            print(bcolors.FAIL + str(e) + bcolors.ENDC)
            error = str(e)


    df = utils.rename_sort_df(df = df,
                              columns_info=actual_extractor.get_columns_info())
    
    if reversed_transaction_order:
        df = df.iloc[::-1]  # reversing the order of transactions

    # utils.write_df_to_file(df, output_file_name,
    #                         extractor_name=extractor_type.__name__,
    #                         errors=error,
    #                         output_file_format=output_file_type)

    # print(f"Создан файл {output_file_name}")

    return df