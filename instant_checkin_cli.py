import requests
from unopass import unopass as secret

try:
    print("\n\033[93mRetrieving Jamf secrets via unopass...\033[0m")
    username = secret.unopass("personal", "hyper_jamf", "username")
    password = secret.unopass("personal", "hyper_jamf", "credential")
    jss = secret.unopass("personal", "hyper_Jamf", "url")
except Exception as e:
    print(f"\n\033[91mError\033[0m: {e}")
    exit(1)


def getBearerToken() -> str:
    url = f"{jss}/api/v1/auth/token"
    headers = {"Accept": "application/json"}
    response = requests.post(url, auth=(username, password), headers=headers)
    token = response.json()["token"]
    return token


def invalidateToken(token: str) -> str:
    url = f"{jss}/api/v1/auth/invalidate-token"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(url, headers=headers)
    secret.signout(deauthorize=True)

    if response.status_code == 204:
        print("\n\033[92mJamf token invalidated OK\033[0m")
    elif response.status_code == 401:
        print("\nJamf token already invalidated")
    else:
        print("\nError invalidating Jamf token")


def banner():
    print("\n\033[92mWelcome to the instant-checkin CLI\033[0m\n\n-------------------------------------")


def user_input() -> str:
    print("\nEnter the employee username: ")
    username = input()
    return username


def update_room(chosen: str, token: str) -> None:
    name = chosen.split(":")[1]
    ids = chosen.split(":")[0]
    headers = {"Authorization": f"Bearer {token}"}
    data = "<computer><location><room>check-in</room></location></computer>"
    url = f"{jss}/JSSResource/computers/id/{ids}"
    resp = requests.put(url, data=data, headers=headers)

    if resp.status_code == 201:
        print(f"\n\033[92mSuccess\033[0m: {name} will be check-in shortly.")
    else:
        print(f"\n\033[91mError\033[0m: {name} was not updated.")

    invalidateToken(token)


def main() -> None:
    banner()
    computers = []
    token = getBearerToken()
    username = user_input()
    url = f"{jss}/JSSResource/computers/match/{username}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers).json()
    data = response["computers"]

    if data:
        for computer in data:
            if "ready" in computer["room"].lower():
                computers.append(f"{computer['id']}:{computer['name']}")
            else:
                print(f"\n\033[91mWarning\033[0m: {computer['name']}: Not ready for Instant Check-in")
                print(f"\nDeploy this policy to get the user's computer ready:\n{jss}/policies.html?id=157")
    else:
        print(f"\n\033[91mError\033[0m: No computers found for {username}\n")
        invalidateToken(token)
        exit(1)

    if computers:
        for ids, name in enumerate(computers, 1):
            print("\n-------------------------------------")
            print(f"\n\033[92mJamf Computer Lookup Results:\033[0m {username}\n\n{ids}, Computer {name}")

        try:
            ids = int(input("\nEnter a computer number from the list : "))
        except ValueError:
            print("You fail at typing numbers.")
            return

        try:
            chosen = computers[ids - 1]
            print("\n-------------------------------------")
            print(f"\n\033[93mRequesting an instant check-in\033[0m: {chosen}")
            update_room(chosen, token)
        except IndexError:
            print("Try a number in range next time.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n\033[91mError\033[0m: {e}")
        exit(1)
    except KeyboardInterrupt:
        print("\n\n\033[91mExiting...\033[0m")
        invalidateToken(getBearerToken())
        secret.signout(deauthorize=True)
        exit()
