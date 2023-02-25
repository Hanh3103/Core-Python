import hashlib
import os
import re
import sys


class FileHandler:
    def __init__(self, arg):
        self.arg = arg
        self.target_files = {}
        self.hash_files = {}
        self.file_count = 1
        self.file_duplicates = {}

    def extract_file_paths(self, file_ending):
        root_dir = self.arg[1]
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                if filename.endswith(file_ending) or file_ending == "":
                    file_path = os.path.join(dirpath, filename)
                    file_size = os.path.getsize(file_path)
                    if file_size not in self.target_files.keys():
                        self.target_files[file_size] = []
                    self.target_files[file_size].append(file_path)

    def sorting_target_files(self, sort_strategy):
        if sort_strategy == 1:
            self.target_files = dict(sorted(self.target_files.items(), reverse=True))
        if sort_strategy == 2:
            self.target_files = dict(sorted(self.target_files.items()))

        for key in self.target_files.keys():
            print("{} bytes".format(key))
            for value in self.target_files[key]:
                print(value)

    def check_with_hashing(self):
        for key in self.target_files.keys():
            self.hash_files[key] = {}
            for file_path in self.target_files[key]:
                with open(file_path, "rb") as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                if file_hash not in self.hash_files[key]:
                    self.hash_files[key][file_hash] = []
                self.hash_files[key][file_hash].append(file_path)

    def print_duplicate(self):
        for key in self.hash_files.keys():
            print("{} bytes".format(key))
            for file_hash in self.hash_files[key].keys():
                if len(self.hash_files[key][file_hash]) >= 2:
                    print("Hash: " + file_hash)
                    for file_path in self.hash_files[key][file_hash]:
                        print(f"{self.file_count}. {file_path}")
                        self.file_duplicates[self.file_count] = (file_path, key)
                        self.file_count += 1

    def delete_duplicate(self, sequence):
        sum_free_spaces= 0
        if len(sequence) != 0 and all(elem in self.file_duplicates.keys() for elem in sequence):
            for num in sequence:
                os.remove(self.file_duplicates[num][0])
                sum_free_spaces += self.file_duplicates[num][1]
            print("Total freed up space: " + str(sum_free_spaces))
            return True
        else:
            print("Wrong format")
            return False


if __name__ == "__main__":
    argsf = sys.argv
    if len(argsf) != 1:
        a = FileHandler(argsf)
        file_end = input("Enter file format:")
        a.extract_file_paths(file_end.lower())

        print('''
        Size sorting options:
        1. Descending
        2. Ascending
        ''')
        sort_stra = 0
        while True:
            sort_stra = int(input("Enter a sorting option:"))
            if sort_stra == 1 or sort_stra == 2:
                break
            else:
                print("Wrong option")
        a.sorting_target_files(sort_stra)

        check_dup = ""
        while True:
            check_dup = input("Check for duplicates?")
            if check_dup.lower() == "yes" or check_dup.lower() == "no":
                break
            else:
                print("Wrong option")
        if check_dup.lower() == "yes":
            a.check_with_hashing()
            a.print_duplicate()
        while True:
            del_dup = input("Delete files?")
            if del_dup.lower() == "yes" or del_dup.lower() == "no":
                break
            else:
                print("Wrong option")
        if del_dup.lower() == "yes":
            while True:
                sequence_files = input("Enter file numbers to delte:")
                if re.match(r'^\d+( \d+)*$', sequence_files):
                    file_numbers = list(map(int, sequence_files.split()))
                    t = a.delete_duplicate(file_numbers)
                    if t:
                        break
                else:
                    print("Wrong format")
    else:
        print("Directory is not specified")
