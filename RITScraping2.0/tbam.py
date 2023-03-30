import time

from RITScraping import exam_macro, sis_macro

if __name__ == '__main__':
    YEAR = 2021
    DEPT = "CY"
    TEMP = False
    ODD = True
    EVEN = ODD
    DRY = False

    t = time.time()

    # macro query
    exam_stats = exam_macro(YEAR, DEPT, TEMP, EVEN, dry=DRY)
    usns = [int(stat['usn'][7:10]) for stat in exam_stats]
    sis_stats = sis_macro(YEAR, DEPT, usns, temp=TEMP, odd=ODD, dry=DRY)

    # micro query
    # usn = "1MS21IS129"
    # print(exam_micro(usn, even=EVEN))
    # print(sis_micro(usn, odd=ODD))

    print(f"Time taken: {time.time() - t:.2f}s")
