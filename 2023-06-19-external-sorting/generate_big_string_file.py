import string
import random
import time

letters = string.ascii_lowercase # a-z
string_lengths = [i+1 for i in range(9)] # 1 - 10

def get_random_string():
    chars = [random.choice(letters) for i in range(random.choice(string_lengths))]
    chars.append("\n")
    return ''.join(chars)


start_time = time.time()
f = open("./big_string_file.txt", 'w')
target_file_size = 2**30 # 1GB
expected_string_size = 7.5 # average 5.5B + 2B("\n")
needed_string_num = int(target_file_size / expected_string_size)

for i in range(needed_string_num):
    f.write(get_random_string())
f.close()

end_time = time.time()
print(f"파일 생성이 완료되었습니다. {end_time-start_time:.2f}초 소요.")