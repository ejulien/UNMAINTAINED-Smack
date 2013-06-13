# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, vs2010

def platformFromTargetArchitecture(base, target, arch):
	return 'Emscripten' if target == 'emscripten' else base(target, arch)
def platformImpliesArch(base, platform):
	return True if platform == 'Emscripten' else base(platform)
def getConfigurationType(base, make, cfg):
	return 'HTMLPage' if cfg['ctx']['target'] == 'emscripten' and cfg['type'] == 'html' else base(make, cfg)

def getBinaryExt(base, type, target):
	types = {
		'staticlib': '.bc',
		'dynamiclib': '.bc',
		'executable': '.js',
		'html': '.html',
	}
	if target == 'emscripten' and type in types:
		return types[type]
	return base(type, target)

def getBinaryName(base, name, type, target):
	if target == 'emscripten':
		return name if type == 'html' or type == 'executable' else 'lib' + name
	return base(name, type, target)

def install():
	vs2010.platformFromTargetArchitecture = api.hook(vs2010.platformFromTargetArchitecture, platformFromTargetArchitecture)
	vs2010.platformImpliesArch = api.hook(vs2010.platformImpliesArch, platformImpliesArch)
	vs2010.getConfigurationType = api.hook(vs2010.getConfigurationType, getConfigurationType)
	vs2010.getBinaryName = api.hook(vs2010.getBinaryName, getBinaryName)
	vs2010.getBinaryExt = api.hook(vs2010.getBinaryExt, getBinaryExt)
