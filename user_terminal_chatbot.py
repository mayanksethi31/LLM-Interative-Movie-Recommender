from urllib.parse import urljoin
from pip._vendor import requests
from alive_progress import alive_bar


def make_request_request(server_url, raw_data):
    try:
        with alive_bar(100) as bar:
            r = requests.post(server_url, json=raw_data)
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
                "Please choose an option: \n 1. Get suggestions based on your mood or any keywords for movies or TV shows, \n 2. Check trending movies or TV Shows:\n Respond Here --> "
            )
            print()
            data = server_url(option)
            print(data)
        except:
            raise SystemExit()


def server_url(option):
    if option == "1":
        server_url = "http://127.0.0.1:5052/recommend"
        message = input("Please enter some keywords you wish to search for: ")
        media_type = input("Please enter media type like 'movie' or 'tv': ")
        raw_data = dict()
        raw_data = {"movie_or_tvshows": media_type, "preferences": message}
        data = make_request_request(server_url, raw_data)
        print("Response from the Engine: \n")
        return data
    elif option == "2":
        server_url = "http://127.0.0.1:5051/get_trending"
        message = input("Please enter day/week for daily, weekly trending: ")
        media_type = input("Please enter media type like movie or tv: ")
        raw_data = dict()
        raw_data = {"entertainment_type": media_type, "time_window": message}
        data = make_request_request(server_url, raw_data)
        print("Response from the Engine: \n")
        return data
    else:
        print("Response from the Engine: \n Invalid option selected. Please try again.")


if __name__ == "__main__":
    main()
