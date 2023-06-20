import time
import os

def sort_and_save(file_path):
    file = open(file_path, 'r')
    data = []
    while True:
        line = file.readline().strip()
        if not line: break
        data.append(line)
    file.close()
    data.sort()
    file = open(file_path, 'w')
    for dat in data:
        file.write(dat+'\n')
    file.close()

def quick_sort(file_path):
    # split by pivot 
    file = open(file_path, 'r')
    pivot = file.readline().strip()
    if not pivot: return
    smaller_file_path = file_path + "-smaller"
    larger_file_path = file_path + "-larger"
    smaller_file = open(smaller_file_path, 'w')
    larger_file = open(larger_file_path, 'w')
    while True:
        line = file.readline().strip()
        if not line: break
        if line <= pivot:
            smaller_file.write(line+'\n')
        else:
            larger_file.write(line+'\n')
    smaller_file.close()
    larger_file.close()
    file.close()

    # recursion if memory not enough
    if os.stat(smaller_file_path).st_size < memory_size:
        sort_and_save(smaller_file_path)
    else:
        quick_sort(smaller_file_path)
    
    if os.stat(larger_file_path).st_size < memory_size:
        sort_and_save(larger_file_path)
    else:
        quick_sort(larger_file_path)
    
    # concatenate smaller and larger
    file = open(file_path, 'w')
    smaller = open(smaller_file_path, 'r')
    while True:
        line = smaller.readline()
        if not line: break
        file.write(line)
    smaller.close()
    os.remove(smaller_file_path)
    larger = open(larger_file_path, 'r')
    file.write(pivot + '\n')
    while True:
        line = larger.readline()
        if not line: break
        file.write(line)
    larger.close()
    os.remove(larger_file_path)
    file.close()

start_time = time.time()
memory_size = 200 * (2**20)

file = open("./big_string_file.txt", 'r')
result_file_path = "./quick_sort_result.txt"
result_file = open(result_file_path, 'w')
while True:
    line = file.readline()
    if not line: break
    result_file.write(line)
file.close()
result_file.close()

quick_sort(result_file_path)

end_time = time.time()
print(f"퀵 정렬 완료. {(end_time-start_time) // 60:.0f}분 {(end_time-start_time) % 60:.0f}초 소요")