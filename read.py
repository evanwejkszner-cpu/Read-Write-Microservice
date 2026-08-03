import zmq
import sqlite3

DATABASE_NAME = "saved_items.db"

###########################################################################
# Database
###########################################################################


def connect_db():
    """Create a database connection."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """
    Creates the table if it doesn't already exist.
    """

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_items(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            description TEXT,

            media_type TEXT NOT NULL,

            filepath TEXT NOT NULL,

            created TEXT,

            modified TEXT

        );
    """)

    conn.commit()
    conn.close()


###########################################################################
# Utility
###########################################################################

def row_to_dict(row):
    """
    Convert a SQLite Row object into a Python dictionary.
    """

    if row is None:
        return None

    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "media_type": row["media_type"],
        "filepath": row["filepath"],
        "created": row["created"],
        "modified": row["modified"]
    }


###########################################################################
# Read Functions
###########################################################################

def get_all_items():
    """
    Return every item in the database.
    """

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM saved_items
        ORDER BY title ASC;
    """)

    rows = cursor.fetchall()

    conn.close()

    return [row_to_dict(r) for r in rows]


###########################################################################

def get_item(item_id):
    """
    Return one item by its ID.
    """

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM saved_items
        WHERE id = ?;
    """, (item_id,))

    row = cursor.fetchone()

    conn.close()

    return row_to_dict(row)


###########################################################################

def get_media_type(media_type):
    """
    Return all TEXT, IMAGE, or VIDEO records.
    """

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM saved_items
        WHERE media_type = ?
        ORDER BY title;
    """, (media_type.upper(),))

    rows = cursor.fetchall()

    conn.close()

    return [row_to_dict(r) for r in rows]


###########################################################################

def search_items(keyword):
    """
    Search title and description.
    """

    conn = connect_db()
    cursor = conn.cursor()

    wildcard = f"%{keyword}%"

    cursor.execute("""
        SELECT *
        FROM saved_items
        WHERE title LIKE ?
           OR description LIKE ?
        ORDER BY title;
    """, (wildcard, wildcard))

    rows = cursor.fetchall()

    conn.close()

    return [row_to_dict(r) for r in rows]


###########################################################################
# UI Helpers
###########################################################################

def display_item(item):
    """
    Display one record.
    """

    if item is None:
        print("Item not found.")
        return

    print("=" * 50)

    print(f"ID          : {item['id']}")
    print(f"Title       : {item['title']}")
    print(f"Description : {item['description']}")
    print(f"Media Type  : {item['media_type']}")
    print(f"File        : {item['filepath']}")
    print(f"Created     : {item['created']}")
    print(f"Modified    : {item['modified']}")

    print("=" * 50)


###########################################################################

def display_list(items):

    if not items:
        print("No matching items.")
        return

    print()

    for item in items:

        print(
            f"[{item['id']:3}] "
            f"{item['title']:<25} "
            f"{item['media_type']:<6}"
        )

    print()


###########################################################################
# Edit Support
###########################################################################

def prepare_for_edit(item_id):
    """
    Returns the complete record.

    The Save Service can use this information
    to populate an editing form.
    """

    return get_item(item_id)


###########################################################################
# Demonstration
###########################################################################

def start_server():

    initialize_database()

    context = zmq.Context()

    socket = context.socket(zmq.REP)

    socket.bind("tcp://*:5555")

    print("====================================")
    print(" Read Microservice Running")
    print(" Listening on tcp://localhost:5555")
    print("====================================")

    while True:

        request = socket.recv_json()

        print("\nReceived Request:")
        print(request)

        command = request.get("command", "").upper()

        try:

            ####################################################
            # GET ALL
            ####################################################

            if command == "GET_ALL":

                socket.send_json(get_all_items())

            ####################################################
            # GET ITEM
            ####################################################

            elif command == "GET_ITEM":

                item_id = request["id"]

                socket.send_json(get_item(item_id))

            ####################################################
            # SEARCH
            ####################################################

            elif command == "SEARCH":

                keyword = request["keyword"]

                socket.send_json(search_items(keyword))

            ####################################################
            # FILTER BY TYPE
            ####################################################

            elif command == "GET_TYPE":

                media = request["type"]

                socket.send_json(get_media_type(media))

            ####################################################
            # EDIT
            ####################################################

            elif command == "EDIT":

                item_id = request["id"]

                socket.send_json(prepare_for_edit(item_id))

            ####################################################
            # PING
            ####################################################

            elif command == "PING":

                socket.send_json({
                    "status": "OK",
                    "service": "Read Service"
                })

            ####################################################
            # UNKNOWN COMMAND
            ####################################################

            else:

                socket.send_json({
                    "error": "Unknown command"
                })

        except Exception as e:

            socket.send_json({
                "error": str(e)
            })


###########################################################################

if __name__ == "__main__":
    start_server()
