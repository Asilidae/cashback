import re

def find_type(description, category_dict, default_category="Other"):
    for category, phrases in category_dict.items():
        if any(phrase.lower() in description.lower() for phrase in phrases):
            return category
    return default_category


def clean_text(text):
    # Удаляем символы переноса строки и дефисы
    cleaned_text = re.sub(r'[-*.,_\r\n]', ' ', text)
    cleaned_text = cleaned_text.replace('\\n', ' ')
    return cleaned_text


def is_phrase_in_tokens(phrase, tokens):
    phrase_words = phrase.lower().split()  # Разбиваем фразу на слова
    phrase_len = len(phrase_words)

    # Ищем подпоследовательность в токенах
    for i in range(len(tokens) - phrase_len + 1):
        if tokens[i:i + phrase_len] == phrase_words:
            return True
    return False


def find_category(text, category_dict, default_category="Other"):
    cleaned_text = clean_text(text).lower()
    tokens = cleaned_text.split()  # Токены разбиты по пробелам
    # print(cleaned_text)
    # print("\n")
    # Поиск совпадений с темами
    labels = []
    for theme, phrases in category_dict.items():
        for phrase in phrases:
            if is_phrase_in_tokens(phrase, tokens):
                labels.append(theme)
                break  # Если нужна только одна метка на тему

    if labels:
        return list(set(labels))
    else:
        return default_category


def categorize_transactions(df,
                            type_transaction_dict,
                            description_col_index,
                            type_transaction_index,
                            default_category,
                            cost_col_index,
                            category_dict):
    description_col = df.columns[description_col_index]
    type_col = df.columns[type_transaction_index]
    cost_col = df.columns[cost_col_index]
    df["type_transaction"] = df[type_col].apply(
        lambda description: find_type(description, type_transaction_dict, default_category))
    df["category"] = df[description_col].apply(lambda description: find_category(description, category_dict))
    df["cost"] = df[cost_col].astype(str).str.replace("[+-]", "", regex=True).astype(float)
    return df