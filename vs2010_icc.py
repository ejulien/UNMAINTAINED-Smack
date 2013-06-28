# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, vs2010

def getPlatformToolset(base, make, ctx):
	use_icc = make.get('use_icc', ctx)
	return ('Intel C++ Compiler XE ' + use_icc[0]) if use_icc else base(make, ctx)

def outputGeneralProjectProperty(base, f, make, project, cfg):
	base(f, make, project, cfg)
	cflags = cfg['cflags']

	# ipp
	if 'use-Parallel_Static-ipp' in cflags:
		f.write('    <UseIntelIPP>Parallel_Static</UseIntelIPP>\n')
	elif 'use-Parallel_Dynamic-ipp' in cflags:
		f.write('    <UseIntelIPP>Parallel_Dynamic</UseIntelIPP>\n')
	elif 'use-Sequential-ipp' in cflags:
		f.write('    <UseIntelIPP>Sequential</UseIntelIPP>\n')
	elif 'use-ipp' in cflags:
		f.write('    <UseIntelIPP>true</UseIntelIPP>\n')

	# mkl
	if 'use-Parallel-mkl' in cflags:
		f.write('    <UseIntelMKL>Parallel</UseIntelMKL>\n')
	elif 'use-Sequential-mkl' in cflags:
		f.write('    <UseIntelMKL>Sequential</UseIntelMKL>\n')
	elif 'use-Cluster-mkl' in cflags:
		f.write('    <UseIntelMKL>Cluster</UseIntelMKL>\n')



def getInterprocedureOptimLinkOptions(make, cfg):
	options = make.getBestMatch('link_interprocedural_optimization', cfg['ctx'])
	return options

def outputAdditionalLinkTags(base, f, make, cfg):
	base(f, make, cfg)
	InterproceduralOptimization = getInterprocedureOptimLinkOptions(make, cfg)
	if InterproceduralOptimization != None:
		f.write('      <InterproceduralOptimization>' + InterproceduralOptimization + '</InterproceduralOptimization>\n')



def install():
	vs2010.getPlatformToolset = api.hook(vs2010.getPlatformToolset, getPlatformToolset)
	vs2010.outputGeneralProjectProperty = api.hook(vs2010.outputGeneralProjectProperty, outputGeneralProjectProperty)
	vs2010.outputAdditionalLinkTags = api.hook(vs2010.outputAdditionalLinkTags, outputAdditionalLinkTags)
