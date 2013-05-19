# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, vs2010

def getProjectKeyword(base, make, ctx):
	use_mfc = make.get('use-mfc', ctx)
	return 'MFCProj' if use_mfc and use_mfc[0] == True else base(make, ctx)

def outputGeneralProjectProperty(base, f, make, project, cfg):
	base(f, make, project, cfg)

	ctx = cfg['ctx']
	use_mfc = make.get('use-mfc', ctx)
	if use_mfc == None or use_mfc[0] != True:
		return

	f.write('    <UseOfMfc>' + api.translate(make.get('mfc_type', ctx), {'dynamic': 'Dynamic', 'static': 'Static'}, 'Dynamic') + '</UseOfMfc>\n')

def install():
	vs2010.getProjectKeyword = api.hook(vs2010.getProjectKeyword, getProjectKeyword)
	vs2010.outputGeneralProjectProperty = api.hook(vs2010.outputGeneralProjectProperty, outputGeneralProjectProperty)
