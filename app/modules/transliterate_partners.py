from transliterate import detect_language, translit
import re
from itertools import product
import pandas as pd
from tqdm import tqdm


def recursive_replace(current_word, replacements, index=0):
    if index >= len(current_word):
        return [current_word]

    char = current_word[index]
    results = []

    # Если символ есть в replacements, добавляем варианты замен
    if char in replacements:
        for replacement in replacements[char]:
            new_word = current_word[:index] + replacement + current_word[index + 1:]
            results.extend(recursive_replace(new_word, replacements, index + len(replacement)))
    else:
        results.extend(recursive_replace(current_word, replacements, index + 1))

    return results


def generate_variations(word):
    # variations = set()

    # Основные варианты замен
    replacements = {
        'ё': ['е', 'yo'],
        'е': ['e', 'ye'],
        'ж': ['j', 'zh'],
        'и': ['i', 'y'],
        'й': ['i', 'y'],
        'щ': ['shh', 'sch'],
        'я': ['ya', 'ia'],
        'ю': ['yu', 'iu'],
        'ь': ['', '\''],
        'ъ': ['', '\''],
        '-': ['', ' ', '_'],
        '_': ['', ' ', '-']
    }

    return list(set(recursive_replace(word, replacements)))


def traslite(component):
    variants = set()
    for word in component:
        if word.isdigit():
            continue

        # Определение языка
        lang = detect_language(component)

        try:
            if lang == 'ru':
                translit_en = translit(word, 'ru', reversed=True)
                variants.add(translit_en)
                variants.add(translit_en.replace(' ', ''))
            else:
                variants.add(word)
                variants.add(word.replace(' ', ''))
        except:
            pass
    return variants


def generate_combinations(components, separators):
    if not components:
        return set()

    combinations = set()

    for parts in product(*components):
        for sep in separators:
            combined = sep.join(parts)
            combinations.add(combined)

    return combinations


def process_partner(name):
    # if len(name.split()) > 2: return name
    name = name.lower()
    original = re.sub(r'[^\w\s-]', '', str(name)).strip()
    components = re.split(r'[\s\-_]+', original)
    components = [generate_variations(component) + [component] for component in components]

    # Генерация языковых вариантов
    all_components = []
    for component in components:
        all_components.append(traslite(component))

    combined_variations = generate_combinations(all_components, separators=['', ' '])

    # return sorted(combined_variations)
    return ', '.join(combined_variations)


# # Пример использования
# partners = [
#     "ВОЯЖ-сервис",
#     # "ULTRAMOBILE",
#     "Тесла",
#     "Лакра",
#     # "Mobile Rybinsk"
# ]
#
# partner_keywords = {partner: process_partner(partner) for partner in partners}
#
# # Вывод для первых 5 партнеров
# for k, v in list(partner_keywords.items())[:5]:
#     print(f"{k}:")
#     print(', '.join(v))
#     print()

if __name__ == '__main__':
    tqdm.pandas()
    df = pd.read_excel('partners/partners10.xlsx')
    df['translite_name'] = df['Имя партнера'].progress_apply(process_partner)
    df.to_excel('partners/traslite_name10.xlsx')
