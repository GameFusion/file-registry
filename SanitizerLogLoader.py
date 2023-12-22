import pickle
import sys

def read_and_print_data(file_path):
    try:
        with open(file_path, 'rb') as file:
            non_utf8_files = pickle.load(file)

        file_count = 0

        for record in non_utf8_files:
            ascii_name = record.get("ASCII Equivalent", "N/A")
            directory_path = record.get("Directory Path", "N/A")
            print(f"ASCII Equivalent: {ascii_name} | Directory Path: {directory_path}")
            file_count += 1

        print(f"Total count of files: {file_count}")

    except Exception as e:
        print(f"Error reading file: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <path_to_pickle_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    read_and_print_data(file_path)

if __name__ == "__main__":
    main()

