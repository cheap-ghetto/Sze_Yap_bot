import pandas as pd
import re
import unidecode
from os.path import join, dirname
from datetime import datetime
filepath = dirname(__file__)
hed = pd.read_csv(join(filepath, 'HED Alphabetical 20200622.csv'), 
                  low_memory=False)
time_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

accent_to_tone = {
    '\u0304': '55',
    '\u0308': '33',
    '\u0342': '22',
    '\u0300': '32',
    '\u0302': '21'
}

tone_to_accent_dict = {
    "55": '\u0304',
    "33": '\u0308',
    "22": '\u0342',
    "32": '\u0300',
    "21": '\u0302'
}

vowels = ('a', 'e', 'i', 'o', 'u')
pinyin_regex = r'[\u00C0-\u024FẼẽ]|m̃|M̃|M̂|m̂|M̈|m̈|M̄|m̄|M̀|m̀'
chinese_charset = r'\u4e00-\u9fff\u3400-\u4DBF\u4E00-\u9FCC'


def search_string_format(search_string):
    return " " + " ".join(search_string.split()) + " "

def remove_format(string):
        return re.sub(r'[⁰¹²³⁴⁵⁶⁷⁸⁹]|\<wr\.\>\s|<又>\s|<台>\s', '', string)

def hed_index(word):
    columns = ["繁", "简", "台拼", "汉拼"]

    search_table = pd.DataFrame()
    search_indices = []

    for column in columns:
        find_match = hed[hed[column] == word]
        if not find_match.empty:
            print("Found match!")
            search_table = find_match
            search_indices = find_match.index.tolist()
            break
    if len(search_table) == 0:
        return None, None
    else:
        return search_indices, search_table


def hed_usage(index):
    index += 1
    counter = 0
    if (index + counter) > 80565:
        return hed["英译与词句"].iloc[
            range(index, index + counter)].dropna().tolist()
    else:
        while pd.isna(hed["繁"].iloc[index + counter]):
            counter += 1
        if counter == 0:
            return ["None"]
        else:
            return hed["英译与词句"].iloc[
                range(index, index + counter)].dropna().tolist()


def hed_translate_all(word_phrase):
    return hed[hed["英译与词句"].str.contains(
        pat=word_phrase.lower(), regex=False, na=False)]


def hed_translate_from_chinese(chinese_word):
    definition_indices = []
    for index in hed[hed["英译与词句"].str.contains(
            pat=chinese_word, regex=False, na=False)].index:

        while pd.isna(hed["繁"].iloc[index]):
            index -= 1
        if index not in definition_indices:
            definition_indices.append(index)
    print(hed.iloc[definition_indices, :])
    return hed.iloc[definition_indices, :]

# Start of new section


def single_chinese(chinese_word):
    search_result = hed[hed['繁'].str.contains(
        pat=chinese_word, regex=False, na=False)]
    if search_result.empty:
        search_result = hed[hed['简'].str.contains(
        pat=chinese_word, regex=False, na=False)]
    return search_result


def simple_chinese(chinese_word):
    return hed[hed['简'].str.contains(
        pat=chinese_word, regex=False, na=False)]


def multi_chinese(chinese_word):
    return hed[hed['英译与词句'].str.contains(
        pat=chinese_word, regex=False, na=False)]


def pinyin(pinyin_word):
    return hed[hed['p.y.'].str.contains(pinyin_word, na=False)]


def hed_translate_mean_only(word_phrase):
    word_phrase = f"\\b{word_phrase}\\b"
    return hed[(hed["繁"].notna()) & (hed["英译与词句"].str.contains(
        pat=word_phrase, case=False, regex=True, na=False))]


macron = ['Ā', 'Ē', 'Ī', 'Ō', 'Ū', 'ā', 'ē', 'ī', 'ō', 'ū', 'm̃', 'm̃']
diaeresis = ['Ä', 'Ë', 'Ï', 'Ö', 'Ü', 'ä', 'ë', 'ï', 'ö', 'ü', 'M̈', 'm̈']
tilde = ['Ã', 'Ẽ', 'Ĩ', 'Õ', 'Ũ', 'ã', 'ẽ', 'ĩ', 'õ', 'ũ', 'M̃', 'm̃']
grave_accent = ['À', 'È', 'Ì', 'Ò', 'Ù', 'à', 'è', 'ì', 'ò', 'ù', 'M̀', 'm̀']
circumflex = ['Â', 'Ê', 'Î', 'Ô', 'Û', 'â', 'ê', 'î', 'ô', 'û', 'M̂', 'm̂']

def process_defn(search_result):
    for search_index, row in search_result.iterrows():
        if str(row['繁']) == "nan":
            string = remove_format(row['英译与词句'])
            try:
                pinyin = re.search(
                    r'(^[\u4e00-\u9fff\u3400-\u4DBF\u4E00-\u9FCC\[\],.]+)(( or |\s)([\u4e00-\u9fff\u3400-\u4DBF\u4E00-\u9FCC\[\]]+)|((?: or |\s|-)[a-zA-Z]{0,3}(?:[\u00C0-\u024FẼẽ]|m̃|M̃|M̂|m̂|M̈|m̈|M̄|m̄|M̀|m̀)+[^\s]+))+',
                    string).group(0).replace(', ', ',').split(' ')
            except AttributeError:
                print(f'{time_string}: Error on {string}')
                continue
            string = re.sub(
                r'(^[\u4e00-\u9fff\u3400-\u4DBF\u4E00-\u9FCC\[\],.]+)(( or |\s)([\u4e00-\u9fff\u3400-\u4DBF\u4E00-\u9FCC\[\]]+)|((?: or |\s|-)[a-zA-Z]{0,3}(?:[\u00C0-\u024FẼẽ]|m̃|M̃|M̂|m̂|M̈|m̈|M̄|m̄|M̀|m̀)+[^\s]+))+',
                "$", string)
            string = re.search(r'(?<=\$\s)[^\$]+$', string)
            if string is None:
                print(f'Error on {row["英译与词句"]}')
                continue
            else:
                string = string.group(0)
            chinese_chars = []
            penyum = []
            mando = []

            for index, word in enumerate(pinyin):
                if re.search(rf'[{chinese_charset}]',
                             word):
                    chinese_chars.append(word)
                elif re.search(rf'{pinyin_regex}', word):
                    penyum.append(word)
                    try:
                        if "or" in pinyin[index+1]:
                            pass
                        elif re.search(rf'{pinyin_regex}',
                                       pinyin[index+1]):
                            while index < len(pinyin)-1 and \
                                    "or" not in pinyin[index+1]:
                                mando.append(pinyin[index+1])
                                index += 1
                        if index >= len(pinyin)-1:
                            break
                    except IndexError:
                        pass
            search_result.at[search_index, '台拼'] = " or ".join(penyum)
            num_penyum = penyum
            for word_index, pin_phrase in enumerate(
                    [word.split("-") for word in num_penyum]):
                for pin_index, pin in enumerate(pin_phrase):
                    special_char = re.search(rf"{pinyin_regex}", pin)
                    if special_char is None:
                        print(f"error on {pin}")
                    special_char = special_char.group(0)
                    if special_char in macron:
                        pin += "1"
                    elif special_char in diaeresis:
                        pin += "2"
                    elif special_char in tilde:
                        pin += "3"
                    elif special_char in grave_accent:
                        pin += "4"
                    elif special_char in circumflex:
                        pin += "5"
                    pin_phrase[pin_index] = unidecode.unidecode(pin)
                num_penyum[word_index] = "-".join(pin_phrase)

            search_result.at[search_index, '繁'] = " or ".join(chinese_chars)
            search_result.at[search_index, '汉拼'] = " ".join(mando)
            
            search_result.at[search_index, 'p.y.'] = " or ".join(num_penyum)
            search_result.at[search_index, '英译与词句'] = string
    return search_result


def num_to_accent(input_string):
    return_list = []
    items = [phrase.groups() for phrase in re.finditer(r"([a-z]+)([0-9]+)\b",
                                                       input_string, re.I)]
    for word_num in items:
        positions = [index+1 for index, char in enumerate(
            word_num[0]) if char in vowels]
        if len(positions) > 1:
            return_list.append(word_num[0][:(positions[-2])] +
                               tone_to_accent_dict[word_num[1]] +
                               word_num[0][positions[-2]:])
        else:
            return_list.append(word_num[0][:(positions[0])] +
                               tone_to_accent_dict[word_num[1]] +
                               word_num[0][positions[0]:])
    return " ".join(return_list)




def single_multi_search(eng_word):
    eng_word = f"\\b{eng_word}\\b"
    search_result = hed[hed["英译与词句"].str.contains(
        pat=eng_word, case=False, regex=True, na=False)]
    return process_defn(search_result)


def rand_word():
    return process_defn(hed[(hed['英译与词句'].str.len() > 30)].sample(2))
