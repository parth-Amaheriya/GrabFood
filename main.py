import os
from parser import parse_file
from db import FOLDER_PATH, get_connection, create_table, insert_data, create_database

def main():
    conn = get_connection()
    cursor = conn.cursor()
    
    create_database(cursor)
    create_table(cursor)

    for file_name in os.listdir(FOLDER_PATH):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(FOLDER_PATH, file_name)
        print(f"Processing: {file_name}")

        try:
            grab_food = parse_file(file_path)
            insert_data(cursor, grab_food)
            conn.commit()

        except Exception as e:
            print(f"Error in {file_name}: {e}")

    cursor.close()
    conn.close()
    print("Done!")

if __name__ == "__main__":
    main()