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

    if response.status_code == 204:
        print("\n\033[92mJamf token invalidated OK\033[0m")
    elif response.status_code == 401:
        print("\nJamf token already invalidated")
    else:
        print("\nError invalidating Jamf token")


def banner():
    print(
        "\n\033[92mWelcome to the instant-checkin CLI"
        "\033[0m\n\n-------------------------------------"
    )


def user_input() -> str:
    while True:
        print("\nEnter the employee username: Format amado.tejada\n")
        username = input()
        if "." in username:
            return username
        else:
            print(
                f"\n\033[91mError\033[0m: {username} is invalid | Format amado.tejada"
            )


def update_room(chosen: str, token: str) -> None:
    name = chosen.split(":")[1]
    ids = chosen.split(":")[0]
    headers = {"Authorization": f"Bearer {token}"}
    data = "<computer><location><room>check-in</room></location></computer>"
    url = f"{jss}/JSSResource/computers/id/{ids}"
    resp = requests.put(url, data=data, headers=headers)

    try:
        if resp.status_code == 201:
            print(f"\n\033[92mSuccess\033[0m: {ids}:{name} 🎉")
        elif resp.status_code == 409:
            print(f"\n\033[93mSkipping\033[0m: Jamf duplicate serial# for {ids}:{name}")
        else:
            print(resp.status_code)
            print(f"\n\033[91mError\033[0m: {ids}:{name} was not updated")
    except Exception as e:
        print(f"\n\033[91mError\033[0m: {e}")


def main() -> None:
    banner()
    token = getBearerToken()
    username = user_input()
    computers, usernames = [], []
    results, used = [], []
    usernames = set()
    usernames.add(username)
    usernames.add(username.replace(".", ""))
    usernames.add(username + "@DOMAIN.com")  # change to Jamf domain
    usernames.add(username.replace(".", "") + "@DOMAIN.com")

    for u in usernames:
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        url = f"{jss}/JSSResource/computers/match/{u}"
        response = requests.get(url, headers=headers)
        data = response.json()
        if data != []:
            for u in data["computers"]:
                computers.append(u)

    unique = [x for x in computers if x not in used and (used.append(x) or True)]
    for c in unique:
        if "ready" in c["room"].lower():
            results.append(f"{c['id']}:{c['name']}")
        else:
            print(
                f"\n\033[91mWarning: Not ready for Instant Check-in - deploy policy\033[0m "
                f"\nID: {c['id']}, Laptop: {c['name']}, Serial: {c['serial_number']} "
                f"\nPolicy: {jss}/policies.html?id=157\nLaptop: {jss}/computers.html?id={c['id']} 💻"
            )

    if results:
        sresults = set(results)
        print(
            f"\n-------------------------------------\n"
            f"\n\033[92mJamf Laptop Lookup Results ({len(sresults)}):\033[0m {username}\n"
        )

        for ids, name in enumerate(sorted(sresults), start=1):
            print(f"{ids}, Laptop {name}")

        sorted_results = sorted(sresults)

        if len(sorted_results) > 1:
            print(
                "\nEnter a number from above or type "
                "\033[92mALL\033[0m to check-in all laptops:\n"
            )
        else:
            print(
                "\nEnter the number from above to check-in the laptop:\n"
            )

        while True:
            chosen = input()
            if chosen.upper() == "ALL":
                for c in sorted_results:
                    update_room(c, token)
                break
            elif chosen.isdigit():
                if int(chosen) <= len(sorted_results) and int(chosen) > 0:
                    update_room(sorted_results[int(chosen) - 1], token)
                    break
                else:
                    print(
                        f"\n\033[91mError\033[0m: {chosen} is not a valid option, try again below\n"
                    )
            else:
                print(
                    f"\n\033[91mError\033[0m: {chosen} is not a valid option, try again below\n"
                )
    else:
        print(f"\n\033[91mError\033[0m: No ready computers found for {username}")
        invalidateToken(token)
        exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n\033[91mError\033[0m: {e}")
        secret.signout(deauthorize=True)
        exit(1)
    except KeyboardInterrupt:
        print("\n\n\033[91mExiting...\033[0m")
        invalidateToken(getBearerToken())
        secret.signout(deauthorize=True)
        exit(1)
