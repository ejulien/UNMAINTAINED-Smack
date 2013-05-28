# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed
#
# Note: I have no idea what I'm doing. The only thing I know is that I want
# minimal rebuild when touching a file AND correct builds when touching header
# files only.

import os, copy, api, smack

#------------------------------------------------------------------------------
def outputHeader(f):
	f.write('# smack GNU makefile generator\n')
	f.write('# Emmanuel Julien 2013\n\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def isTargetSupported(target):
	return target == 'linux'

def getTargetBuildEnv(target, arch):
	if target == 'linux' and arch == 'x86':
		return {'CC': 'gcc'}
	return None

def getOutputFilename(file, output_path):
	return api.getRelativePath(file, output_path)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def isCompilationUnit(unit):
	for ext in ['.cpp', '.cc', '.c']:
		if unit.endswith(ext):
			return True
	return False

def getCompilationUnitObject(unit):		# 'the target' in Make talk
	split = os.path.split(unit)
	spext = os.path.splitext(split[1])
	return spext[0] + '.o'

def getCompilationUnitDependencies(unit):
	deps = []
#	f = open(unit)
	deps.append(unit)
	return deps
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputCompilationUnitBuildDirective(f, make, prj, unit):
	f.write('\t$(CC) $(BUILD_CFLAGS) -o $(BUILD_OBJ_PATH)/' + unit['obj'] + ' ' + unit['file'] + '\n')
def outputProjectBuildDirective(f, make, prj):
	f.write('\t$(CC) $(BUILD_LDFLAGS) -o $(BUILD_OBJ_PATH)/' + prj['obj'] + ' ')
	for unit in prj['units']:
		f.write('$(BUILD_OBJ_PATH)/' + unit['obj'] + ' ')
	f.write('\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def getProjectObject(project, type):
	exts = {'staticlib': '.a', 'dynamiclib': '.so', 'executable': '.elf'}
	return project + exts[type] if type in exts else project + '.o'
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def prepareCompilationUnits(files):
	units = []
	for file in files:
		if not isCompilationUnit(file):
			continue
		units.append({'file': file, 'obj': getCompilationUnitObject(file), 'deps': getCompilationUnitDependencies(file)})
	return units

def generateProject(build_env, make, ctx, output_path):
	prj = {'name': ctx['project'], 'ctx': ctx}

	pflags = make.get('pflags', ctx)
	if pflags and ('skip_build' in pflags):
		return None
	prj['pflags'] = pflags

	files = make.get('files', ctx)
	if not files: files = []
	skip_files = make.get('skip_files', ctx)
	if not skip_files: skip_files = []

	prj['files'] = [api.normPathForOs(file) for file in files if file not in skip_files]
	prj['units'] = prepareCompilationUnits(prj['files'])

	type = make.getBestMatch('type', ctx)
	prj['obj'] = getProjectObject(prj['name'], type)

	prj['includes'] = make.get('include_path', ctx)
	prj['defines'] = make.get('define', ctx)
	return prj

def outputProject(f, build_env, make, prj, output_path):
	f.write("# Project '" + prj['name'] + "' object files.\n")
	for unit in prj['units']:
		f.write(unit['obj'] + ':\t')
		for dep in unit['deps']:
			f.write(dep + ' ')
		f.write('\n')
		outputCompilationUnitBuildDirective(f, make, prj, unit)

	f.write('\n')
	f.write(prj['obj'] + ':\t')
	for unit in prj['units']:
		f.write(unit['obj'] + ' ')
	f.write('\n')

	if len(prj['includes']) > 0 or len(prj['defines']) > 0:
		f.write('\t$(BUILD_CFLAGS) += ')
		for include in prj['includes']:
			f.write('-I' + include + ' ')
		for define in prj['defines']:
			f.write('-D' + define + ' ')
		f.write('\n')

	outputProjectBuildDirective(f, make, prj)

	#
	f.write('\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputWorkspace(f, build_env, make, ctx, output_path):
	projects = make.getConfigurationKeyValuesFilterByContext('project', ctx)

	make_projects = []
	for project in projects:
		prj = generateProject(build_env, make, ctx.clone({'project': project}), output_path)
		if prj:
			make_projects.append(prj)

	for prj in make_projects:
		outputProject(f, build_env, make, prj, output_path)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def generate(make, toolchains, output_path):
	api.log('GNU makefile generator', 0)
	api.log('Target directory: ' + output_path, 1)

	if not os.path.exists(output_path):
	    os.makedirs(output_path)

	f = open(output_path + '/makefile', 'w')
	outputHeader(f)

	# retrieve all workspaces
	workspaces = make.getConfigurationKeyValues('workspace')
	groups = make.getConfigurationKeyValues('group')

	# process all workspaces
	for workspace in workspaces:
		builds = make.getConfigurationKeyValuesFilterByContext('build', smack.context().clone({'workspace': workspace}))	# all build in this workspace

		for toolchain in toolchains:
			target = toolchain['target']
			if not isTargetSupported(target):
				continue

			for arch in toolchain['arch']:
				build_env = getTargetBuildEnv(target, arch)
				if not build_env:
					api.log('GNU make ignoring unsupported architecture ' + arch + ' for target ' + target + '.\n', 1)
					continue
				build_env['builds'] = builds

				for group in groups:
					ctx = smack.context().clone({'workspace': workspace, 'group': group, 'target': target, 'arch': arch})
					outputWorkspace(f, build_env, make, ctx, output_path)
#------------------------------------------------------------------------------
