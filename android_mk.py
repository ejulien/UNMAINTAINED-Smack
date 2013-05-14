# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import os, copy, api, smack

#------------------------------------------------------------------------------
def getProject(name, projects):
	for project in projects:
		if project['name'] == name:
			return project
	return None
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputHeader(f):
	f.write('# smack NDK-BUILD makefile generator\n')
	f.write('# Emmanuel Julien 2013\n\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def filterCFlags(out, cflags, dict):
	for f in cflags:
		if f in dict:
			v = api.translate(f, dict, None)
			if v == None:
				continue
			if type(v) == list:
				out.extend(v)
			else:
				out.append(v)
			break	# only convert the first match in dict
	return out

def convertCFlags(cflags):
	out = []
	filterCFlags(out, cflags, {'W4': ['-Wall', '-Wextra'], 'W3': ['-Wall'], 'W2': None, 'W1': None, 'W0': '-w'})
	filterCFlags(out, cflags, {'fp-fast': '-ffast-math'})
	filterCFlags(out, cflags, {'O3': ['-O3', '-funroll-loops'], 'O2': '-O2', 'O1': '-O1', 'O0': '-O0'})

	if 'debug' in cflags: out.append('-g')
	if 'maxsize' in cflags: out.append('-Os')
	if 'maxspeed' in cflags: out.append('-Ofast')
	return out
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputProject(f, make, project, projects, output_path):
	# filter out unsupported types
	if project['type'] == 'executable':
		api.warning('NDK-BUILD cannot build executables', 1)
		return

	# skip project
	if project['pflags'] != None and 'skip_build' in project['pflags']:
		return

	ctx = project['ctx']
	deps = make.getDependencies(ctx)
	global_ctx = ctx.clone({'project': '@Exclude'})		# everything not in a project specific context

	f.write('# Begin project ' + ctx['project'] + '\n')
	f.write('#-------------------------------\n')
	f.write('include $(CLEAR_VARS)\n\n')

	f.write('LOCAL_MODULE := ' + ctx['project'] + '\n')

	# project cflags
	cflags = ''
	local_defines = api.substractLists(make.getAcrossDependencies(deps, 'define', ctx), make.get('define', global_ctx))
	if len(local_defines) > 0:
		for define in local_defines:
			cflags += '-D' + define + ' '

	local_cflags = api.substractLists(make.get('cflags', ctx), make.get('cflags', global_ctx))
	gflags = convertCFlags(local_cflags)
	for f in gflags:
		cflags += f + ' '

	if local_cflags != None:
		if 'short-commands' in local_cflags:
			f.write('LOCAL_SHORT_COMMANDS := true\n')

	if cflags != '':
		f.write('LOCAL_CFLAGS := ' + cflags + '\n')

	# includes
	includes = make.getAcrossDependencies(deps, 'include_path', ctx)
	if includes != None:
		f.write('LOCAL_C_INCLUDES := ')
		for include in includes:
			f.write(api.getRelativePath(include, output_path) + ' ')
		f.write('\n')

	# output files
	f.write('LOCAL_SRC_FILES := \\\n')

	files = make.get('files', ctx)
	skip_files = make.get('skip_files', ctx)
	skip_files = [api.getRelativePath(file, output_path) for file in skip_files] if skip_files != None else []
	if files != None:
		for file in files:
			ext = os.path.splitext(file)[1].lower()
			if ext in ['.c', '.cpp']:
				rel_path = api.getRelativePath(file, output_path)
				if rel_path not in skip_files:
					f.write(rel_path + ' \\\n')

	f.write('\n')

	# linkage
	if project['type'] != 'staticlib':
		l_static = ''
		l_shared = ''
		l_ldlibs = ''

		links = make.getLinksAcrossDependencies(deps, ctx)
		for link in links:
			prj = getProject(link, projects)	# is it a workspace project?
			if prj != None:
				if prj['type'] == 'staticlib':
					l_static = l_static + prj['name'] + ' '
				elif prj['type'] == 'dynamiclib':
					l_shared = l_shared + prj['name'] + ' '
			else:
				l_ldlibs = l_ldlibs + '-l' + link + ' '

		if l_static != '': f.write('LOCAL_STATIC_LIBRARIES := ' + l_static + '\n')
		if l_shared != '': f.write('LOCAL_SHARED_LIBRARIES := ' + l_shared + '\n')
		if l_ldlibs != '': f.write('LOCAL_LDLIBS := ' + l_ldlibs + '\n')

		if l_static != '' or l_shared != '' or l_ldlibs != '': f.write('\n')	# some formatting doesn't hurt

	# output project type
	f.write('include $(' + api.translate(project['type'], {'staticlib': 'BUILD_STATIC_LIBRARY', 'dynamiclib': 'BUILD_SHARED_LIBRARY'}, None) + ')\n')
	f.write('\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def generateProject(make, ctx, output_path):
	project = {}
	project['name'] = ctx['project']
	project['ctx'] = copy.deepcopy(ctx)
	project['type'] = make.getBestMatch('type', ctx)
	project['pflags'] = make.get('pflags', ctx)
	return project
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def getArchABI(arch):
	return api.translate(arch, {'ARMv7': 'armeabi-v7a', 'ARMv5': 'armeabi', 'x86': 'x86', 'Mips': 'mips', 'All': 'all'}, None)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputApplicationMk(make, ctx, toolchains, mk_projects, output_path):
	api.log("Output makefile 'Application.mk'", 1)
	f = open(output_path + '/' + 'Application.mk', 'w')
	outputHeader(f)

	# grab builds
	builds = make.getConfigurationKeyValuesFilterByContext('build', ctx)
	if len(builds) == 0:
		api.warning("No build configuration to make for this application", 1)
		return

	# output build selection
	f.write('# Select the build configuration. Possible values: ')
	first = True
	for build in builds:
		if first == False:
			f.write(', ')
		f.write('"' + build + '"')
		first = False
	f.write('.\n')
	f.write('BUILD = "' + builds[0] + '"\n')

	# output architecture selection (ugh...)
	supported_archs = []
	for toolchain in toolchains:
		if toolchain['target'] == 'android':
			for arch in toolchain['arch']:
				if getArchABI(arch) != None:
					supported_archs.append(arch)

	f.write('# Select the target architecture. Possible values: ')
	first = True
	for arch in supported_archs:
		if first == False:
			f.write(', ')
		f.write('"' + arch + '"')
		first = False
	f.write('.\n')
	f.write('ARCH = "' + supported_archs[0] + '"\n')

	f.write('\n')

	# output build rules
	for build in builds:
		for toolchain in toolchains:
			if toolchain['target'] != 'android':
				continue
			for arch in toolchain['arch']:
				abi = getArchABI(arch)
				if abi == None:
					api.warning('Unsupported architecture: ' + arch + '\n', 1)
					continue

				app_ctx = ctx.clone({'build': build, 'arch': arch, 'project': '@exclude'})	# in this build for this architecture, not specific to a project

				f.write('# Configuration for build ' + build + ' ' + arch + '\n')
				f.write('#------------------------------------------------\n')
				f.write('ifeq (${BUILD}, "' + build + '")\n')
				f.write('  ifeq (${ARCH}, "' + arch + '")\n\n')

				# app cflags
				app_cflags = ''
				defines = make.get('define', app_ctx)
				if defines != None:
					for define in defines:
						app_cflags += '-D' + define + ' '

				cflags = make.get('cflags', app_ctx)
				if cflags != None:
					gflags = convertCFlags(cflags)
					for v in gflags:
						app_cflags += v + ' '

				if app_cflags != '':
					f.write('APP_CFLAGS := ' + app_cflags + '\n')

				f.write('APP_OPTIM := ' + ('debug' if 'debug' in cflags else 'release') +'\n')
				f.write('APP_ABI := ' + abi + '\n')

				if 'use-stlport' in cflags:
					f.write('APP_STL := stlport_static\n')

				f.write('\n  endif\n')
				f.write('endif\n\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def generateMakefile(make, ctx, toolchains, output_path):
	api.log('Android makefile: ' + ctx['workspace'], 0)
	api.log('Target directory: ' + output_path, 1)
	api.warning('Build and architecture support with NDK-BUILD is done through Application.mk', 1)

	if not os.path.exists(output_path):
	    os.makedirs(output_path)

	# convert projects
	projects = make.getConfigurationKeyValuesFilterByContext('project', ctx)

	mk_projects = []
	for project in projects:
		# filter out any build specific configuration keys, they will be added to Application.mk
		mk_projects.append(generateProject(make, ctx.clone({'project': project, 'build': '@Exclude'}), output_path))

	# write Android makefile
	api.log("Output makefile 'Android.mk'", 1)
	f = open(output_path + '/' + 'Android.mk', 'w')
	outputHeader(f)
	f.write('LOCAL_PATH := $(call my-dir)\n\n')
	for project in mk_projects:
		outputProject(f, make, project, mk_projects, output_path)
	f = None

	# write Application makefile
	outputApplicationMk(make, ctx, toolchains, mk_projects, output_path)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def generate(make, toolchains, output_path):
	# retrieve all workspaces
	workspaces = make.getConfigurationKeyValues('workspace')

	# process all workspaces
	for workspace in workspaces:
		ctx = smack.context().clone({'workspace': workspace, 'target': 'android', 'group': '*'})
		generateMakefile(make, ctx, toolchains, output_path)
#------------------------------------------------------------------------------
