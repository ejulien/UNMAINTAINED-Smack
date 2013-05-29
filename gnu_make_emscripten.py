# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, gnu_make

#------------------------------------------------------------------------------
def isTargetSupported(base, target):
	return True if target == 'emscripten' else base(target)

def getTargetBuildEnv(base, target, arch):
	if target == 'emscripten' and arch == 'Default':
		return {'CC': ['emcc'], 'CXX': ['emcc'], 'CFLAGS': [''], 'LDFLAGS': ['']}
	return base(target, arch)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputExecutableBuildDirective(base, f, make, prj, output_path):
	f.write('\t$(CXX) $(GLOBAL_LDFLAGS) -o ' + prj['obj'] + ' ')
	gnu_make.outputProjectCompilationUnits(f, make, prj)

	# linkage
	for plink in prj['plinks']:
		f.write(plink['obj'] + ' ')
	for llink in prj['llinks']:
		f.write('-l' + llink + ' ')

def outputStaticLibBuildDirective(base, f, make, prj, output_path):
	f.write('\t$(CXX) -o ' + prj['obj'] + ' ')
	gnu_make.outputProjectCompilationUnits(f, make, prj)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputProjectBuildDirective(base, f, make, prj, output_path):
	if prj['type'] == 'html':
		gnu_make.outputExecutableBuildDirective(f, make, prj, output_path)
	else:
		base(f, make, prj, output_path)

def getProjectObjectBase(base, project, type):
	exts = {'staticlib': '.o', 'dynamiclib': '.so', 'executable': '.js', 'html': '.html'}
	return project + exts[type] if type in exts else base(project, type)
#------------------------------------------------------------------------------

def install():
	gnu_make.isTargetSupported = api.hook(gnu_make.isTargetSupported, isTargetSupported)
	gnu_make.getTargetBuildEnv = api.hook(gnu_make.getTargetBuildEnv, getTargetBuildEnv)
	gnu_make.outputExecutableBuildDirective = api.hook(gnu_make.outputExecutableBuildDirective, outputExecutableBuildDirective)
	gnu_make.outputStaticLibBuildDirective = api.hook(gnu_make.outputStaticLibBuildDirective, outputStaticLibBuildDirective)
	gnu_make.outputProjectBuildDirective = api.hook(gnu_make.outputProjectBuildDirective, outputProjectBuildDirective)
	gnu_make.getProjectObjectBase = api.hook(gnu_make.getProjectObjectBase, getProjectObjectBase)

