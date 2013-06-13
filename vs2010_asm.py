# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, vs2010, os

asm_ext = ['.asm', '.s']

#------------------------------------------------------------------------------
def getFileCategory(base, project, file, output_path):
	ext = api.getFileExt(file['name'])

	cat = None
	if ext in asm_ext:
		cat = 'custom_files'

	return cat if cat else base(project, file, output_path)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputCustomFileClDirective(base, f, make, project, file, output_path):
	base(f, make, project, file, output_path)

	ext = api.getFileExt(file['name'])

	if ext in asm_ext:
		f.write('      <FileType>Document</FileType>\n')
		for cfg in project['configurations']:
			f.write('      <Message ' + vs2010.getCondition(cfg) + '>Assembling %(Identity)...</Message>\n')
			f.write('      <Outputs ' + vs2010.getCondition(cfg) + '>%(Filename).obj;%(Outputs)</Outputs>\n')
			f.write('      <Command ' + vs2010.getCondition(cfg) + '>ml64 /c "%(FullPath)"</Command>\n')
#------------------------------------------------------------------------------

def install():
	vs2010.getFileCategory = api.hook(vs2010.getFileCategory, getFileCategory)
	vs2010.outputCustomFileClDirective = api.hook(vs2010.outputCustomFileClDirective, outputCustomFileClDirective)
