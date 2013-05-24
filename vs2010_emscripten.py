# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, vs2010

def platformFromTargetArchitecture(base, target, arch):
	return 'Emscripten' if target == 'emscripten' else base(target, arch)
def platformImpliesArch(base, platform):
	return True if platform == 'Emscripten' else base(platform)

#def formatTargetDependency(base, cfg, link):
#	return ('-l' + link) if cfg['ctx']['target'] == 'emscripten' else base(cfg, link)

def install():
	vs2010.platformFromTargetArchitecture = api.hook(vs2010.platformFromTargetArchitecture, platformFromTargetArchitecture)
	vs2010.platformImpliesArch = api.hook(vs2010.platformImpliesArch, platformImpliesArch)
