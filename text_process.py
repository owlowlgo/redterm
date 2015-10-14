import unicodedata


def get_east_asian_width(string):
    length = 0

    for char in string:
        if unicodedata.east_asian_width(char) in {'W', 'F', 'A'}:
            length += 2
        else:
            length += 1

    return length


def wrap_east_asian_string(string, width):
    width -= 1
    lines = []

    for line in string.splitlines():
        length = 0
        last_char_num = 0
        for char_num, char in enumerate(line, 1):
            if unicodedata.east_asian_width(char) in {'W', 'F', 'A'}:
                length += 2
            else:
                length += 1

            if length >= width:
                string_to_extract = line[last_char_num:char_num]
                first_char_of_next_line = line[char_num:char_num+1]

                #print('AAA' + first_char_of_next_line)
                # if last word over steps width boundary, obmit it from current line
                len_of_obmission = 0
                if not string_to_extract.endswith(' '):
                    if not first_char_of_next_line == ' ':
                        print([string_to_extract, first_char_of_next_line])
                        line_split = string_to_extract.rsplit(' ', 1)
                        print(line_split)
                        print('-----------------')
                        string_to_extract = line_split[0]
                        len_of_obmission = len(line_split[1])
                        char_num -= len_of_obmission

                #print([string_to_extract, first_char_of_next_line])

                lines.append(string_to_extract)

                length = 0
                last_char_num = char_num

        string_to_extract = line[last_char_num:]
        lines.append(string_to_extract)

    return lines

if __name__ == '__main__':
    strings = []



    strings.append("""Taro Yamamoto (山本 太郎 Yamamoto Tarō?, born 24 November 1974 in Takarazuka, Hyōgo) is a Japanese politician and former actor.

In 2008, he said on a TV show that the Liancourt Rocks, disputed between Japan and Korea, should be given to Korea.[1]

In 2011, he announced that he "would no longer be a silent accomplice of the terrorist nation Japan", and became a protester in the anti-nuclear movement.[2] Yamamoto, a resident of Tokyo, flew to Saga Prefecture and attempted to break into the governor's office to protest the restart of a power plant. He chanted phrases such as, "Protect our children!" "We don't need nuclear energy!" "Come out, Governor!" He did not get an audience with the governor, but said he was glad that he came.[3]""")


    #print(get_east_asian_width(string1))
    #print(get_east_asian_width(string2))

    width = 40
    for string in strings:
        lines = wrap_east_asian_string(string, width)
        for line in lines:
            print(get_east_asian_width(line), line)

#print(wrap_east_asian_string(strings[0], 20))

