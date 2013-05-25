# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, vs2010

def getBinaryExt(base, type, target):
	if target == 'android':
		return {
			'staticlib': '.a',
			'dynamiclib': '.so',
			'executable': '.elf'
		}[type]
	return base(type, target)

def platformFromTargetArchitecture(base, target, arch):
	return 'Android' if target == 'android' and arch in ['ARMv7', 'ARMv5', 'Mips', 'x86'] else base(target, arch)

def outputGeneralProjectProperty(base, f, make, project, cfg):
	base(f, make, project, cfg)

	ctx = cfg['ctx']
	if ctx['target'] != 'android':
		return

	android_arch = api.translate(ctx['arch'], {'ARMv7': 'armv7-a', 'ARMv5': 'armv5te', 'Mips': 'mips', 'x86': 'x86'}, None)
	if android_arch != None:
		f.write('    <AndroidArch>' + android_arch + '</AndroidArch>\n')

	android_toolset_version = make.get('android_toolset', ctx)
	android_toolset = None
	if ctx['arch'] in {'ARMv7', 'ARMv5'}:
		android_toolset = api.translate(android_toolset_version, {'4.6': 'arm-linux-androideabi-4.6', '4.4.3': 'arm-linux-androideabi-4.4.3'}, None)
	elif ctx['arch'] == 'Mips':
		android_toolset = api.translate(android_toolset_version, {'4.6': 'mipsel-linux-android-4.6', '4.4.3': 'mipsel-linux-android-4.4.3'}, None)
	elif ctx['arch'] == 'x86':
		android_toolset = api.translate(android_toolset_version, {'4.6': 'x86-4.6', '4.4.3': 'x86-4.4.3'}, None)
	if	android_toolset != None:			
		f.write('	<PlatformToolset>' + android_toolset + '</PlatformToolset>\n')

	android_api_level = api.translate(make.get('android-api-level', ctx), {'4.0': 'android-14', '2.3': 'android-9', '2.2': 'android-8', '2.0': 'android-5'}, None)
	if	android_api_level != None:
		f.write('    <AndroidAPILevel>' + android_api_level + '</AndroidAPILevel>\n')

def formatTargetDependency(base, cfg, link):
	return ('-l' + link) if cfg['ctx']['target'] == 'android' else base(cfg, link)

def install():
	vs2010.platformFromTargetArchitecture = api.hook(vs2010.platformFromTargetArchitecture, platformFromTargetArchitecture)
	vs2010.outputGeneralProjectProperty = api.hook(vs2010.outputGeneralProjectProperty, outputGeneralProjectProperty)
	vs2010.formatTargetDependency = api.hook(vs2010.formatTargetDependency, formatTargetDependency)
	vs2010.getBinaryExt = api.hook(vs2010.getBinaryExt, getBinaryExt)
