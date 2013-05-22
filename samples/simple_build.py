# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import api, smack, vs2010

cpp_filter = ['*.cpp', '*.h']

make = smack.make()

# set the current workspace filter to 'Solution'
make.setWorkspace('Solution')

# set the current project filter to 'HelloWorld'
make.setProject('HelloWorld')

# set build configuration values for the project 'HelloWorld' in the workspace 'Solution'
make.set('type', 'executable')
make.set('include_path', 'd:/HelloWorld/include')
make.set('files', api.inputs().addFile('d:/HelloWorld/source/main.cpp'))

# set the current build filter to 'SingleDebugBuild'
make.setBuild('SingleDebugBuild')

# set build configuration for the build 'SingleDebugBuild' of the project 'HelloWorld' in the workspace 'Solution'
make.set('cflags', ['debug', 'O0'])
make.set('define', '_DEBUG')

# toolchains to generate
toolchains = [
	{
		'target': 'windows',
		'arch': ['x86', 'x64'],
	},
]

# the generator will now build a solution for each workspace/project and build with a configuration value defined
vs2010.generate(make, toolchains, 'vs2010')
