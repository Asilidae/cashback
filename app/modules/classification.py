from langchain_community.document_loaders import PyMuPDFLoader
import glob
import json


def load_patterns(filename="banks_patterns.json"):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_bank(docs, patterns):
    context = docs[0].page_content
    if len(context) > 1:
        context += docs[-1].page_content
    for bank, keywords in patterns.items():
        if any(keyword in context for keyword in keywords):
            return bank
    return "Неизвестный банк"


if __name__ == "__main__":
    patterns = load_patterns()
    docs_name = glob.glob("statements/*.pdf")

    for doc in docs_name:
        loader = PyMuPDFLoader(
            doc
        ).load()
        # with open(f"{doc[:-4]}.txt", "w", encoding="utf8") as file:
        #     file.write(context)

        result = detect_bank(loader, patterns)
        print(f"{doc}: {result}")
