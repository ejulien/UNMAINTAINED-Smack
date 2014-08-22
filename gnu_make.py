# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import os, copy, api, smack

#------------------------------------------------------------------------------
def outputHeader(f):
	f.write('# smack GNU makefile generator\n')
	f.write('# Emmanuel Julien 2013\n\n')

#------------------------------------------------------------------------------
def isTargetSupported(target):
	return target == 'linux'

def getTargetBuildEnv(target, arch):
	if target == 'linux' and arch == 'x86':
		return {'CXX': ['g++'], 'CFLAGS': [''], 'LDFLAGS': ['-pthread']}
	return None

def getOutputFilename(file, output_path):
	return api.getRelativePath(file, output_path)

#------------------------------------------------------------------------------
def isCompilationUnit(unit):
	l = unit.lower()
	for ext in ['.cpp', '.cxx', '.cc', '.c']:
		if l.endswith(ext):
			return True
	return False

def getCompilationUnitCommand(unit, ctx):
	cu_commands = {'.cpp': '$(CXX)', '.cxx': '$(CXX)', '.cc': '$(CXX)', '.cp': '$(CXX)'}
	if unit['ext'].lower() in cu_commands:
		return cu_commands[unit['ext']]
	return '$(CC)'

def getCompilationUnitObject(unit, obj_path, ctx):  # 'the target' in Make talk
	return obj_path + '/' + unit['basename'] + '.o'

def isCppCompilationUnit(unit):
	l = unit['ext'].lower()
	for ext in ['.cpp', '.cxx']:
		if l == ext:
			return True
	return False

def getCompilationUnitCFlags(unit, cflags, ctx):
	cmds = ['-c']
	if isCppCompilationUnit(unit) and 'c++11' in cflags:
		cmds.append('-std=c++11')
	return ' '.join(cmds)

def getCompilationUnitDependencies(unit):
	deps = []
	deps.append(unit)
	return deps

#------------------------------------------------------------------------------
def get_project_cflags_varname(prj):
	return prj['name'].upper() + '_CFLAGS'

def outputCompilationUnitBuildDirective(f, make, ctx, cflags, prj, unit, output_path):
	f.write('\t' + getCompilationUnitCommand(unit, ctx) + ' $(' + get_project_cflags_varname(prj) + ') ' + getCompilationUnitCFlags(unit, cflags, ctx) + ' -o ' + unit['obj'] + ' ' + api.getRelativePath(unit['file'], output_path) + '\n')

def outputProjectCompilationUnits(f, make, ctx, prj):
	# output compilation units
	for unit in prj['units']:
		f.write(unit['obj'] + ' ')

def outputStaticLibBuildDirective(f, make, ctx, prj, output_path):
	f.write('\tar rcs ' + prj['obj'] + ' ')
	outputProjectCompilationUnits(f, make, ctx, prj)

def outputDynamicLibBuildDirective(f, make, ctx, prj, output_path):
	return

def outputExecutableBuildDirective(f, make, ctx, prj, output_path):
	f.write('\t$(CXX) $(GLOBAL_LDFLAGS) -o ' + prj['obj'] + ' ')
	outputProjectCompilationUnits(f, make, ctx, prj)

	# linkage
	f.write('-L' + prj['bin_path'] + ' ')
	for plink in prj['plinks']:
		f.write('-l' + plink['name'] + ' ')
	for llink in prj['llinks']:
		f.write('-l' + llink + ' ')

def outputProjectBuildDirective(f, make, ctx, prj, output_path):
	if prj['type'] == 'staticlib':
		outputStaticLibBuildDirective(f, make, ctx, prj, output_path)
	elif prj['type'] == 'dynamiclib':
		outputDynamicLibBuildDirective(f, make, ctx, prj, output_path)
	elif prj['type'] == 'executable':
		outputExecutableBuildDirective(f, make, ctx, prj, output_path)
	f.write('\n')

#------------------------------------------------------------------------------
def getProjectObjectBase(project, type, ctx):
	exts = {'staticlib': '.a', 'dynamiclib': '.so', 'executable': '.elf'}
	return project + exts[type] if type in exts else project + '.o'

def getProjectObject(project, type, ctx):
	base = getProjectObjectBase(project, type, ctx)
	return 'lib' + base if type == 'staticlib' else base

#------------------------------------------------------------------------------
def prepareCompilationUnits(files, obj_path, ctx):
	units = []
	for file in files:
		if not isCompilationUnit(file):
			continue
		path_split = os.path.split(file)
		file_split = os.path.splitext(path_split[1])

		unit = {'file': file, 'basename': file_split[0], 'ext': file_split[1], 'deps': getCompilationUnitDependencies(file)}
		unit['obj'] = getCompilationUnitObject(unit, obj_path, ctx)
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
	prj['obj'] = prj['bin_path'] + '/' + getProjectObject(prj['name'], prj['type'], ctx)

	prj['includes'] = make.getAcrossDependencies(deps, 'include_path', ctx)
	prj['defines'] = make.getAcrossDependencies(deps, 'define', ctx)

	return prj

def outputProjectCFlags(f, ctx, cflags):
	# Note: C++11 support is tested at the compilation unit level to ensure that
	# it is only specified when compiling C++.
	pass

def outputProject(f, build_env, make, ctx, prj, projects, output_path):
	f.write("# Project '" + prj['name'] + "' object files.\n")

	# project cflags
	f.write(get_project_cflags_varname(prj) + ' = $(GLOBAL_CFLAGS) ')

	cflags = make.get('cflags', ctx)
	outputProjectCFlags(f, ctx, cflags)

	if len(prj['includes']) > 0 or len(prj['defines']) > 0:
		for include in prj['includes']:
			f.write('-I' + api.getRelativePath(include, output_path) + ' ')
		for define in prj['defines']:
			f.write('-D' + define + ' ')
	f.write('\n\n')

	# project prerequesites rules
	prj_req_rules = []
	if prj['obj_path']:  # object output path
		prj_req_rules.append(prj['obj_path'])
	if prj['bin_path']:  # binary output path
		prj_req_rules.append(prj['bin_path'])

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
		link_prj = getProject(link)	 # is it a workspace project?
		if link_prj:
			if link_prj['type'] == 'staticlib':
				prj['plinks'].append(link_prj)
		else:
			prj['llinks'].append(link)

	# compilation unit rule targets
	for unit in prj['units']:
		f.write(unit['obj'] + ': ')
		for dep in unit['deps']:
			f.write(api.getRelativePath(dep, output_path) + ' ')

		# directories are order-only prerequisites (right of the pipe, in a typical braindead GNU bullying way)
		f.write('| ' + ' '.join(prj_req_rules) + ' ')
		f.write('\n')

		outputCompilationUnitBuildDirective(f, make, ctx, cflags, prj, unit, output_path)

	f.write('\n')

	# project dependencies
	f.write(prj['obj'] + ': ')
	if prj['plinks']:
		for plink in prj['plinks']:
			f.write(plink['obj'] + ' ')
	for unit in prj['units']:
		f.write(unit['obj'] + ' ')
	f.write('\n')

	outputProjectBuildDirective(f, make, ctx, prj, output_path)

	#
	f.write('\n')

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

	# build output directory list
	obj_paths, bin_paths = [], []
	for prj in make_projects:
		if prj['obj_path'] and prj['obj_path'] not in obj_paths:
			obj_paths.append(prj['obj_path'])
		if prj['bin_path'] and prj['bin_path'] not in bin_paths:
			bin_paths.append(prj['bin_path'])

	# output global rules
	f.write('# Global rules.\n')
	f.write('.PHONY: all clean\n\n')

	f.write('all: %s\n\n' % ' '.join([prj['obj'] for prj in make_projects]))

	f.write('debug: CXX += -g3 -O0\n')
	f.write('debug: CC += -g3 -O0\n')
	f.write('debug: all\n')

	f.write('\n')

	f.write('clean:\n')
	for path in obj_paths:
		f.write('\trm -drf ' + path + '\n')
	for path in bin_paths:
		f.write('\trm -drf ' + path + '\n')

	f.write('\n')

	# output directories rules
	f.write('# Output directory rules.\n')
	for path in obj_paths:
		f.write('%s:\n\t%s\n' % (path, 'mkdir -p ' + path))
	for path in bin_paths:
		f.write('%s:\n\t%s\n' % (path, 'mkdir -p ' + path))
	f.write('\n')

	# output projects
	for prj in make_projects:
		outputProject(f, build_env, make, ctx.clone({'project': prj['name']}), prj, make_projects, output_path)

#------------------------------------------------------------------------------
def outputFlag(f, flag, key, build_env):
	if key not in build_env:
		return
	f.write(flag + ' = ')
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
def generate(make, toolchains, output_path):
	api.log('GNU makefile generator', 0)
	api.log('Target directory: ' + output_path, 1)

	if not os.path.exists(output_path):
	    os.makedirs(output_path)

	# retrieve all workspaces
	workspaces = make.getConfigurationKeyValues('workspace')

	# process all workspaces
	for workspace in workspaces:
		builds = make.getConfigurationKeyValuesFilterByContext('build', smack.context({'workspace': workspace}))  # all build in this workspace

		for toolchain in toolchains:
			target = toolchain['target']
			if not isTargetSupported(target):
				print("Skipping unsupported target '%s'.\n" % target)
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

