import random
import copy


def lookup_byte(byte):
    x = byte >> 4
    y = byte & 0x0f
    s_box = [[0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
             [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
             [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
             [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
             [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
             [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
             [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
             [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
             [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
             [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
             [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
             [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
             [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
             [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
             [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
             [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]]
    return s_box[x][y]


def shift_row(row, shift):
    result = list(row)
    if shift != 0:
        temp = result[0]

        for i in range(3):
            result[i] = result[i + 1]
        result[3] = temp

        return shift_row(result, shift - 1)

    else:
        return result


def rotate_word(word):
    result = word
    result = shift_row(result, 1)
    return result


def xor_words(word_a, word_b):
    result = [0, 0, 0, 0]
    w_a = list(word_a)
    w_b = list(word_b)
    for i in range(4):
        result[i] = w_a[i] ^ w_b[i]
    return result


def sub_word(word):
    result = [0, 0, 0, 0]
    for i in range(4):
        byte = word[i]
        result[i] = lookup_byte(byte)

    return result


def generate_keys(state_key):
    key_schedule = []
    temp = []
    round_key = [[0] * 4 for _ in range(4)]
    p_round_key = [[0] * 4 for _ in range(4)]
    RCON = [[0x01, 0X00, 0X00, 0X00],
            [0x02, 0X00, 0X00, 0X00],
            [0x04, 0X00, 0X00, 0X00],
            [0x08, 0X00, 0X00, 0X00],
            [0x10, 0X00, 0X00, 0X00],
            [0x20, 0X00, 0X00, 0X00],
            [0x40, 0X00, 0X00, 0X00],
            [0x80, 0X00, 0X00, 0X00],
            [0x1b, 0X00, 0X00, 0X00],
            [0x36, 0X00, 0X00, 0X00]]
    key_schedule.append(state_key)
    for i in range(4):
        p_round_key[i] = [state_key[4 * i], state_key[4 * i + 1], state_key[4 * i + 2], state_key[4 * i + 3]]

    for i in range(10):
        round_key[0] = rotate_word(tuple(p_round_key[3]))
        round_key[0] = sub_word(round_key[0])
        round_key[0] = xor_words(tuple(xor_words(tuple(p_round_key[0]), tuple(round_key[0]))), RCON[i])
        for j in range(1, 4):
            round_key[j] = xor_words(tuple(round_key[j - 1]), tuple(p_round_key[j]))

        for k1 in range(4):
            for k2 in range(4):
                temp.append(round_key[k1][k2])

        key_schedule.append(temp)
        temp = []

        p_round_key = round_key.copy()

    return key_schedule


def random_key_generator():
    random_key = []
    for i in range(16):
        random_key.append(random.randint(0, 255))
    return random_key


def transpose_state(state_block):
    transposed_state = [[0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            transposed_state[i][j] = state_block[j][i]

    return transposed_state


def key_to_words(round_key):
    word_block = [[0] * 4 for _ in range(4)]

    for i in range(4):
        word_block[i] = [round_key[4 * i], round_key[4 * i + 1], round_key[4 * i + 2], round_key[4 * i + 3]]

    return word_block


def add_round_key(state, round_key):
    result = [[0] * 4 for _ in range(4)]

    state_words = transpose_state(state)
    key_words = key_to_words(round_key)

    for i in range(4):
        result[i] = xor_words(state_words[i], key_words[i])

    return transpose_state(result)


def sub_bytes(state):
    result = [[0] * 4 for _ in range(4)]

    for i in range(4):
        for j in range(4):
            byte = state[i][j]
            result[i][j] = lookup_byte(byte)

    return result


def shift_rows(state):
    result = [[0] * 4 for _ in range(4)]

    for i in range(4):
        result[i] = shift_row(state[i], i)

    return result


def mult_2(value):
    s = value << 1

    if value & 0x80:
        s &= 0xff
        s = s ^ 0x1b

    return s


def mult_3(value):
    return mult_2(value) ^ value


def mix_column(state_column):
    result = [0, 0, 0, 0]

    result[0] = mult_2(state_column[0]) ^ mult_3(state_column[1]) ^ state_column[2] ^ state_column[3]
    result[1] = mult_2(state_column[1]) ^ mult_3(state_column[2]) ^ state_column[3] ^ state_column[0]
    result[2] = mult_2(state_column[2]) ^ mult_3(state_column[3]) ^ state_column[0] ^ state_column[1]
    result[3] = mult_2(state_column[3]) ^ mult_3(state_column[0]) ^ state_column[1] ^ state_column[2]

    return result


def mix_columns(state):
    result = [[0] * 4 for _ in range(4)]
    column = [0, 0, 0, 0]

    for i in range(4):
        for j in range(4):
            column[j] = state[j][i]

        column = mix_column(column)

        for k in range(4):
            result[k][i] = column[k]

    return result


def encrypt_block(block, key_schedule):
    state = list(block)
    state = add_round_key(state, key_schedule[0])

    for i in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, key_schedule[i])

    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, key_schedule[10])

    return state


def encrypt_data(open_text, key_schedule):
    return_pair = []
    encrypted_blocks = []
    encrypted_text = ''
    open_text_length = len(open_text)
    zero_count = 0

    if open_text_length % 16 != 0:
        for i in range(16 - (open_text_length % 16)):
            open_text += '0'
            zero_count += 1

    blocks_count = len(open_text) // 16
    block = [[0] * 4 for _ in range(4)]
    open_text_position = 0

    for i in range(blocks_count):
        for j in range(16):
            block[j % 4][j // 4] = ord(open_text[open_text_position])
            open_text_position += 1
        block = encrypt_block(block, key_schedule)
        appending_copy = copy.deepcopy(block)
        encrypted_blocks.append(appending_copy)
        for row in range(4):
            for column in range(4):
                encrypted_text += chr(block[column][row])

    return_pair.append(encrypted_blocks)
    return_pair.append(encrypted_text[:-zero_count])

    return return_pair


def un_mix_columns(state):
    result = mix_columns(state)
    result = mix_columns(result)
    result = mix_columns(result)

    return result
