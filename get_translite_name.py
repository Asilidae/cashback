import pandas as pd
import iuliia
import re


def transliteration(name):
    name = re.sub(r'\(|\)|\.ru|_|:|-|\.|,', ' ', name)
    name = name.lower()
    # name = name.replace('.ru', ' ')
    name = name.strip()
    variants_names = [
        # iuliia.ALA_LC.translate(name),
        iuliia.ALA_LC_ALT.translate(name),
        iuliia.BGN_PCGN.translate(name),
        iuliia.BGN_PCGN_ALT.translate(name),
        # iuliia.BS_2979.translate(name),
        iuliia.BS_2979_ALT.translate(name),
        # iuliia.GOST_16876.translate(name),
        iuliia.GOST_16876_ALT.translate(name),
        iuliia.GOST_52290.translate(name),
        iuliia.GOST_52535.translate(name),
        iuliia.GOST_7034.translate(name),
        # iuliia.GOST_779.translate(name),
        iuliia.GOST_779_ALT.translate(name),
        # iuliia.ISO_9_1954.translate(name),
        # iuliia.ISO_9_1968.translate(name),
        # iuliia.ISO_9_1968_ALT.translate(name),
        iuliia.MOSMETRO.translate(name),
        iuliia.MVD_310.translate(name),
        iuliia.MVD_310_FR.translate(name),
        iuliia.MVD_782.translate(name),
        # iuliia.SCIENTIFIC.translate(name),
        iuliia.TELEGRAM.translate(name),
        # iuliia.UNGEGN_1987.translate(name),
        # iuliia.UZ.translate(name),
        iuliia.WIKIPEDIA.translate(name),
        iuliia.YANDEX_MAPS.translate(name),
        iuliia.YANDEX_MONEY.translate(name)
    ]
    # for i, j in enumerate(variants_names):
    #     print(f"{i+1}:\t{j}")
    unique_names = list(set(variants_names))
    return ', '.join(unique_names)



if __name__ == '__main__':
    df = pd.read_excel("app/partners/partners_all.xlsx")
    count_df = df[(df['Количество магазинов партнера'] > 1) | (df['Количество магазинов партнера'] == 0)]
    name_df = count_df[(count_df['Имя партнера'].str.split().str.len() > 1) & (count_df['Имя партнера'].str.split().str.len() < 3)]
    top_df = df[df['Порядковый номер'] < 100]
    df = pd.concat([name_df, top_df])
    df = df.drop_duplicates()
    # print(df)
    df['translite_name'] = df['Имя партнера'].apply(transliteration)

    df.to_excel("filter_2.xlsx")
    # print(transliteration("9 Жизней"))
