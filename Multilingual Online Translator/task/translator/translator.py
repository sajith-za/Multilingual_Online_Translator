import requests
from bs4 import BeautifulSoup
import re
import sys

# List of language options for translations
lang_list = {1: "Arabic", 2: "German", 3: "English", 4: "Spanish", 5: "French", 6: "Hebrew",
             7: "Japanese", 8: "Dutch", 9: "Polish", 10: "Portuguese", 11: "Romanian", 12: "Russian", 13: "Turkish"}


class NotInLangListError(Exception):
    def __init__(self, lang):
        self.lang = lang

    def __str__(self):
        return "Sorry, the program doesn't support " + self.lang


class InternetConnectionError(Exception):
    def __str__(self):
        return "Something wrong with your internet connection"


class IncorrectWordError(Exception):
    def __init__(self, word):
        self.word = word

    def __str__(self):
        return "Sorry, unable to find " + self.word


def initial_greeting():
    print('Hello, welcome to the translator. Translator supports: ')
    for k, v in lang_list.items():
        print(f'{k}. {v}')

    first = lang_list[int(input('Type the number of your language: '))]
    print('Type the number of a language you want to translate to'
          ' or "0" to translate to all languages: ')
    second = input()
    print('Type the word you want to translate:')
    word = input()
    second = 'all' if second == '0' else lang_list[int(second)]

    processing(first, second, word)


def secondary_greeting():
    args = sys.argv

    if len(args) != 4:
        print("The Multilingual Online Translator script should be called with 3 arguments.")

    else:
        first = args[1]
        second = args[2]
        word = args[3]

        # Testing if the Language specified is in the list of allowable translations
        try:
            if not (first.capitalize() in lang_list.values()):
                raise NotInLangListError(first)

            elif second.lower() != 'all' and not (second.capitalize() in lang_list.values()):
                raise NotInLangListError(second)

            else:
                processing(first, second, word)

        except NotInLangListError as err1:
            print(err1)


def processing(first, second, word):
    if second.lower() != 'all':

        stew = translate(first, second, word)

        with open(word + '.txt', 'w', encoding='utf-8') as f:
            write_station(f, second, stew)

    else:
        with open(word + '.txt', 'w', encoding='utf-8') as f:
            for k in lang_list.values():
                second = k

                if second == first:
                    continue

                stew = translate(first, second, word)
                write_station(f, second, stew)

                if k != "Turkish":
                    # print()
                    f.write('\n\n')

    with open(word + '.txt', 'r', encoding='utf-8') as readfile:
        for line in readfile:
            print(line.strip())


def translate(first, second, word):
    headers = {'User-Agent': 'Mozilla/5.0'}
    var1 = first.lower() + '-' + second.lower() + '/'
    url = 'https://context.reverso.net/translation/' + var1 + word.lower()

    page = requests.get(url, headers=headers)

    try:
        if page.status_code != 200:
            if int(page.status_code) // 500 == 1:
                raise InternetConnectionError
            elif int(page.status_code) // 400 == 1:
                raise IncorrectWordError(word)
        else:
            soup = BeautifulSoup(page.content, 'html.parser')
            return soup

    except InternetConnectionError as err2:
        print(err2)
        exit()

    except IncorrectWordError as err3:
        print(err3)
        exit()


def print_station(lang, soup):
    counter = 0
    limit = 1

    # print()
    print(f'{lang} translations:')

    for element in retrieve_list(soup, "display-term"):
        print(element)
        counter += 1
        if counter == limit:
            counter = 0
            break

    print()
    print(f'{lang} examples:')
    variable = 'trg rtl arabic' if lang == 'Arabic' else \
        ('trg rtl' if lang == 'Hebrew' else 'trg ltr')

    for a, b in zip(retrieve_list(soup, "src ltr"), retrieve_list(soup, variable)):

        new_b = re.sub(r"[«]", "", b)
        print(a + '\n' + new_b)
        counter += 1

        if counter == limit:
            break

        print()


def write_station(f, lang, soup):
    counter = 0
    limit = 20

    f.write(f'{lang} translations:' + '\n')

    for element in retrieve_list(soup, "display-term"):
        f.write(element + '\n')
        counter += 1
        if counter == limit:
            counter = 0
            break

    f.write('\n')
    f.write(f'{lang} examples:' + '\n')
    variable = 'trg rtl arabic' if lang == 'Arabic' else \
        ('trg rtl' if lang == 'Hebrew' else 'trg ltr')

    for a, b in zip(retrieve_list(soup, "src ltr"), retrieve_list(soup, variable)):

        f.write(a + '\n' + b)
        counter += 1

        if counter == limit:
            break

        # f.write('\n')


def retrieve_list(soup, class_type):
    sample_list = []
    translates = soup.find_all(class_=class_type)

    for p in translates:
        sample_list.append(p.text.strip())

    return sample_list


if __name__ == '__main__':
    secondary_greeting()
