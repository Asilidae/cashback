from redis import Redis 
from langchain_community.document_loaders import PyMuPDFLoader
from celery import Celery
from app.utils.file_utils import read_from_s3, delete_from_s3
from app.core.config import settings
import pandas as pd
import json
import os
from app.modules.classification import load_patterns, detect_bank
from app.modules.extract_table import parse_bank_statement
from app.modules.categorization import categorize_transactions
from app.modules.cashback_calculation import cashback_calculation
from app.modules.sber_extract import sberbankPDF2Excel
import tempfile



def preprocess_translite(orig_name, translite_name):
    try:
        parts = translite_name.split(', ')
    except:
        parts = [orig_name]
    return parts


def preprocess_parntners(partners_df):
    first_col = partners_df.columns[2]
    second_col = partners_df.columns[-1]
    # partners = {x: y.split(', ') for x, y in zip(partners_df[first_col], partners_df[second_col])}
    # partners = {x: y for x,y in zip(partners_df[first_col], partners_df[second_col])}
    partners = {x: preprocess_translite(x, y) for x, y in zip(partners_df[first_col], partners_df[second_col])}
    # partners = {x: ast.literal_eval(y) for x,y in zip(partners_df[first_col], partners_df[second_col])}
    # partners = {x: y for x,y in zip(partners_df[first_col], partners_df[second_col])}
    return partners



celery_app = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

redis_client = Redis.from_url(settings.REDIS_URL)  # Инициализация клиента

# Загрузка конфига и партнеров
config = json.load(open('app/config.json', encoding='utf-8'))
partners_df = pd.read_excel('app/partners/filter_2.xlsx')
partners = preprocess_parntners(partners_df)
print("Конфиг загружен")

@celery_app.task(bind=True)
def process_file_task(self, s3_key: str):
    try:

        # Скачиваем файл из S3
        pdf_content = read_from_s3(s3_key)

        # Сохраняем временный файл (т.к. PyMuPDFLoader требует путь)
        # Создаем временную папку (если не существует)
        TEMP_DIR = os.path.join(tempfile.gettempdir(), "cashback_service")
        os.makedirs(TEMP_DIR, exist_ok=True)

        # Генерируем путь к файлу
        temp_pdf_path = os.path.join(TEMP_DIR, s3_key.split('/')[-1])

        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_content)

        # Обработка PDF
        docs = PyMuPDFLoader(temp_pdf_path).load()
        classification_param = load_patterns(filename="app/banks_patterns.json")
        bank_class = detect_bank(docs, classification_param)

        # извлечение таблицы
        if bank_class == 'Sber':
            df = sberbankPDF2Excel.sberbankPDF2Excel(input_file_name=temp_pdf_path)
            default_category = "buy"
            type_transaction_dict = config["type_transaction_sber"]
        else:
            df = parse_bank_statement(docs, config['banks'][bank_class])
            default_category = "Other"
            type_transaction_dict = config["type_transaction"]

        df = categorize_transactions(df=df,
                                     type_transaction_dict=type_transaction_dict,
                                     description_col_index=config["banks"][bank_class]["column_description"],
                                     type_transaction_index=config["banks"][bank_class]["column_type"],
                                     default_category=default_category,
                                     cost_col_index=config["banks"][bank_class]["column_cost"],
                                     category_dict=partners)

        # Расчет кэшбека
        df = cashback_calculation(df=df, name_col="cashback_sub", cashback_params=config["cashback"]["subscribing"])
        df = cashback_calculation(df=df, name_col="cashback_unsub",
                                  cashback_params=config["cashback"]["no_subscription"])

        sum_partners = float(df.loc[df['category'] != 'Other', 'cashback_sub'].sum())
        sum_non_partners = float(df.loc[df['category'] == 'Other', 'cashback_sub'].sum())
        
        # минимальная и максимальная даты
        first_date = df['Дата операции'].min().strftime('%Y-%m-%d') if pd.notnull(df['Дата операции'].min()) else None
        last_date = df['Дата операции'].max().strftime('%Y-%m-%d') if pd.notnull(df['Дата операции'].max()) else None
        
        # Удаление временного файла
        os.unlink(temp_pdf_path)

        response_data = {
            "s3_key": s3_key,
            "bank": bank_class,
            "first_date": first_date,
            "last_date": last_date,
            "transactions_count": len(df),
            "cashback_partners": sum_partners,
            "cashback_non_partners": sum_non_partners
        }
        print(response_data)

        delete_from_s3(s3_key)
        redis_client.setex(
            f"cashback:{s3_key}",  # Ключ
            3600,  # Время жизни (секунд)
            json.dumps(response_data)  # Значение (кэшбэк)
        )
        return response_data
    except Exception as e:
        # В случае ошибки пробуем удалить файл
        try:
            delete_from_s3(s3_key)
        except:
            pass  # Игнорируем ошибки удаления при провале задачи
        finally:
            return {"s3_key": s3_key, "error": str(e)}


