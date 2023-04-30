import time

from RITScraping import exam_macro, sis_macro, exam_micro, sis_micro

if __name__ == '__main__':
    YEAR = 2021
    DEPT = "IS"
    TEMP = False
    ODD = True
    EVEN = True
    DRY = False

    t = time.time()

    # macro query
    # exam_stats = exam_macro(YEAR, DEPT, TEMP, EVEN, start=1, stop=151, dry=DRY)
    # usns = [int(stat['usn'][7:10]) for stat in exam_stats if stat]
    usns = range(1, 133)
    sis_stats = sis_macro(YEAR, DEPT, usns, temp=TEMP, odd=ODD, dry=DRY)

    # micro query
    # usn = "1MS20IS136"
    # print(exam_micro(usn, even=EVEN))
    # print(sis_micro(usn, odd=False))
    # print(sis_micro(usn, odd=True))

    print(f"Time taken: {time.time() - t:.2f}s")
