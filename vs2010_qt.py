# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, vs2010, os, re

qt_filter = ['*.ui', '*.qrc']
qt_modules = {'core': 'QtCore', 'gui': 'QtGui', 'opengl': 'QtOpenGL', 'script': 'QtScript', 'webkit': 'QtWebKit', 'network': 'QtNetwork'}
qobject_re = re.compile(r'\bQ_OBJECT\b')

#------------------------------------------------------------------------------
def isQtSupportedTarget(target):	# does Qt supports this target?
	return True if target == 'windows' else False
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def getProjectKeyword(base, make, ctx):
	use_qt = make.get('qt', ctx)
	return 'Qt4VSv1.0' if use_qt != None else base(make, ctx)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def getAdditionalIncludes(base, make, cfg, output_path):
	list = base(make, cfg, output_path)
	use_qt = make.get('qt', cfg['ctx'])
	if use_qt == None:
		return list

	qt_list = '.\GeneratedFiles;$(QTDIR)\include;.\GeneratedFiles\$(Configuration);$(QTDIR)\include\qtmain;'
	mods = make.get('qt_modules', cfg['ctx'])
	if mods != None:
		for mod in mods:
			qt_list += '$(QTDIR)\\include\\' + qt_modules[mod] + ';'
	return qt_list + list

def getAdditionalDependencies(base, make, cfg, projects):
	list = base(make, cfg, projects)
	use_qt = make.get('qt', cfg['ctx'])
	if use_qt == None:
		return list

	is_debug = make.testKeyForValue('cflags', 'debug', cfg['ctx'])
	lib_suffix = 'd4.lib' if is_debug else '4.lib'

	qt_list = 'qtmaind.lib;' if is_debug else 'qtmain.lib;'
	mods = make.get('qt_modules', cfg['ctx'])
	if mods != None:
		for mod in mods:
			qt_list += qt_modules[mod] + lib_suffix + ';'
	return qt_list + list

def getAdditionalLibraryDirectories(base, make, cfg, output_path):
	list = base(make, cfg, output_path)
	use_qt = make.get('qt', cfg['ctx'])
	if use_qt == None:
		return list
	return '$(QTDIR)\lib;' + list;
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
qt_specific_files = None

def getFileCategory(base, project, file, output_path):
	global qt_specific_files
	ext = os.path.splitext(file['name'])[1].lower()

	cat = None
	if ext in ['.h', '.hpp']:
		# test header for the Q_OBJECT macro presence
		cat = 'include_files'
		with open(output_path + '\\' + file['name'], 'r') as f:
			for line in f.readlines():
				if qobject_re.search(line):
					cat = 'custom_files'
					break

		# MOC'ed headers produces additional compilation units
		if cat == 'custom_files':
			for cfg in project['configurations']:
				ctx = cfg['ctx']
				if ctx['target'] == 'windows' and ctx['arch'] == 'x86':		# TODO support x64 as well...
					moc_name = 'moc_' + os.path.splitext(os.path.basename(file['name']))[0] + '.cpp'
					moc_path = 'GeneratedFiles\\' + ctx['build'] + '\\' + moc_name
					moc_file = {'name': moc_path, 'custom_build': False, 'filter': 'GeneratedFiles\\' + ctx['build']}

					# skip building this file for all configurations but this one
					moc_file['skip_cfg'] = [c for c in project['configurations'] if c != cfg]
					qt_specific_files.append(moc_file)

	elif ext == '.qrc':
		cat = 'custom_files'

		# qrc files produces additional compilation units
		qrc_name = 'qrc_' + os.path.splitext(os.path.basename(file['name']))[0] + '.cpp'
		qrc_path = 'GeneratedFiles\\' + qrc_name
		qrc_file = {'name': qrc_path, 'custom_build': False, 'filter': 'GeneratedFiles', 'use_pch': False}	# [EJ] disable PCH for qrc produced compilation unit
		qt_specific_files.append(qrc_file)

	elif ext == '.ui':
		file_type = 'custom_files'

	return cat if cat else base(project, file, output_path)

def distributeProjectFiles(base, make, project, output_path):
	global qt_specific_files
	qt_specific_files = []

	base(make, project, output_path)

	project['files'].extend(qt_specific_files)
	project['source_files'].extend(qt_specific_files)	# MOC are standard c++
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputCustomFileClDirective(base, f, make, project, file, output_path):
	base(f, make, project, file, output_path)

	ext = api.getFileExt(file['name'])

	if ext == '.h':
		for cfg in project['configurations']:
			if isQtSupportedTarget(cfg['ctx']['target']):
				basename = os.path.basename(file['name'])
				f.write('      <AdditionalInputs ' + vs2010.getCondition(cfg) + '>$(QTDIR)\\bin\\moc.exe;%(FullPath)</AdditionalInputs>\n')
				f.write('      <Message ' + vs2010.getCondition(cfg) + '>Moc%27ing ' + basename + '...</Message>\n')
				f.write('      <Outputs ' + vs2010.getCondition(cfg) + '>.\GeneratedFiles\$(ConfigurationName)\moc_%(Filename).cpp</Outputs>\n')
				f.write('      <Command ' + vs2010.getCondition(cfg) + '>"$(QTDIR)\\bin\\moc.exe" "%(FullPath)" -o ".\\GeneratedFiles\\$(ConfigurationName)\\moc_%(Filename).cpp" ')

				defines = vs2010.getDefines(make, cfg)
				def_list = defines.split(';')
				for define in def_list:
					if define != '%(PreprocessorDefinitions)':
						f.write('-D' + define + ' ')

				includes = vs2010.getAdditionalIncludes(make, cfg, output_path)
				inc_list = includes.split(';')
				for inc in inc_list:
					if inc != '%(AdditionalIncludeDirectories)':
						if inc.startswith('..\\'):
							f.write('"-I.\\..\\..\\' + inc + '" ')
						else:
							f.write('"-I' + inc + '" ')

				# PCH support
				use_pch = make.get('use_pch', cfg['ctx'])
				if use_pch:
					f.write('"-f' + use_pch[0] + '" ')

				# end command
				f.write('"-f' + file['name'] + '"')
				f.write('</Command>\n')

	elif ext == '.qrc':
		for cfg in project['configurations']:
			if isQtSupportedTarget(cfg['ctx']['target']):
				qrc_name = 'qrc_' + os.path.splitext(os.path.basename(file['name']))[0] + '.cpp'
				f.write('      <Message ' + vs2010.getCondition(cfg) + '>Rcc%27ing %(Filename)%(Extension)...</Message>\n')
				f.write('      <Command ' + vs2010.getCondition(cfg) + '>"$(QTDIR)\\bin\\rcc.exe" -name "%(Filename)" -no-compress "%(FullPath)" -o .\\GeneratedFiles\\' + qrc_name + '</Command>\n')

				resources = make.get('qt_res', cfg['ctx'])
				if resources:
					f.write('      <AdditionalInputs ' + vs2010.getCondition(cfg) + '>%(FullPath);')
					for res in resources:
						f.write(api.getRelativePath(res, output_path, 'windows') + ';')
					f.write('%(AdditionalInputs)</AdditionalInputs>\n')

				f.write('      <Outputs ' + vs2010.getCondition(cfg) + '>.\\GeneratedFiles\\' + qrc_name + ';%(Outputs)</Outputs>\n')
		f.write('      <SubType>Designer</SubType>\n')

	elif ext == '.ui':
		f.write('      <FileType>Document</FileType>\n')
		for cfg in project['configurations']:
			if isQtSupportedTarget(cfg['ctx']['target']):
				f.write('      <AdditionalInputs ' + vs2010.getCondition(cfg) + '>$(QTDIR)\\bin\\uic.exe;%(AdditionalInputs)</AdditionalInputs>\n')
				f.write('      <Message ' + vs2010.getCondition(cfg) + '>Uic%27ing %(Identity)...</Message>\n')
				f.write('      <Outputs ' + vs2010.getCondition(cfg) + '>.\\GeneratedFiles\\ui_%(Filename).h;%(Outputs)</Outputs>\n')
				f.write('      <Command ' + vs2010.getCondition(cfg) + '>"$(QTDIR)\\bin\\uic.exe" -o ".\\GeneratedFiles\\ui_%(Filename).h" "%(FullPath)"</Command>\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputProjectExtensionTag(base, f, make, project):
	use_qt = make.get('qt', project['ctx'])
	if use_qt != None:
		f.write('    <VisualStudio>\n')
		f.write('      <UserProperties lupdateOnBuild="0" MocDir=".\GeneratedFiles\$(ConfigurationName)" MocOptions="" QtVersion_x0020_Win32="' + use_qt[0] + '" QtVersion_x0020_x64="' + use_qt[0] + '" RccDir=".\GeneratedFiles" UicDir=".\GeneratedFiles" />\n')
		f.write('    </VisualStudio>\n')
	base(f, make, project)
#------------------------------------------------------------------------------

def install():
	vs2010.getProjectKeyword = api.hook(vs2010.getProjectKeyword, getProjectKeyword)

	vs2010.getFileCategory = api.hook(vs2010.getFileCategory, getFileCategory)
	vs2010.distributeProjectFiles = api.hook(vs2010.distributeProjectFiles, distributeProjectFiles)

	vs2010.getAdditionalIncludes = api.hook(vs2010.getAdditionalIncludes, getAdditionalIncludes)
	vs2010.getAdditionalDependencies = api.hook(vs2010.getAdditionalDependencies, getAdditionalDependencies)
	vs2010.getAdditionalLibraryDirectories = api.hook(vs2010.getAdditionalLibraryDirectories, getAdditionalLibraryDirectories)

	vs2010.outputCustomFileClDirective = api.hook(vs2010.outputCustomFileClDirective, outputCustomFileClDirective)
	vs2010.outputProjectExtensionTag = api.hook(vs2010.outputProjectExtensionTag, outputProjectExtensionTag)
