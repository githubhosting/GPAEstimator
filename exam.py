import time

# from image import show_img
from scraper import Scraper

D_URL = "https://exam.msrit.edu"
T_URL = f"{D_URL}/eresultseven/"
HEAD = "1MS"
YEAR = "21"
DEPT = "CI"
TOLERATE = 5
SLEEP = 0.125
S = Scraper()


def get_payload():
    # soup = S.get_soap(T_URL)
    # captcha = show_img(S.get_img(soup.body.find(id="captchaCode0")['src']))
    captcha = ""
    return {"usn": "", "osolCatchaTxt": captcha, "osolCatchaTxtInst": "0", "option": "com_examresult", "task": "getResult"}


def get_stats(payload):
    soup = S.get_soap(T_URL, "POST", payload)
    body = soup.body
    try:
        return {
            "name": body.find_all("h3")[0].text,
            "usn": payload["usn"],
            "sgpa": float(body.find_all("p")[3].text),
            "photo": D_URL + body.find_all("img")[1]['src'],
        }
    except IndexError:
        return
    except ValueError:
        return


if __name__ == '__main__':
    pl = get_payload()
    tol = TOLERATE
    i = 1
    S.start_session()
    with open(f"results_{DEPT}_{YEAR}.csv", "w+") as file:
        file.write((stat := f"{'name':64},{'usn':{len(HEAD+YEAR+DEPT)+3+5}},{'sgpa':5},photo") + "\n")
        print(stat)
        while tol > 0:
            time.sleep(SLEEP)
            pl["usn"] = f"{HEAD}{YEAR}{DEPT}{i:03}".lower()
            i += 1
            if not (stats := get_stats(pl)):
                tol -= 1
                continue
            tol = TOLERATE
            file.write((stat := f"{stats['name']:64},{stats['usn']:{len(HEAD+YEAR+DEPT)+3+5}},{stats['sgpa']:5.2f},{stats['photo']}") + "\n")
            print(stat)
    S.stop_session()
