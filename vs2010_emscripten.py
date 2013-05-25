# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, vs2010

def getBinaryExt(base, type, target):
	if target == 'emscripten':
		return {
			'staticlib': '.a',
			'dynamiclib': '.so',
			'executable': '.js'
		}[type]
	return base(type, target)

def platformFromTargetArchitecture(base, target, arch):
	return 'Emscripten' if target == 'emscripten' else base(target, arch)
def platformImpliesArch(base, platform):
	return True if platform == 'Emscripten' else base(platform)

#def formatTargetDependency(base, cfg, link):
#	return ('-l' + link) if cfg['ctx']['target'] == 'emscripten' else base(cfg, link)

def install():
	vs2010.platformFromTargetArchitecture = api.hook(vs2010.platformFromTargetArchitecture, platformFromTargetArchitecture)
	vs2010.platformImpliesArch = api.hook(vs2010.platformImpliesArch, platformImpliesArch)
	vs2010.getBinaryExt = api.hook(vs2010.getBinaryExt, getBinaryExt)
