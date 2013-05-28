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
		return {'CFLAGS': [''], 'LDFLAGS': ['-pthread']}
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

def getCompilationUnitCommand(unit):
	cu_commands = {'.cpp': 'CXX'}
	if unit['ext'] in cu_commands:
		return cu_commands[unit['ext']]
	return 'CC'

def getCompilationUnitObject(unit, obj_path):		# 'the target' in Make talk
	return obj_path + '/' + unit['basename'] + '.o'

def getCompilationUnitDependencies(unit):
	deps = []
#	f = open(unit)
	deps.append(unit)
	return deps
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputCompilationUnitBuildDirective(f, make, prj, unit, output_path):
	f.write('\t$(' + getCompilationUnitCommand(unit['ext']) + ') $(CFLAGS) -c -o ' + unit['obj'] + ' ' + api.getRelativePath(unit['file'], output_path) + '\n')

def outputProjectCompilationUnits(f, make, prj):
	# output compilation units
	for unit in prj['units']:
		f.write(unit['obj'] + ' ')

def outputProjectBuildDirective(f, make, prj, output_path):
	# output command start
	if prj['type'] == 'staticlib':
		f.write('\tar rcs ' + prj['obj'] + ' ')
		outputProjectCompilationUnits(f, make, prj)
	elif prj['type'] == 'dynamiclib':
		return
	elif prj['type'] == 'executable':
		f.write('\t$(CC) $(GLOBAL_LDFLAGS) -o ' + prj['obj'] + ' ')

		outputProjectCompilationUnits(f, make, prj)

		f.write('-L' + prj['bin_path'] + ' ')

		# workspace project linking
		for plink in prj['plinks']:
			f.write('-l' + plink['name'] + ' ')
		# static linking for executables
		for llink in prj['llinks']:
			f.write('-l' + llink + ' ')

	f.write('\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def getProjectObject(project, type):
	exts = {'staticlib': '.a', 'dynamiclib': '.so', 'executable': '.elf'}
	return project + exts[type] if type in exts else project + '.o'
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def prepareCompilationUnits(files, obj_path, ctx):
	units = []
	for file in files:
		if not isCompilationUnit(file):
			continue
		path_split = os.path.split(file)
		file_split = os.path.splitext(path_split[1])

		unit = {'file': file, 'basename': file_split[0], 'ext': file_split[1], 'deps': getCompilationUnitDependencies(file)}
		unit['obj'] = getCompilationUnitObject(unit, obj_path)
		units.append(unit)
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

	prj['obj_path'] = 'obj/' + ctx['target'] + '/' + ctx['project']
	prj['bin_path'] = 'bin/' + ctx['target']

	prj['files'] = [api.normPathForOs(file) for file in files if file not in skip_files]
	prj['units'] = prepareCompilationUnits(prj['files'], prj['obj_path'], ctx)

	deps = make.getDependencies(ctx)
	prj['deps'] = deps

	prj['type'] = make.getBestMatch('type', ctx)
	prj['obj'] = prj['bin_path'] + '/' + getProjectObject(prj['name'], prj['type'])

	prj['includes'] = make.getAcrossDependencies(deps, 'include_path', ctx)
	prj['defines'] = make.getAcrossDependencies(deps, 'define', ctx)

	return prj

def outputProject(f, build_env, make, prj, projects, output_path):
	f.write("# Project '" + prj['name'] + "' object files.\n")

	if prj['name'] == 'unit_test':
		prj = prj

	# prepare links
	def getProject(name):
		for project in projects:
			if project['name'] == name:
				return project
		return None

	prj['plinks'] = []
	prj['llinks'] = []
	links = make.getLinksAcrossDependencies(prj['deps'], prj['ctx'])
	for link in links:
		link_prj = getProject(link)	# is it a workspace project?
		if link_prj:
			if link_prj['type'] == 'staticlib':
				prj['plinks'].append(link_prj)
		else:
			prj['llinks'].append(link)

	# compilation unit targets
	for unit in prj['units']:
		f.write(unit['obj'] + ': ')
		for dep in unit['deps']:
			f.write(api.getRelativePath(dep, output_path) + ' ')
		f.write('\n')
		outputCompilationUnitBuildDirective(f, make, prj, unit, output_path)

	f.write('\n')

	# project target
	mkdir_obj_target = None
	if prj['obj_path']:
		mkdir_obj_target = '__dep_mkdir_obj_' + prj['name']	# dependency to create the object output directory
		f.write(mkdir_obj_target + ':\n\tmkdir -p ' + prj['obj_path'] + '\n')

	mkdir_bin_target = None
	if prj['bin_path']:
		mkdir_bin_target = '__dep_mkdir_bin_' + prj['name']	# dependency to create the binary output directory
		f.write(mkdir_bin_target + ':\n\tmkdir -p ' + prj['bin_path'] + '\n')

	f.write(prj['obj'] + ': CFLAGS = $(GLOBAL_CFLAGS) ')
	if len(prj['includes']) > 0 or len(prj['defines']) > 0:
		for include in prj['includes']:
			f.write('-I' + api.getRelativePath(include, output_path) + ' ')
		for define in prj['defines']:
			f.write('-D' + define + ' ')
	f.write('\n')

	# project dependencies
	f.write(prj['obj'] + ': ')
	if mkdir_obj_target: f.write(mkdir_obj_target + ' ')
	if mkdir_bin_target: f.write(mkdir_bin_target + ' ')
	if prj['plinks']:
		for plink in prj['plinks']:
			f.write(plink['obj'] + ' ')
	for unit in prj['units']:
		f.write(unit['obj'] + ' ')
	f.write('\n')

	outputProjectBuildDirective(f, make, prj, output_path)

	#
	f.write('\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputWorkspace(f, build_env, make, ctx, output_path):
	make_projects = []

	groups = make.getConfigurationKeyValues('group')
	for group in groups:
		group_ctx = ctx.clone({'group': group})
		projects = make.getConfigurationKeyValuesFilterByContext('project', group_ctx)

		for project in projects:
			prj = generateProject(build_env, make, group_ctx.clone({'project': project}), output_path)
			if prj:
				make_projects.append(prj)

	for prj in make_projects:
		outputProject(f, build_env, make, prj, make_projects, output_path)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputFlag(f, flag, key, build_env):
	if key not in build_env:
		return
	f.write(flag + ' ?= ')
	for value in build_env[key]:
		f.write(value + ' ')
	f.write('\n')

def outputGlobals(f, build_env):
	outputFlag(f, 'CC', 'CC', build_env)
	outputFlag(f, 'CXX', 'CXX', build_env)
	outputFlag(f, 'GLOBAL_CFLAGS', 'CFLAGS', build_env)
	outputFlag(f, 'GLOBAL_LDFLAGS', 'LDFLAGS', build_env)
	f.write('\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def generate(make, toolchains, output_path):
	api.log('GNU makefile generator', 0)
	api.log('Target directory: ' + output_path, 1)

	if not os.path.exists(output_path):
	    os.makedirs(output_path)

	# retrieve all workspaces
	workspaces = make.getConfigurationKeyValues('workspace')

	# process all workspaces
	for workspace in workspaces:
		builds = make.getConfigurationKeyValuesFilterByContext('build', smack.context({'workspace': workspace}))	# all build in this workspace

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

				f = open(output_path + '/' + target + '-' + arch + '_' + workspace + '.mk', 'w')
				outputHeader(f)
				outputGlobals(f, build_env)
				outputWorkspace(f, build_env, make, smack.context({'workspace': workspace, 'target': target, 'arch': arch}), output_path)
#------------------------------------------------------------------------------
