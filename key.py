import random

def gen_key_part():
    # Генерация цифр
    num1 = str(random.randint(0, 9))
    num2 = str(random.randint(0, 9))
    num3 = str(random.randint(0, 9))
    num4 = str(random.randint(0, 9))

    # Генерация части ключа (1 блок)
    final = num1 + num2 + num3 + num4
    return final

def sum_ord(key_part):
    # Раскладываем переданную часть ключа на цифры
    num1 = key_part[0]
    num2 = key_part[1]
    num3 = key_part[2]
    num4 = key_part[3]

    # Алгорит сложения в crackme
    sum = ord(num1) + ord(num2) + ord(num3) + ord(num4) + ord(num4) + ord(num4)
    sum_final = ord(num4) + sum - 336
    return sum_final

def shr(key):
    # Разбиваем ключ на блоки
    a = key[0:4]
    b = key[5:9]
    c = key[10:14]
    d = key[15:19]

    # Алгоритм сдвига по битам в crackme
    x = sum_ord(a) + sum_ord(b) + sum_ord(c) + sum_ord(d)
    x = x >> 2
    return x

def generate_key():
    # Генерация ключа
    key = gen_key_part() + '-' + gen_key_part() + '-' + gen_key_part() + '-' + gen_key_part()
    print(key)
    #

# Генерируем ключ, вызывая функцию
if __name__ == "__main__":
    generate_key()