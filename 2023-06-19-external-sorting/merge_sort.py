import time
import os

start_time = time.time()

file = open("./big_string_file.txt", 'r')

# split files 
buffers_path = ["./merge_buffer"]
size_of_part = 200 * (2**20) # 200MB
i = 1
buffer_file = open(buffers_path[-1], 'w')
expected_string_size = 10
buffer_size = expected_string_size
while True:
    if size_of_part < buffer_size:
        buffer_file.close()
        buffer_size = expected_string_size
        i += 1
        buffers_path.append(buffers_path[0] + f'_{i}')
        buffer_file = open(buffers_path[-1], 'w')
    line = file.readline().strip()
    if not line: break
    write_line = line + '\n'
    buffer_file.write(write_line)
    buffer_size += expected_string_size
buffer_file.close()

# sort by files
for buff_path in buffers_path:
    data = []
    buffer = open(buff_path, 'r')
    while True:
        line = buffer.readline().strip()
        if not line: break
        data.append(line)
    buffer.close()
    data.sort()
    buffer = open(buff_path, 'w')
    for dat in data:
        buffer.write(dat+"\n")
    buffer.close()

# merge 
result_file = open("./merge_sort_result.txt", 'w')
buffers = [open(buff_path) for buff_path in buffers_path]
data = [file.readline().strip() for file in buffers]
i = 0
while True:
    min_index = -1
    min_str = ""
    for index, dat in enumerate(data):
        if dat != "" and (min_index == -1 or min_str < dat):
            min_index = index
            min_str = dat
    if min_index == -1: break
    result_file.write(min_str + '\n')
    data[min_index] = buffers[min_index].readline().strip()
    i += 1
    if i % 100000 == 0:
        print(f"----------{i}개 요소 정렬완료------------")

result_file.close()
for buff in buffers:
    buff.close()
for buff_path in buffers_path:
    os.remove(buff_path)

end_time = time.time()
print(f"병합 정렬 완료. {(end_time-start_time) // 60:0f}분 {(end_time-start_time) % 60:.0f}초 소요")