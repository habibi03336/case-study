import os 
import time 

start_time = time.time()

file = open("./big_string_file.txt", 'r')
buffer = open("./bubble_sort_1.txt", 'w')

tmp = None
n = 0
while True:
    line = file.readline().strip()
    if not line: break
    n += 1
    if tmp == None:
        tmp = line
    elif tmp >= line:
        buffer.write(line + '\n')
    elif tmp < line: 
        buffer.write(tmp + '\n')
        tmp = line
buffer.write(tmp)
buffer.close()

buffers_path = ["./bubble_sort_1.txt", "./bubble_sort_2.txt"]
for i in range(n-2):
    read = open(buffers_path[i % 2], 'r')
    buffer = open(buffers_path[(i+1) % 2], 'w')
    tmp = None
    while True:
        line = read.readline().strip()
        if not line: break
        if tmp == None:
            tmp = line
        elif tmp >= line:
            buffer.write(line + '\n')
        elif tmp < line:
            buffer.write(tmp + '\n')
            tmp = line
    read.close()
    buffer.close()

if n % 2 == 0:
    os.rename('./bubble_sort_1.txt', './bubble_sort_result.txt')
    os.remove('./bubble_sort_2.txt')
else:
    os.rename('./bubble_sort_2.txt', './bubble_sort_result.txt')
    os.remove('./bubble_sort_1.txt')

end_time = time.time()

print(f"정렬 완료. {(end_time-start_time) // 60}분 {(end_time-start_time) % 60:.0f}초 소요")