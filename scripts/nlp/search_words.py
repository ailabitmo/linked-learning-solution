# -*- coding: UTF-8 -*-

import os,re,codecs

import MorphologyLibruary

def main():
    input_file = os.path.join(os.path.dirname(__file__), 'input_text', 'test_rus.txt')
    dic_file = os.path.join( os.path.dirname(__file__), r"math_phys_rus-flx.dic")
    outpt_file = os.path.join( os.path.dirname(__file__), r"out_file")

    wh = codecs.open(outpt_file, 'w', encoding = "utf8")
    wh.write("[\n")
    lang = 'rus'
    res = MorphologyLibruary.MorphoAnalyzer(dic_file, lang)
    splitter_re = re.compile(r";|\.")


    task_variants_eng = [
        [["N=^Pos", "N"], []],
        [["N=Pos", "N"], []],
        [["N", "PREP", "A", "N"], []],
        [["A", "N"], []],
        [["A", "N", "N"], []],
        [["A", "A", "N"], []],
        [["A", "N", "N", "N"], []],
        [["A", "N", "PREP", "N", "N"], []],
        [["N"],[]],

        [["N", "N", "N"],[]],
        [["N", "PREP", "N", "N"], []]
    ]

    task_variants_rus = [
        [["ADJ=^Bin", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case"]],
        [["ADJ=Bin", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case"]],
        [["ADJ", "N", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case"]],
        [["ADJ", "ADJ", "N"], ["0.gender=1.gender,  1.gender=2.gender", "0.number=1.number, 1.number=2.number", "0.case=1.case, 1.case=2.case"]],
        [["N", "N=gen"], []],
        [["N", "N=gen", "ADJ=^Bin=gen", "N=gen"], ["2.gender=3.gender", "2.number=3.number", "2.case=3.case"]],
        [["N", "N+gen", "ADJ=^Bin=ins", "N=ins"], ["2.gender=3.gender", "2.number=3.number", "2.case=3.case"]],
        [["N", "N=gen", "ADJ=Bin=gen", "N=gen"], ["2.gender=3.gender", "2.number=3.number", "2.case=3.case"]],
        [["N", "N=gen", "ADJ=Bin=ins", "N=ins"], ["2.gender=3.gender", "2.number=3.number", "2.case=3.case"]],
        [["N", "N", "PPL", "PREP", "N"], ["1.gender=2.gender", "1.number=2.number", "1.case=2.case"]],
        [["N", "PPL", "PREP", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case"]],
        [["N", "PPL", "PREP", "ADJ", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case", "3.gender=4.gender", "3.number=4.number", "3.case=4.case"]],
        [["N", "PPL", "PREP", "N", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case"]],
        [["ADJ=Bin", "N", "PREP", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case"]],
        [["ADJ=^Bin", "N", "PREP", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case"]],
        [["ADJ", "N", "PREP", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case"]],
        [["N", "N=gen", "PREP", "N"], ['']],
        [["N", "N=gen", "PREP", "ADJ", "N"], ["3.gender=4.gender", "3.number=4.number", "3.case=4.case"]],
        [["ADJ=Bin", "N", "PREP", "ADJ", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case", "3.gender=4.gender", "3.number=4.number", "3.case=4.case"]],
        [["ADJ=^Bin", "N", "PREP", "ADJ", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case", "3.gender=4.gender", "3.number=4.number", "3.case=4.case"]],
        [["ADJ=Bin", "N", "PREP", "ADJ=^Bin", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case", "3.gender=4.gender", "3.number=4.number", "3.case=4.case"]],
        [["ADJ=^Bin", "N", "PREP", "ADJ=Bin", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case", "3.gender=4.gender", "3.number=4.number", "3.case=4.case"]],
        [["ADJ=Bin", "N", "PREP", "ADJ=Bin", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case", "3.gender=4.gender", "3.number=4.number", "3.case=4.case"]],
        [["ADJ=^Bin", "N", "PREP", "ADJ=^Bin", "N"], ["0.gender=1.gender", "0.number=1.number", "0.case=1.case", "3.gender=4.gender", "3.number=4.number", "3.case=4.case"]],
        [["N", "N=gen", "N=gen"], []],
        [["N", "N=gen", "N=gen", "N=gen"], []],
        [["N", "N=gen", "N=ins"], []],
    ]

    if lang == 'rus':
            task_variants = task_variants_rus
    else:
            task_variants = task_variants_eng
    words_re = re.compile(r"(?P<whole_word>\b[А-Яа-яA-Za-z]+([-']\b[А-Яа-яA-Za-z]+)?\b)")
    source_text = read_file(input_file)


    sentences = re.split(splitter_re, source_text)


    for sentence_id in range(len(sentences)):
        print("Номер предложения -> {0}".format( sentence_id ))
        if sentence_id == 325:
            a = 1
        sentence = sentences[sentence_id]
        elements = re.split(r"\s+", sentence.strip())

        for template_array, gram_conditions in task_variants:
            print("Шаблон -> {0}".format(template_array))
            template_to_check = [re.sub(r"=.+$", "", elem) for elem in template_array]
            extra_params_template = []
            for elem in template_array:
                if elem.find("=") != -1:
                    extra_params_template.append(elem)
                else:
                    extra_params_template.append('')
            extra_params_template = "+".join(extra_params_template)
            for i in range(len(elements)-len(template_array)):
                pos = []
                cur_words = []
                flag = True
                for j in range(len(template_array)):
                    pseudo_word = elements[i+j]

                    if re.search(r"(http:.+)", pseudo_word):
                        flag = False
                        break

                    word_found = re.search(words_re, pseudo_word)
                    if word_found is not None:
                        word_found_text = word_found.group()
                        #word_found_text = 'крибликрабли'
                        cur_pos = res.get_part_of_speech(word_found_text.lower())

                        if cur_pos == '':
                            break
                        cur_words.append(word_found_text)
                        pos.append( cur_pos.split("|") )
                        a = 1
                if len(pos) != len(template_to_check):
                    continue
                flag_pos_comparison = True
                for k in range(len(template_to_check)):
                    if not template_to_check[k] in pos[k]:
                        flag_pos_comparison = False
                if not flag_pos_comparison:
                    continue
                extra_condition = res.parse_extra_condition(extra_params_template, template_to_check)

                is_grammar_ok = False

                if len(extra_condition) == 0:
                    #нет доп. условий
                    is_grammar_ok = res.check_grammar_conditions(cur_words, template_to_check, gram_conditions)

                else:
                    is_matched = res.check_extra_condition(cur_words, extra_condition, template_to_check)
                    if not is_matched:
                        continue
                    #gram_conditions
                    is_grammar_ok = res.check_grammar_conditions(cur_words, template_to_check, gram_conditions)

                if is_grammar_ok:
                    try:
                        print( " ".join( cur_words ).lower() )
                        if " ".join( cur_words ).lower() == "проекции вектора на оси":
                            a = 1
                        [canonical_variants, phrase, word_template_string] = res.normalize(" ".join( cur_words ).lower())
                        canonical_form = canonical_variants[0]
                        if canonical_form == "проекция вектора на осью":
                            a =1
                        lemmas = [res.words2lemmas_dict.get(elem.lower(), ["NO_LEMMA"])[0] for elem in cur_words]

                        wh.write("{\n")
                        wh.write("canon_name: \"{0}\",\n".format(canonical_form))
                        wh.write("\"lemmas\": [{0}]\n".format(",".join(["\"{0}\"".format(elem) for elem in lemmas])))
                        wh.write("},\n")
                        a = 1
                    except Exception as err:
                        print("get_canon -> {0}".format(err))
                a = 1
        a = 1
        #{
#canon_name: "точка пространств",
#"lemmas": ['точка', 'пространство']
#"lemmas": "['точка', 'пространство']",
#},
    wh.write("]\n")
    wh.close()
def read_file(filename):
    '''
    читает txt файл. кодировка входного файла utf-8
    '''
    outpt = ""
    fh = None
    try:
        fh = codecs.open(filename, "rb")
        length = os.path.getsize(filename)
        outpt = fh.read(length).decode('utf8')+"\n"
        outpt = outpt.replace("\n", " ").replace("\r", " ")
    except Exception as err:
        print("read_file -> {0} : {1}".format(filename, err))
    finally:
        if fh is not None:
            fh.close()
        return outpt
main()
