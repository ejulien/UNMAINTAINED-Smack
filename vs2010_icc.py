# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, vs2010

def getPlatformToolset(base, make, ctx):
	use_icc = make.get('use_icc', ctx)
	return ('Intel C++ Compiler XE ' + use_icc) if use_icc else base(make, ctx)

def outputGeneralProjectProperty(base, f, make, project, cfg):
	base(f, make, project, cfg)

	cflags = cfg['cflags']
	if 'use-ipp' in cflags:
		f.write('    <UseIntelIPP>True</UseIntelIPP>\n')

def install():
	vs2010.getPlatformToolset = api.hook(vs2010.getPlatformToolset, getPlatformToolset)
	vs2010.outputGeneralProjectProperty = api.hook(vs2010.outputGeneralProjectProperty, outputGeneralProjectProperty)
