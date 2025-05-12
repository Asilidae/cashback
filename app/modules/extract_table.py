from langchain_community.document_loaders import PyMuPDFLoader
import pandas as pd
import re


def clean_statement(text, head_cap):
    match = re.search(head_cap, text)
    if match:
        return text[match.end():].strip()  # Обрезаем текст до заголовка (не включая его)
    return text


def parse_amount(amount_str):
    return float(amount_str
                 .replace('\xa0', '')
                 .replace(' ', '')
                 .replace(',', '.')
                 .replace('–', '-'))


def parse_bank_statement(docs, bank_params):
    text = ''
    for doc in docs:
        text += clean_statement(doc.page_content, bank_params["head_cap"])
    param_groups = bank_params['param_groups']
    data = []
    pattern = re.compile(bank_params["pattern"], re.DOTALL)
    for match in re.finditer(pattern, text):
        groups = match.groups()
        record = {
            'Дата операции': pd.to_datetime(f"{groups[param_groups['Дата операции']]}",
                                            format=bank_params["format_datatime"]),
            'Описание операции': groups[param_groups['Описание операции']],
            'Сумма операции': parse_amount(groups[param_groups['Сумма операции']]),
        }
        if 'Тип операции' in param_groups.keys():
            record['Тип операции'] = groups[param_groups['Тип операции']]
        data.append(record)

    return pd.DataFrame(data)
