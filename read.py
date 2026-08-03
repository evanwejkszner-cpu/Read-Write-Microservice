import os
import time

REQUEST_FILE = "read_request.txt"
RESPONSE_FILE = "read_response.txt"


############################################################
# Parse key=value request
############################################################

def parse_request(path):

    request = {}

    with open(path, "r") as f:

        for line in f:

            line = line.strip()

            if "=" in line:

                key, value = line.split("=", 1)

                request[key] = value

    return request


############################################################
# Read requested file
############################################################

def read_file(filename):

    if not os.path.exists(filename):

        return None

    with open(filename, "r") as f:

        return f.read()


############################################################
# Write response
############################################################

def write_response(status, filename="", data="", message=""):

    with open(RESPONSE_FILE, "w") as f:

        f.write(f"status={status}\n")

        if filename:

            f.write(f"file_name={filename}\n")

        if data:

            f.write(f"data={data}\n")

        if message:

            f.write(f"message={message}\n")


############################################################
# Main loop
############################################################

def main():

    print("Read Service Running...")

    while True:

        if os.path.exists(REQUEST_FILE):

            print("Read request found!")

            request = parse_request(REQUEST_FILE)

            if "file_name" not in request:

                write_response(
                    "failure",
                    message="Missing file_name"
                )

            else:

                filename = request["file_name"]

                data = read_file(filename)

                if data is None:

                    write_response(
                        "failure",
                        filename=filename,
                        message="File not found"
                    )

                else:

                    write_response(
                        "success",
                        filename=filename,
                        data=data
                    )

                    print(f"Read {filename}")

            os.remove(REQUEST_FILE)

        time.sleep(1)


############################################################

if __name__ == "__main__":

    main()
    
