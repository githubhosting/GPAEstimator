from RITScraping import sis_micro, exam_micro


def main():
	sis_stats = sis_micro("1MS21CS001", odd=True)
	exam_stats = exam_micro("1MS21CS001", even=True)
	print(sis_stats)
	print(exam_stats)


if __name__ == '__main__':
	main()
