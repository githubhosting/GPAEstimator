import os

import wget

if __name__ == '__main__':
	yn = input("IO & Network intensive task: continue?(y/n): ")
	if yn.lower() == "y":
		for sub in list(os.walk('../results'))[1:]:
			for res in sub[-1]:
				with open(f"{sub[0]}\\{res}", 'r+') as f:
					for row in f.readlines()[1:]:
						usn, name, _, photo, _ = row.split(',')
						dept, year = res.split('_')[1:]
						year = year.split('.')[0]
						path = f"photo\\{dept.strip()}\\{year}"
						if not os.path.exists(path): os.makedirs(path)
						path += f"\\{usn.strip().lower()}_{name.strip().lower().replace(' ', '#')}.png"
						print(f"[Log] Photo: {path}")
						wget.download(photo, path)
