from RITScraping import sis_micro, exam_micro


def main():
	sis_stats = sis_micro("1MS21CI049", odd=True)
	print(sis_stats["marks"])


if __name__ == '__main__':
	main()
