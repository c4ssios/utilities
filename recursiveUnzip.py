import os
import zipfile
import shutil

path = 'S:\\textures\\SurfaceMimic\\'

def unzipNoStructure(directory, zipFilePath):

	with zipfile.ZipFile(zipFilePath) as zip_file:
	    for member in zip_file.namelist():
	        filename = os.path.basename(member)
	        # skip directories
	        if not filename:
	            continue

	        # copy file (taken from zipfile's extract)
	        source = zip_file.open(member)
	        target = file(os.path.join(directory, filename), "wb")
	        with source, target:
	            shutil.copyfileobj(source, target)


def recursiveUnzip():


	for root, dirs, files in os.walk(path):
		for file in files:
			if file.endswith(".zip"):

				zipFilePath = os.path.join(root, file)
				pathToExtract = zipFilePath.replace('\\' + zipFilePath.split('\\')[-1], '')
				unzipNoStructure(pathToExtract, zipFilePath)

				print zipFilePath + ' Extracted.'

recursiveUnzip()
