# -*- coding: UTF-8 -*-

import os,re,codecs

def main():
    phrase = 'коллинеарными векторами'
    dic_file = os.path.join( os.path.dirname(__file__), r"math_phys_rus-flx.dic")
    res = MorphoAnalyzer(dic_file, 'rus')

    [canonical_variants, phrase, word_template_string] = res.normalize(phrase.lower())
    lemmas = [res.words2lemmas_dict.get(elem.lower(), ["NO_LEMMA"])[0] for elem in phrase.lower().split(" ")]
    print([canonical_variants, lemmas, phrase, word_template_string])
class MorphoAnalyzer():
    def __init__(self, filename, lang = "rus"):
        self.filename = filename
        self.parts_of_speech = ["N", "V", "A", "ADJ", "PPL", "PREP", "CONJC", "ADV", "INTERJ", "PRO"]

        if lang == 'rus':
            self.normal_templates = self.get_rus_canonical_templates()
        else:
            self.normal_templates = self.get_eng_canonical_templates()

        self.words2lemmas_dict = {}

        self.lemmas_grams = {}

        self.word_splitter = re.compile(r"\s+")
        [words2lemmas_dict, lemmas_grams] = self.read_dict()

        if len(words2lemmas_dict) and len(lemmas_grams):
            self.lemmas_grams = lemmas_grams
            self.words2lemmas_dict = words2lemmas_dict
        a = 1

    def normalize(self, phrase):
        try:
            split_phrase = re.split(self.word_splitter, phrase.lower())
            word_template = []

            for word in split_phrase:
                if word.endswith(","):
                    part_of_speech = self.get_part_of_speech(word[:-1])
                else:
                    part_of_speech = self.get_part_of_speech(word)
                word_template.append(part_of_speech)

            word_template_string = "+".join(word_template)


            cur_templates = self.normal_templates.get(word_template_string, None)

            if cur_templates is None:

                return [ ["Укажи шаблон в MorphologyLibruary !!! :( -> {0}".format( word_template_string ) ], phrase, word_template_string]

            cur_templates_with_gender = self.update_cur_templates(cur_templates, split_phrase, word_template_string)

            if len(cur_templates_with_gender) == 0:
                return [ ["Что-то не так с MorphologyLibruary.update_cur_templates -> {0}".format( word_template_string )],  phrase, word_template_string]

            canonical_variants = []
            for extra_params, canonical_form in cur_templates_with_gender:
                new_canon = []

                extra_condition = self.parse_extra_condition(extra_params, word_template)
                res_form = "IMPOSSIBLE_TO_GET_CANONICAL"
                if len(extra_condition) == 0:
                    #нет доп. условий
                    res_form = self.phrase_converter(split_phrase, canonical_form, word_template, word_template_string)
                else:
                    is_matched = self.check_extra_condition(split_phrase, extra_condition, word_template)
                    if not is_matched:
                        continue
                    res_form = self.phrase_converter(split_phrase, canonical_form, word_template, word_template_string)
                    a = 1
                canonical_variants.append(res_form)

            if word_template_string == "N+PPL+PREP+N":
                canonical_variants = [[el for el in elem.split()] for elem in canonical_variants]
                for i in range(len(canonical_variants)):
                    canonical_variants[i] = [canonical_variants[i][0]+","]+canonical_variants[i][1:]

                canonical_variants = [" ".join(elem) for elem in canonical_variants]
                a = 1
            return canonical_variants, phrase, word_template_string
            a = 1
        except Exception as err:
            print('normalize -> {0}'.format(err))

    def phrase_converter(self, split_phrase, canonical_form, word_template, word_template_string):
        try:
            canonical_variant = []
            canonical_array = []
            for i in range( len(split_phrase) ):

                cur_word = split_phrase[i]
                cur_canonical = canonical_form[i]
                #print(split_phrase[i])
                canon_variants = []
                if len([elem for elem in cur_canonical if elem.find("word=") != -1]) :
                    canon_variants.append([cur_word, cur_canonical])
                else:
                    if cur_word.endswith(","):
                        lemmas = self.words2lemmas_dict.get(cur_word[:-1].lower(), [])
                        if not len(lemmas):
                            lemmas = self.words2lemmas_dict.get(cur_word.lower().title(), [])
                    else:
                        lemmas = self.words2lemmas_dict.get(cur_word.lower(), [])
                        if not len(lemmas):
                            lemmas = self.words2lemmas_dict.get(cur_word.lower().title(), [])

                    for lemma in lemmas:
                        paradygm = self.lemmas_grams[lemma]

                        for para_word, grammar in paradygm.items():
                            #print(para_word)

                            grammar_variants = [elem.split("+") for elem in grammar if set(cur_canonical).issubset( set([el for el in elem.split("+")]) )]


                            if len(grammar_variants):
                                if "Prop" in grammar_variants:
                                    canon_variants.append([para_word.title(), grammar_variants])
                                else:
                                    canon_variants.append([para_word, grammar_variants])
                canonical_variant.append(canon_variants)
            #извлекаю слова
            res_canonical = []
            for variant_rasbora in canonical_variant:
                various_words = {}
                try:

                    for word, grammar in variant_rasbora:
                        various_words[word] = 1
                        a = 1
                    res_canonical.append([el for el in various_words.keys()][0])
                except Exception as err:
                    print(err)
                    res_canonical.append('')
            return " ".join(res_canonical)
        except Exception as err:
            print("phrase_converter -> {0}".format(err))
    def update_cur_templates(self, cur_templates, split_phrase, word_template):
        try:
            new_templates = []
            if word_template == "ADJ+N":
                #так как сущ второе
                noun_gramm = self.get_gramm_info(split_phrase[1])
                genders = self.get_genders(noun_gramm)
                if not len(genders):
                    #Заглушка, если род не найден, то ставлю мужской....
                    genders = ['m']
                for extra_param, templates in cur_templates:
                    new_templates.append([str(extra_param), [templates[0][:]+[genders[0]], templates[1][:]+[genders[0]] ]])
            elif word_template == "ADJ+N+N":
                #так как сущ второе
                noun_gramm = self.get_gramm_info(split_phrase[1])

                noun_gram1 = self.get_gramm_info(split_phrase[2])

                genders_first = self.get_genders(noun_gramm)

                gender_second = self.get_genders(noun_gram1)
                #number_second = self.get_number(noun_gram1)
                if not len(genders_first):
                    #Заглушка, если род не найден, то ставлю мужской....
                    genders_first = ['m']

                if not len(gender_second):
                    #Заглушка, если род не найден, то ставлю мужской....
                    gender_second = ['m']

                for extra_param, templates in cur_templates:
                    new_templates.append([str(extra_param), [templates[0][:]+[genders_first[0]], templates[1][:]+[genders_first[0]], templates[2][:]+[gender_second[0]] ]])

            elif word_template == "ADJ+ADJ+N":
                #так как сущ третье
                noun_gramm = self.get_gramm_info(split_phrase[2])
                genders = self.get_genders(noun_gramm)
                if not len(genders):
                    #Заглушка, если род не найден, то ставлю мужской....
                    genders = ['m']
                for extra_param, templates in cur_templates:
                    new_templates.append([str(extra_param), [templates[0][:]+[genders[0]], templates[1][:]+[genders[0]], templates[2][:]+[genders[0]] ]])
            elif word_template == "N+N":
                #шаблон описанный извне менять не надо, так как согласовывать не нужно
                new_templates = cur_templates
            elif word_template == "N+N+ADJ+N":
                #согласовываем только группу ADJ + N. Остальное. Четвертое существительное
                 #так как сущ второе
                third_noun_gramm = self.get_gramm_info(split_phrase[1])
                forth_noun_gramm = self.get_gramm_info(split_phrase[3])

                forth_genders = self.get_genders(forth_noun_gramm)
                forth_numbers = self.get_number(forth_noun_gramm)

                number_second = self.get_number(third_noun_gramm)
                if not len(forth_genders):
                    #Заглушка, если род не найден, то ставлю мужской....
                    forth_genders = ['m']
                for extra_param, templates in cur_templates:
                    new_templates.append([str(extra_param), [templates[0][:], templates[1][:]+[number_second[0]], templates[2][:]+[forth_genders[0], forth_numbers[0]], templates[3][:]+[forth_genders[0], forth_numbers[0]] ]])
            elif word_template == "N+PPL+PREP+N":
                #"N+PPL+PREP+N": [
                #['', [["nom", "sg"], ["nom", "sg"], [], []]]
                #так как сущ первое
                noun_gramm = self.get_gramm_info(split_phrase[0])
                genders = self.get_genders(noun_gramm)

                if not len(genders):
                    #Заглушка, если род не найден, то ставлю мужской....
                    genders = ['m']

                for extra_param, templates in cur_templates:
                    new_templates.append([str(extra_param), [templates[0][:]+[genders[0]], templates[1][:]+[genders[0]], templates[2][:], templates[3][:]+['word={0}'.format(split_phrase[3])] ]])
                #new_templates = cur_templates
            elif word_template == "ADJ+N+PREP+N":
                for extra_param, templates in cur_templates:
                    new_templates.append([str(extra_param), [templates[0][:], templates[1][:], templates[2][:], templates[3][:]+['word={0}'.format(split_phrase[3])] ]])

            elif word_template == "N+N+PREP+N":

                #для последнего слова получаю род, число и падеж

##                noun_gramm = self.get_gramm_info(split_phrase[3])
##                genders = self.get_genders(noun_gramm)
##                numbers = self.get_number(noun_gramm)
##                cases = self.get_case(noun_gramm)

##                if not len(genders):
##                    #Заглушка, если род не найден, то ставлю мужской....
##                    genders = ['m']

                for extra_param, templates in cur_templates:
                    new_templates.append([str(extra_param), [templates[0][:], templates[1][:], templates[2][:], templates[3][:]+['word={0}'.format(split_phrase[3])] ]])
            elif word_template == "ADJ+N+PREP+ADJ+N":
                #new_templates = cur_templates
                #так как сущ второе
                noun_gramm = self.get_gramm_info(split_phrase[1])
                genders = self.get_genders(noun_gramm)

##                second_gram = self.get_gramm_info(split_phrase[4])
##                sec_genders = self.get_genders(second_gram)
##                sec_number = self.get_number(second_gram)
##                sec_case = self.get_case(second_gram)
                if not len(genders):
                    #Заглушка, если род не найден, то ставлю мужской....
                    genders = ['m']


                for extra_param, templates in cur_templates:
                    new_templates.append([str(extra_param), [templates[0][:]+[genders[0]], templates[1][:]+[genders[0]], templates[2][:], templates[3][:]+['word={0}'.format(split_phrase[3])] , templates[4][:]+['word={0}'.format(split_phrase[4])]  ]])
            elif word_template == "N+N+N":
                try:
                    second_gram = self.get_gramm_info(split_phrase[1])
                    third_gram = self.get_gramm_info(split_phrase[2])

                    second_gender = self.get_genders(second_gram)
                    third_gender = self.get_genders(third_gram)

                    second_number = self.get_number(second_gram)
                    third_number = self.get_number(third_gram)

                    for extra_param, templates in cur_templates:
                        new_templates.append([str(extra_param), [templates[0][:], templates[1][:]+[second_gender[0], second_number[0]], templates[2][:] + [ third_gender[0], third_number[0] ] ]])
                except Exception as err:
                    print(err)
            elif word_template == 'N+ADJ+N':
                third_gram = self.get_gramm_info(split_phrase[2])

                third_number = self.get_number(third_gram)
                third_gender = self.get_genders(third_gram)

                for extra_param, templates in cur_templates:
                    new_templates.append([str(extra_param), [templates[0][:], templates[1][:]+[third_number[0], third_gender[0]], templates[2][:] + [ third_number[0], third_gender[0] ] ]])
            elif word_template == "N":
                #шаблон описанный извне менять не надо, так как согласовывать не нужно
                new_templates = cur_templates
            else:
                new_templates = cur_templates
            return new_templates
        except Exception as err:
            print("update_cur_templates -> {0}".format(err))
    def get_case(self, grams):
        genders_hash = {}
        for gram_for_lemma in grams:
            for elem in gram_for_lemma:
                genders = [el for el in elem if el in ['nom', 'gen', 'dat', 'acc', 'ins', 'loc']]
                for el in genders:
                    genders_hash[el] = genders_hash.get(el, 0) + 1
        return [el for el in genders_hash.keys()]
    def get_number(self, grams):
        genders_hash = {}
        for gram_for_lemma in grams:
            for elem in gram_for_lemma:
                genders = [el for el in elem if el in ['sg', 'pl', 's', 'p']]
                for el in genders:
                    genders_hash[el] = genders_hash.get(el, 0) + 1
        return [el for el in genders_hash.keys()]
    def get_genders(self, grams):
        try:
            genders_hash = {}

            for gram_for_lemma in grams:
                for elem in gram_for_lemma:
                    genders = [el for el in elem if el in ['m', 'f', 'n']]
                    for el in genders:
                        genders_hash[el] = genders_hash.get(el, 0) + 1
            return [el for el in genders_hash.keys()]
        except Exception as err:
            print("get_genders -> {0}".format(err))
            return []
    def get_gramm_info(self, word):
        '''
        возвращает массив с вариантами разбора слова
        '''
        try:
            lemmas = self.words2lemmas_dict.get(word.lower(), [])
            if not len(lemmas):
                lemmas = self.words2lemmas_dict.get(word.lower().title(), [])

            cur_parts_of_speech = []

            outpt = []
            for lemma in lemmas:
                gram_info = [elem.split("+") for elem in self.lemmas_grams[lemma].get(word.lower(), self.lemmas_grams[lemma].get(word.lower().title(), []))]
                outpt.append(gram_info)
            return outpt
        except Exception as err:
            print("get_gramm_info -> {0}".format(err))
    def get_part_of_speech(self, word):
        '''
        Возвращает строчку с возможными частями речи. Разделитель |
        '''
        try:
            lemmas = self.words2lemmas_dict.get(word.lower(), [])
            if not len(lemmas):
                lemmas = self.words2lemmas_dict.get(word.lower().title(), [])

            cur_parts_of_speech = []

            for lemma in lemmas:
                try:
                    cur_part_of_speech = u"|".join( [el for el in dict([(elem.split("+")[0], 1) for elem in self.lemmas_grams[lemma][word.lower()]]).keys()] )
                except Exception as err:
                    cur_part_of_speech = u"|".join( [el for el in dict([(elem.split("+")[0], 1) for elem in self.lemmas_grams[lemma][word.lower().title()]]).keys()] )
                cur_parts_of_speech.append(cur_part_of_speech)
            return u"|".join( cur_parts_of_speech )
        except Exception as err:
            print("get_part_of_speech -> {0}".format(err))
            return u"ERROR_get_part_of_speech->{0}".format(err)
    def check_extra_condition(self, split_phrase, extra_condition, word_template):
        try:
            res_boolean_array = [False for i in range(len(split_phrase))]

            for i in range(len(split_phrase)):
                cur_word = split_phrase[i]
                cur_conditions = extra_condition[i]
                cur_pos = word_template[i]

                if len(cur_conditions) == 0:
                    res_boolean_array[i] = True
                    continue
                lemmas = self.words2lemmas_dict.get(cur_word.lower(), [])

                if not len(lemmas):
                    lemmas = self.words2lemmas_dict.get(cur_word.lower().title(), [])

                good_lemmas = []

                for lemma in lemmas:
                    try:
                        gram_info = [el for el in [elem.split("+") for elem in self.lemmas_grams[lemma][cur_word.lower()]] if cur_pos in el]
                    except Exception as err:
                        gram_info = [el for el in [elem.split("+") for elem in self.lemmas_grams[lemma][cur_word.lower().title()]] if cur_pos in el]
                    #в all_flags хранятся инфа, подходит грамматический разбор или нет варианты грамматического разбора
                    all_flags = []
                    for cur_gram_info in gram_info:
                        flags = []
                        for condition1 in cur_conditions:
                            if condition1.startswith("^"):
                                if condition1[1:] not in cur_gram_info:
                                    flags.append(True)
                                else:
                                    flags.append(False)
                            else:
                                if condition1 in cur_gram_info:
                                    flags.append(True)
                                else:
                                    flags.append(False)
                        flags = [el for el in dict([(elem, 1) for elem in flags]).keys()]
                        if not False in flags:
                            all_flags.append(True)
                        else:
                            all_flags.append(False)
                    #условие выполнено, если
                    if True in all_flags:
                        good_lemmas.append(lemma)
                if len(good_lemmas):
                    res_boolean_array[i] = True
            if False in res_boolean_array:
                return False
            else:
                return True
        except Exception as err:
            print("check_extra_condition ->{0}".format(err))
            return False
    def parse_extra_condition(self, condition, word_template):
        '''
        Возвращает массив массивов. Каждый подмассив содержит массив строк. Каждая строка - дополнительный параметр
        '''
        if not len(condition):
            #если условия нет, то возвращаюпустую строку
            return []
        conditions = [elem.split("=") for elem in condition.split("+")]

        if len(conditions) != len(word_template):
            return []
        outpt_array = []
        for i in range(len(word_template)):
            if conditions[i] == "":
                outpt_array.append([])
                continue
            if conditions[i][0] == word_template[i]:
                extra_cond = conditions[i][1].split(",")
                outpt_array.append(extra_cond)
            else:
                outpt_array.append([])
        return outpt_array
    def check_grammar_conditions(self, cur_words, template_to_check, gram_conditions):
        try:
            if not len(gram_conditions):
                #Если условий нет, то строка соответствует шаблону
                return True

            gram_conditions_array = [[el.split(".") for el in elem.split("=")] for elem in gram_conditions]

            grammar_infos = [self.get_gramm_info(elem) for elem in cur_words]

            for cur_gram_cond in gram_conditions_array:
                try:
                    if cur_gram_cond[0][1] == 'gender':
                        numbers_of_characteristic = [int(elem[0]) for elem in cur_gram_cond if elem[1] == 'gender']
                        genders = [self.get_genders(grammar_infos[elem]) for elem in numbers_of_characteristic]

                        if not len( set(genders[0]).intersection(genders[1]) ):
                            return False
                    elif cur_gram_cond[0][1] == 'number':
                        numbers_of_characteristic = [int(elem[0]) for elem in cur_gram_cond if elem[1] == 'number']
                        numbers = [self.get_number(grammar_infos[elem]) for elem in numbers_of_characteristic]

                        if not len( set(numbers[0]).intersection(numbers[1]) ):
                            return False
                    elif cur_gram_cond[0][1] == 'case':
                        numbers_of_characteristic = [int(elem[0]) for elem in cur_gram_cond if elem[1] == 'case']
                        cases = [self.get_case(grammar_infos[elem]) for elem in numbers_of_characteristic]

                        if not len( set(cases[0]).intersection(cases[1]) ):
                            return False
                except Exception as err:
                    print("loop check_gram_exceptions -> {0}".format( err ) )
                a = 1
            return True
        except Exception as err:
            print("check_grammar_conditions_err -> {0}".format(err))
    def read_dict(self):
        try:
            words2lemmas_dict = {}
            lemmas_grams = {}
            fh = None
            fh = codecs.open(self.filename, "r", encoding="utf8")

            for line in fh:
                line = line.strip()

                #получаю слово, лемму, грамматику для слова
                splt = line.split(",")
                if len(splt) != 3:
                    continue

                word = splt[0]
                lemma = splt[1]
                grammar = splt[2]

                if not word in words2lemmas_dict:
                    words2lemmas_dict[ splt[0] ] = []

                if not lemma in lemmas_grams:
                    lemmas_grams[ splt[1] ] = {}

                if not splt[1] in words2lemmas_dict[ splt[0] ]:
                    words2lemmas_dict[ splt[0] ].append( splt[1] )

                if not word in lemmas_grams[lemma]:
                    lemmas_grams[lemma][word] = []

                if not grammar in lemmas_grams[lemma][word]:
                    lemmas_grams[lemma][word].append(grammar)
        except Exception as err:
            print( 'MorphoAnalyzer.read_file -> {0}'.format(err) )
        finally:
            if fh is not None:
                fh.close()
            return words2lemmas_dict, lemmas_grams
    def get_eng_canonical_templates(self):
        '''
        возвращает словарь с шаблонами канонической формы
        '''
        return {
        	"A+N": [
                ["A=Bin+", [["p"], ["p"]]],
                ["A=^Bin+", [["s"], ["s"]]]
            ],
        	"A+N+N": [
                ["", [["s"], ["s"], ["s"]]]
            ],
            "N": [
                ["", ["s"]]
            ],
        	"A+A+N": [
                ['', [[], [], ["s"]]]
            ],
        	"N+N": [
             ["N=Pos", [["Prop"], ["s"]]],
             ["N=^Pos", [[], ["s"]]]
            ],
        	"N+N+A+N": [
                ['', [["s"], [], [], []]]
            ],
        	"N+PPL+PREP+N": [
                ['', [["s"], [], [], []]]
            ],
        	"A+N+PREP+N": [
                ['', [[""], ["s"], [], []]]
            ],

        	"N+N+PREP+N": [
                ['', [[], [], [], []]]
            ],
           	"N+PPL+PREP+A+N": [
                ['', [[], [], [], [], ["s"]]]
            ],
            "N+PPL+PREP+N+N": [
                ['', [[], [], [], [], ["s"]]]
            ],
        	"A+N+PREP+A+N": [
                ['', [[], ["s"], [], [], []]]
            ],
        	"N+N+N": [
                ['', [[], [], ["s"]]]
            ],
           	"N+N+N+N": [
                ['', [[], [], [], ["s"]]]
            ],
            "N+N+A+N": [
                ['', [[], [], [], ["s"]]]
            ],
            "N+A+N": [
                ['', [ ["s"], [], [] ]]
            ],

        }
    def get_rus_canonical_templates(self):
        return {
        	"ADJ+N": [
                ["ADJ=^Bin", [["nom", "sg"], ["nom", "sg"]]],
                ["ADJ=Bin", [["nom", "pl"], ["nom", "pl"]]]
            ],
        	"ADJ+N+N": [
                ["", [["nom", "sg"], ["nom", "sg"], ["gen"]]]
            ],
        	"ADJ+ADJ+N": [
                ['', [["nom", "sg"], ["nom", "sg"], ["nom", "sg"]]]
            ],
        	"N+N": [
             ['+N=gen', [["nom", "sg"], ["gen"]]]
            ],
        	"ADJ+ADJ+N": [
                ['', [["nom", "sg"], ["nom", "sg"], ["nom", "sg"]]]
            ],
        	"N+N+ADJ+N": [
                ['', [["nom", "sg"], ["gen"], ["gen"], ["gen"]]]
            ],
        	"N+PPL+PREP+N": [
                ['', [["nom", "sg"], ["nom", "sg"], [], []]]
            ],
        	"ADJ+N+PREP+N": [
                ['', [["nom", "sg"], ["nom", "sg"], [], []]]
            ],
            "ADJ+N+PREP+N": [
                ['ADJ=Bin', [["nom", "pl"], ["nom", "pl"], [], []]]
            ],
        	"N+N+PREP+N": [
                ['', [["nom", "sg"], ["gen", 'sg'], [], []]]
            ],
        	"ADJ+N+PREP+ADJ+N": [
                ['', [["nom", "sg"], ["nom", "sg"], [], [], []]]
            ],
            "ADJ+N+PREP+ADJ+N": [
                ['ADJ=Bin', [["nom", "pl"], ["nom", "pl"], [], [], []]]
            ],
            "N+N+PREP+ADJ+N": [
                ['', [["nom", "sg"], ["nom", "sg"], [], [], []]]
            ],
        	"N+N+N": [
                ['', [["nom", "sg"], [], []]]
            ],
            "N+N+N+N": [
                ['', [["nom", "sg"], [], [], []]]
            ],
            "N+ADJ+N": [
                ['', [ ["nom", "sg"], ["gen"], ["gen"] ]]
            ],

        }

if __name__ == "__main__":
    main()
