from pip._vendor import requests
from alive_progress import alive_bar


def make_request_request(server_url, raw_data, headers=None):
    try:
        with alive_bar(100) as bar:
            r = requests.post(server_url, json=raw_data, headers=headers)
            r.raise_for_status()
            bar()
    except requests.exceptions.ConnectionError as err:
        # eg, no internet
        raise SystemExit(err)
    except requests.exceptions.HTTPError as err:
        # eg, url, server and other errors
        raise SystemExit(err)
    data = r.json()
    if data is not None:
        return data
    return None


def main():
    print()
    print("INFO 253B Project: Spring 2023: Team 7")
    print("MakeMyEntertainment: Your Personal Entertainment Chatbot!")
    print(f"Please select an option from the menu below:")
    print()
    print("At any time Ctrl-C will exit the application")
    print()
    # take input from user
    while True:
        try:
            option = input(
                "Please choose an option: \n 1. New Employee? Register using email \n 2. Existing Employee? Login \n Respond Here --> "
            )
            print()
            data = server_url(option)
            print(data)
        except:
            raise SystemExit()


def server_url(option):
    if option == "1":
        server_url = "http://127.0.0.1:5050/register"
        name = input("Please enter user name: ")
        email = input("Please enter your email: ")
        password = input("Please enter your password: ")
        raw_data = dict()
        raw_data = {"name": name, "email": email, "password": password}
        data = make_request_request(server_url, raw_data)
        return data
    elif option == "2":
        server_url = "http://127.0.0.1:5050/login"
        email = input("Please enter your registered email:")
        password = input("Please enter password: ")
        raw_data = dict()
        raw_data = {"email": email, "password": password}
        data = make_request_request(server_url, raw_data)
        print(data)
        token = input("Enter token generated at login to proceed: ")
        analytics = protected_url(token)
        if analytics["message"] == "Verified":
            while True:
                try:
                    report_option = input(
                        "Please choose an option: \n 1. Generate complete report \n 2. Report based on parameters like title, type and genre \n Respond Here --> "
                    )
                    report = analytics_url(report_option)
                    print(report)
                    email_report = input("Do you want to send email report? (y/n) --> ")
                    if email_report == "y":
                        server_url = "http://127.0.0.1:5053/execute"
                        raw_data = dict()
                        email = input("Please enter recipient email:")
                        subject = input("Please enter subject: ")
                        raw_data = {
                            "data": {
                                "command": "email",
                                "message": str(email)
                                + " "
                                + str(subject)
                                + " "
                                + str(report),
                            }
                        }
                        data = make_request_request(server_url, raw_data)
                        print(data["message"])
                except:
                    raise SystemExit()
        return data
    else:
        print("Response from the Engine: \n Invalid option selected. Please try again.")


def protected_url(token):
    server_url = "http://127.0.0.1:5050/protected"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    raw_data = dict()
    data = make_request_request(server_url, raw_data, headers)
    return data


def analytics_url(report):
    if report == "1":
        server_url = "http://127.0.0.1:5055/check_data"
        raw_data = dict()
        data = make_request_request(server_url, raw_data)
        return data
    elif report == "2":
        server_url = "http://127.0.0.1:5055/filter_data"
        raw_data = dict()
        raw_data = {
            "title": input("Please enter title: "),
            "data_type": input("Please enter media type: "),
            "genre": input("Please enter genre: "),
        }
        data = make_request_request(server_url, raw_data)
        return data
    else:
        print("\n Invalid option selected. Please try again.")


if __name__ == "__main__":
    main()
