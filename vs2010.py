# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import smack, copy, uuid, api, os

resource_filter = ['*.rc']

files_common_prefix = ''

#------------------------------------------------------------------------------
# generator configuration flags
output_master_solution = True

output_per_project_solution = False
per_project_solution_prefix = 'project_'

output_per_group_solution = False
per_group_solution_prefix = 'group_'

output_per_condition_solution		= False
per_condition_solution_key			= None
per_condition_solution_and_searchString = None
per_condition_solution_or_searchString = None
per_condition_solution_prefix = 'cond_'
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def getProject(projects, name):
	for prj in projects:
		if prj['name'] == name: return prj
	return None

#------------------------------------------------------------------------------
def platformImpliesArch(platform):
	return platform in ['Win32', 'x64']

def platformFromTargetArchitecture(target, arch):
	if target == 'windows':
		if		arch == 'x86': return 'Win32'
		elif	arch == 'x64': return 'x64'
	return None
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def getBinaryName(name, type, target):
	return name

def getPDBName(base, suffix):
	if suffix == None:
		suffix = ''
	else:
		suffix = suffix[0]

	return base + suffix

def getBinaryExt(type, target):
	types = {
		'staticlib': '.lib',
		'dynamiclib': '.dll',
		'executable': '.exe'
	}
	return types[type] if type in types else '.lib'
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def getCondition(cfg):
	return 'Condition="\'$(Configuration)|$(Platform)\'==\'' + cfg['qualified_name'] + '\'"'

def getWarningLevel(cflags):
	return api.translate(cflags, {'W4': 'Level4', 'W3': 'Level3', 'W2': 'Level2', 'W1': 'Level1', 'W0': 'Level0'}, 'Level3')

def getSubSystem(make, cfg):
	subsystem = make.get('subsystem', cfg['ctx'])
	return api.translate(subsystem, {'native': 'Windows', 'console': 'Console'}, 'Windows')

def getModuleDefinitionFile(make, cfg):
	moduledefinitionfile = make.getBestMatch('module_definition_file', cfg['ctx'])
	return moduledefinitionfile

def getPreBuildEventCommand(make, cfg):
	command = make.getBestMatch('pre_build_event_command', cfg['ctx'])
	return command

def getPreBuildEventMessage(make, cfg):
	message = make.getBestMatch('pre_build_event_message', cfg['ctx'])
	return message

def getPreLinkEventCommand(make, cfg):
	command = make.getBestMatch('pre_link_event_command', cfg['ctx'])
	return command

def getPreLinkEventMessage(make, cfg):
	message = make.getBestMatch('pre_link_event_message', cfg['ctx'])
	return message

def getPostBuildEventCommand(make, cfg):
	command = make.getBestMatch('post_build_event_command', cfg['ctx'])
	return command

def getPostBuildEventMessage(make, cfg):
	message = make.getBestMatch('post_build_event_message', cfg['ctx'])
	return message

def getRuntimeLibrary(make, cfg):
	runtime = make.getBestMatch('runtime_library', cfg['ctx'])
	if 'debug' in cfg['cflags']:
		return api.translate(runtime, {'dynamic': 'MultiThreadedDebugDLL', 'static': 'MultiThreadedDebug'}, 'MultiThreadedDebugDLL')
	return api.translate(runtime, {'dynamic': 'MultiThreadedDLL', 'static': 'MultiThreaded'}, 'MultiThreadedDLL')

def getAdditionalClOptions(make, cfg):
	options = make.getBestMatch('additional_Cl_options', cfg['ctx'])
	return options

def getAdditionalLinkOptions(make, cfg):
	options = make.getBestMatch('additional_link_options', cfg['ctx'])
	return options

def getUACExecutionLevel(make, cfg):
	options = make.getBestMatch('UACExecutionLevel', cfg['ctx'])
	return options

def getLibTargetMachine(make, cfg):
	options = make.getBestMatch('lib_target', cfg['ctx'])
	return options

def getAdditionalLibDependencies(make, cfg):
	options = make.getBestMatch('additional_lib_Dependencies', cfg['ctx'])
	return options

def getDefines(make, cfg):
	list = ''
	defines = make.getAcrossDependencies(cfg['deps'], 'define', cfg['ctx'])
	if defines != None:
		for define in defines:
			list += define + ';'
	return list + '%(PreprocessorDefinitions)'

def getAdditionalIncludes(make, cfg, output_path):
	list = ''
	includes = make.getAcrossDependencies(cfg['deps'], 'include_path', cfg['ctx'])
	if includes != None:
		for include in includes:
			list += api.getRelativePath(include, output_path, 'windows') + ';'
	return list + '%(AdditionalIncludeDirectories)'

def formatTargetDependency(cfg, link):
	return link + '.lib'

def getAdditionalDependencies(make, cfg, projects):
	list = ''
	links = make.getLinksAcrossDependencies(cfg['deps'], cfg['ctx'])
	if links != None:
		for link in links:
			if getProject(projects, link) == None:	# only link libraries here (projects are linked in the solution)
				list += formatTargetDependency(cfg, link) + ';'
	return list + '%(AdditionalDependencies)'

def getAdditionalLibraryDirectories(make, cfg, output_path):
	list = ''
	paths = make.getAcrossDependencies(cfg['deps'], 'lib_path', cfg['ctx'])
	if paths != None:
		for path in paths:
			list += api.getRelativePath(path, output_path, 'windows') + ';'
	return list + '%(AdditionalLibraryDirectories)'

def getDebugInformation(cflags):
	return 'EditAndContinue' if 'debug' in cflags else 'ProgramDatabase'
def getOptimization(cflags):
	return api.translate(cflags, {'maxspeed': 'MaxSpeed', 'maxsize': 'MaxSize', 'optimize': 'Full'}, 'Disabled')
def useDebugLibrairies(cflags):
	return 'true' if 'debug' in cflags else 'false'

def getUnicode(cflags):
	return 'MultiByte' if 'use-utf8' in cflags else 'Unicode'

def getFloatingPointModel(cflags):
	return api.translate(cflags, {'fp-fast': 'Fast', 'fp-strict': 'Strict'}, 'Precise')

def getUseExceptions(cflags):
	return 'Sync' if 'use-exceptions' in cflags else 'false'

def getUseRTTI(cflags):
	return 'true' if 'use-rtti' in cflags else 'false'

def getMultiProcessorCompilation(cflags):
	return 'true' if 'use-multi-processor-compilation' in cflags else 'false'

def getMinimalRebuild(cflags):
	return 'true' if 'use-minimal-rebuild' in cflags else 'false'

def getIntermediatePath(make, cfg):
	ctx = cfg['ctx']
	path = make.getBestMatch('obj_path', ctx)
	if path:
		return os.path.normpath(path + '/?')[:-1]	# trailing slash is required

	path = 'obj\\' + cfg['vsplatform']
	if platformImpliesArch(cfg['vsplatform']) == False:
		path += '\\' + ctx['arch']
	return path + '\\' + ctx['build'] + '\\' + ctx['project'] + '\\'

def getBinaryPath(make, cfg):
	ctx = cfg['ctx']
	path = make.getBestMatch('bin_path', ctx)
	if	path == None:
		path = '.'
	return os.path.normpath(path + '/?')[:-1]	# trailing slash is required

def skipProjectBuild(cfg):
	pflags = cfg['pflags']
	if pflags == None: return False
	return 'skip_build' in pflags

def getConfigurationType(make, cfg):
	return api.translate(cfg['type'], {'staticlib': 'StaticLibrary', 'dynamiclib': 'DynamicLibrary', 'executable': 'Application'}, 'StaticLibrary')

def getPlatformToolset(make, ctx):
	return make.getBestMatch('platform_toolset', ctx)

def outputGeneralProjectProperty(f, make, project, cfg):
	cflags = cfg['cflags']
	f.write('    <ConfigurationType>' + getConfigurationType(make, cfg) + '</ConfigurationType>\n')
	f.write('    <UseDebugLibraries>' + useDebugLibrairies(cflags) + '</UseDebugLibraries>\n')
	f.write('    <CharacterSet>' + getUnicode(cflags) + '</CharacterSet>\n')

	toolset = getPlatformToolset(make, cfg['ctx'])
	if toolset:
		f.write('    <PlatformToolset>' + toolset + '</PlatformToolset>\n')

def getSolutionFileName(file, output_path):
	return api.getRelativePath(file, output_path, 'windows')

def getProjectKeyword(make, project_ctx):
	return 'Win32Proj'

def openIncludeFileClDirective(f, project, file, output_path):
	f.write('    <ClInclude Include="' + file['name'] + '">\n')
def outputIncludeFileClDirective(f, make, project, file, output_path):
	return
def closeIncludeFileClDirective(f, project, file, output_path):
	f.write('    </ClInclude>\n')

def openCompileFileClDirective(f, project, file, output_path):
	f.write('    <ClCompile Include="' + file['name'] + '">\n')
def outputCompileFileClDirective(f, make, project, file, output_path):
	return
def closeCompileFileClDirective(f, project, file, output_path):
	f.write('    </ClCompile>\n')

def openCustomFileClDirective(f, project, file, output_path):
	f.write('    <CustomBuild Include="' + file['name'] + '">\n')
def outputCustomFileClDirective(f, make, project, file, output_path):
	return
def closeCustomFileClDirective(f, project, file, output_path):
	f.write('    </CustomBuild>\n')

def outputPrecompiledHeaderTags(f, make, cfg):
	use_pch = make.get('use_pch', cfg['ctx'])
	if use_pch != None:
		f.write('      <PrecompiledHeader>Use</PrecompiledHeader>\n')
		f.write('      <PrecompiledHeaderFile>' + use_pch[0] + '</PrecompiledHeaderFile>\n')

def outputProjectExtensionTag(f, make, project):
	return

def outputAdditionalLinkTags(f, make, cfg):
	return

def getFileCategory(project, file, output_path):
	ext = os.path.splitext(file['name'])[1].lower()
	if ext in ['.cpp', '.c', '.cc', '.cxx']:
		return 'source_files'
	elif ext in ['.h', '.hpp']:
		return 'include_files'
	elif ext in ['.rc']:
		return 'resource_files'
	return 'custom_files'
	
def distributeProjectFiles(make, project, output_path):
	project['source_files'] = []
	project['include_files'] = []
	project['resource_files'] = []
	project['custom_files'] = []
	for file in project['files']:
		project[getFileCategory(project, file, output_path)].append(file)

def assignProjectFilesFilter(project, output_path):
	for file in project['files']:
		if 'filter' in file:
			continue
		out = file['name']
		if 'common_prefix' in project:
			prefix = project['common_prefix']
			if out.startswith(prefix):
				out = out[len(prefix):]
		file['filter'] = os.path.dirname(out).replace('..\\', '')

def outputPCHDirective(f, project, file):
	for cfg in project['configurations']:
		if 'use_pch' in file and file['use_pch'] == False:
			f.write('      <PrecompiledHeader ' + getCondition(cfg) + '></PrecompiledHeader>\n')
		else:
			if file['name'] == cfg['create_pch']:
				f.write('      <PrecompiledHeader ' + getCondition(cfg) + '>Create</PrecompiledHeader>\n')

def outputBigObjDirective(f, project, file):
	if 'bigobj_cfg' in file:
		for cfg in file['bigobj_cfg']:
			f.write('      <AdditionalOptions ' + getCondition(cfg) + '>/bigobj %(AdditionalOptions)</AdditionalOptions>\n')

def outputNoPchDirective(f, file):
	if 'nopch_cfg' in file:
		for cfg in file['nopch_cfg']:
			f.write('      <PrecompiledHeader ' + getCondition(cfg) + '>NotUsing</PrecompiledHeader>\n')

def outputExcludeFileFromBuildDirective(f, file):
	if 'skip_cfg' in file:
		for cfg in file['skip_cfg']:
			f.write('      <ExcludedFromBuild ' + getCondition(cfg) + '>true</ExcludedFromBuild>\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputProject(make, project, projects, output_path):
	project_ctx = project['ctx']

	api.log("Output project '" + project['name'] + "'", 1)
	f = open(output_path + '/' + project['name'] + '.vcxproj', 'w')

	f.write('<?xml version="1.0" encoding="utf-8"?>\n')
	f.write('<Project DefaultTargets="Build" ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">\n')

	# configurations
	f.write('  <ItemGroup Label="ProjectConfigurations">\n')
	for cfg in project['configurations']:
		cfg['qualified_name'] = cfg['name'] + '|' + cfg['vsplatform']
		f.write('    <ProjectConfiguration Include="' + cfg['qualified_name'] + '">\n')
		f.write('      <Configuration>' + cfg['name'] + '</Configuration>\n')
		f.write('      <Platform>' + cfg['vsplatform'] + '</Platform>\n')
		f.write('    </ProjectConfiguration>\n')
	f.write('  </ItemGroup>\n')

	# global properties
	f.write('  <PropertyGroup Label="Globals">\n')
	f.write('    <ProjectGuid>{' + project['guid'] + '}</ProjectGuid>\n')
	f.write('    <RootNamespace>' + project['name'] + '</RootNamespace>\n')
	f.write('    <Keyword>' + getProjectKeyword(make, project_ctx) + '</Keyword>\n')
	f.write('  </PropertyGroup>\n')

	# store a few commonly used values directly in the configuration
	for cfg in project['configurations']:
		cfg['deps'] = make.getDependencies(cfg['ctx'])
		cfg['links'] = make.getLinksAcrossDependencies(cfg['deps'], cfg['ctx'])
		cfg['type'] = make.getBestMatch('type', cfg['ctx'])
		cfg['cflags'] = make.get('cflags', cfg['ctx'])
		cfg['pflags'] = make.get('pflags', cfg['ctx'])

	# build the project link list across all configurations (we'll disable unused ones on a per project basis in the solution)
	project['all_link'] = None
	for cfg in project['configurations']:
		project['all_link'] = api.appendToList(project['all_link'], cfg['links'])
	if project['all_link'] != None:
		project['all_link'] = list(set(project['all_link']))

	# cpp default properties
	f.write('  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.Default.props" />\n')

	# general project properties
	for cfg in project['configurations']:
		f.write('  <PropertyGroup ' + getCondition(cfg) + ' Label="Configuration">\n')
		outputGeneralProjectProperty(f, make, project, cfg)
		f.write('  </PropertyGroup>\n')

	# cpp extension settings
	f.write('  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.props" />\n')
	f.write('  <ImportGroup Label="ExtensionSettings">\n')
	f.write('  </ImportGroup>\n')

	# default props
	for cfg in project['configurations']:
		f.write('  <ImportGroup Label="PropertySheets" ' + getCondition(cfg) + '>\n')
		f.write('    <Import Project="$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props" Condition="exists(\'$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props\')" Label="LocalAppDataPlatform" />\n')
		f.write('  </ImportGroup>\n')

	# user macros
	f.write('  <PropertyGroup Label="UserMacros" />\n')

	# binary output
	for cfg in project['configurations']:
		f.write('  <PropertyGroup ' + getCondition(cfg) + '>\n')
		f.write('    <OutDir>' + getBinaryPath(make, cfg) + '</OutDir>\n')
		f.write('    <IntDir>' + getIntermediatePath(make, cfg) + '</IntDir>\n')

		target_name = make.getBestMatch('target_name', cfg['ctx'])
		if not target_name:
			target_name = getBinaryName(project['name'], cfg['type'], cfg['ctx']['target'])

		suffix = make.getBestMatch('bin_suffix', cfg['ctx'])
		if suffix:
			target_name += suffix

		target_ext = make.getBestMatch('bin_ext', cfg['ctx'])
		if not target_ext:
			target_ext = getBinaryExt(cfg['type'], cfg['ctx']['target'])

		f.write('    <TargetName>' + target_name + '</TargetName>\n')
		f.write('    <TargetExt>' + target_ext + '</TargetExt>\n')
		f.write('  </PropertyGroup>\n')

	# compiler / linker properties
	for cfg in project['configurations']:
		ctx = cfg['ctx']
		suffix = make.get('bin_suffix', ctx)

		f.write('  <ItemDefinitionGroup ' + getCondition(cfg) + '>\n')

		# compiler
		cflags = cfg['cflags']

		outDir = '$(OutDir)' if 'debug' in cfg['cflags'] else '$(IntDir)'

		f.write('    <ClCompile>\n')
		f.write('      <PrecompiledHeader>NotUsing</PrecompiledHeader>\n')
		f.write('      <WarningLevel>' + getWarningLevel(cflags) + '</WarningLevel>\n')
		f.write('      <PreprocessorDefinitions>' + getDefines(make, cfg) + '</PreprocessorDefinitions>\n')
		f.write('      <AdditionalIncludeDirectories>' + getAdditionalIncludes(make, cfg, output_path) + '</AdditionalIncludeDirectories>\n')
		f.write('      <DebugInformationFormat>' + getDebugInformation(cflags) + '</DebugInformationFormat>\n')
		f.write('      <ProgramDataBaseFileName>'+ outDir + getPDBName(project['name'], suffix) + '.pdb</ProgramDataBaseFileName>\n')
		f.write('      <Optimization>' + getOptimization(cflags) + '</Optimization>\n')
		f.write('      <ExceptionHandling>' + getUseExceptions(cflags) + '</ExceptionHandling>\n')
		f.write('      <RuntimeTypeInfo>' + getUseRTTI(cflags) + '</RuntimeTypeInfo>\n')
		f.write('      <FloatingPointModel>' + getFloatingPointModel(cflags) + '</FloatingPointModel>\n')
		
		if 'omit-frame-pointers' in cflags:
			f.write('      <OmitFramePointers>true</OmitFramePointers>\n')

		f.write('      <RuntimeLibrary>' + getRuntimeLibrary(make, cfg) + '</RuntimeLibrary>\n')

		f.write('      <MultiProcessorCompilation>' + getMultiProcessorCompilation(cflags) + '</MultiProcessorCompilation>\n')
		f.write('      <MinimalRebuild>' + getMinimalRebuild(cflags) + '</MinimalRebuild>\n')

		additionalClOptions = getAdditionalClOptions(make, cfg)
		if additionalClOptions != None:
			f.write('      <AdditionalOptions>' + additionalClOptions + ' %(AdditionalOptions)</AdditionalOptions>\n')

		align_dict = {'struct-member-align-1': 1, 'struct-member-align-2': 2, 'struct-member-align-4': 4, 'struct-member-align-8': 8, 'struct-member-align-16': 16}
		for key in align_dict.keys():
			if key in cflags:
				f.write('      <StructMemberAlignment>' + str(align_dict[key]) + 'Bytes</StructMemberAlignment>\n')
				break

		if 'use-sse2' in cflags:
			f.write('      <EnableEnhancedInstructionSet>StreamingSIMDExtensions2</EnableEnhancedInstructionSet>\n')

		outputPrecompiledHeaderTags(f, make, cfg)
		f.write('    </ClCompile>\n')

		f.write('    <Link>\n')
		f.write('      <SubSystem>' + getSubSystem(make, cfg) + '</SubSystem>\n')
		f.write('      <AdditionalDependencies>' + getAdditionalDependencies(make, cfg, projects) + '</AdditionalDependencies>\n')
		f.write('      <AdditionalLibraryDirectories>' + getAdditionalLibraryDirectories(make, cfg, output_path) +'</AdditionalLibraryDirectories>\n')
		f.write('      <GenerateDebugInformation>' + ('True' if ('debug' in cfg['cflags']) else 'False') + '</GenerateDebugInformation>\n')

		ModuleDefFile = getModuleDefinitionFile(make, cfg);
		if (ModuleDefFile != None):
			f.write('      <ModuleDefinitionFile>' + ModuleDefFile + '</ModuleDefinitionFile>\n')

		additionalLinkOptions = getAdditionalLinkOptions(make, cfg)
		if additionalLinkOptions != None:
			f.write('      <AdditionalOptions>' + additionalLinkOptions + ' %(AdditionalOptions)</AdditionalOptions>\n')

		UACExecutionLevel = getUACExecutionLevel(make, cfg)
		if UACExecutionLevel != None:
			f.write('      <UACExecutionLevel>' + UACExecutionLevel + '</UACExecutionLevel>\n')

		outputAdditionalLinkTags(f, make, cfg)

		f.write('    </Link>\n')

		f.write('    <Lib>\n')

		additionalLibDependencies = getAdditionalLibDependencies(make, cfg)
		if additionalLibDependencies != None:
			f.write('      <AdditionalDependencies>' + additionalLibDependencies + '</AdditionalDependencies>\n')

		LibTargetMachine = getLibTargetMachine(make, cfg)
		if LibTargetMachine != None:
			f.write('      <TargetMachine>' + LibTargetMachine + '</TargetMachine>\n')

		f.write('    </Lib>\n')

		PreBuildEventCommand = getPreBuildEventCommand(make, cfg)
		PreBuildEventMessage = getPreBuildEventMessage(make, cfg)
		if (PreBuildEventCommand != None):
			f.write('    <PreBuildEvent>\n')
			f.write('      <Command>' + PreBuildEventCommand + '</Command>\n')
			if (PreBuildEventMessage != None):
				f.write('      <Message>' + PreBuildEventMessage + '</Message>\n')
			f.write('    </PreBuildEvent>\n')


		PreLinkEventCommand = getPreLinkEventCommand(make, cfg)
		PreLinkEventMessage = getPreLinkEventMessage(make, cfg)
		if (PreLinkEventCommand != None):
			f.write('    <PreLinkEvent>\n')
			f.write('      <Command>' + PreLinkEventCommand + '</Command>\n')
			if (PreLinkEventMessage != None):
				f.write('      <Message>' + PreLinkEventMessage + '</Message>\n')
			f.write('    </PreLinkEvent>\n')

		PostBuildEventCommand = getPostBuildEventCommand(make, cfg)
		PostBuildEventMessage = getPostBuildEventMessage(make, cfg)
		if (PostBuildEventCommand != None):
			f.write('    <PostBuildEvent>\n')
			f.write('      <Command>' + PostBuildEventCommand + '</Command>\n')
			if (PostBuildEventMessage != None):
				f.write('      <Message>' + PostBuildEventMessage + '</Message>\n')
			f.write('    </PostBuildEvent>\n')

		f.write('  </ItemDefinitionGroup>\n')

	# source files
	project['files'] = []
	for cfg in project['configurations']:	# grab across all configurations
		cfg['files'] = make.get('files', cfg['ctx'])
		if cfg['files']:
			cfg['files'] = [getSolutionFileName(file, output_path) for file in cfg['files']]
			project['files'].extend(cfg['files'])

	project['files'] = list(set(project['files']))
	project['files'] = [{'name': file, 'skip_cfg': [], 'bigobj_cfg': [], 'nopch_cfg': []} for file in project['files']]

	if len(project['files']) == 0:
		api.warning("No files added to project '" + project['name'] + "' in context " + str(project_ctx), 1)

	# skipped configurations per file
	def getProjectFile(name):
		for file in project['files']:
			if file['name'] == name:
				return file
		return None

	for cfg in project['configurations']:
		skips = make.get('skip_files', cfg['ctx'])
		if skips:
			for skip in skips:
				file = getProjectFile(getSolutionFileName(skip, output_path))
				if file:
					file['skip_cfg'].append(cfg)

	for file in project['files']:
		for cfg in project['configurations']:
			if file['name'] not in cfg['files']:
				file['skip_cfg'].append(cfg)

	# PCH creation per configuration
	for cfg in project['configurations']:
		create_pch = make.get('create_pch', cfg['ctx'])
		cfg['create_pch'] = api.getRelativePath(create_pch[0], output_path, 'windows') if create_pch != None else ''

	# big obj per file
	for cfg in project['configurations']:
		nopchs = make.get('big_obj', cfg['ctx'])
		if nopchs:
			for nopch in nopchs:
				file = getProjectFile(getSolutionFileName(nopch, output_path))
				if file:
					file['bigobj_cfg'].append(cfg)

	for file in project['files']:
		for cfg in project['configurations']:
			if file['name'] not in cfg['files']:
				file['bigobj_cfg'].append(cfg)
	
	# no pch per file
	for cfg in project['configurations']:
		nopchs = make.get('no_pch', cfg['ctx'])
		if nopchs:
			for nopch in nopchs:
				file = getProjectFile(getSolutionFileName(nopch, output_path))
				if file:
					file['nopch_cfg'].append(cfg)

	for file in project['files']:
		for cfg in project['configurations']:
			if file['name'] not in cfg['files']:
				file['nopch_cfg'].append(cfg)

	# distribute over file categories	
	distributeProjectFiles(make, project, output_path)

	# output include files
	f.write('  <ItemGroup>\n')
	for file in project['include_files']:
		openIncludeFileClDirective(f, project, file, output_path)
		outputIncludeFileClDirective(f, make, project, file, output_path)
		closeIncludeFileClDirective(f, project, file, output_path)
	f.write('  </ItemGroup>\n')

	# output compilation units
	f.write('  <ItemGroup>\n')
	for file in project['source_files']:
		openCompileFileClDirective(f, project, file, output_path)
		outputCompileFileClDirective(f, make, project, file, output_path)
		outputPCHDirective(f, project, file)
		outputBigObjDirective(f, project, file)
		outputNoPchDirective(f, file)
		outputExcludeFileFromBuildDirective(f, file)
		closeCompileFileClDirective(f, project, file, output_path)
	f.write('  </ItemGroup>\n')

	# output resource compilation
	f.write('  <ItemGroup>\n')
	for file in project['resource_files']:
		f.write('    <ResourceCompile Include=\"' + file['name'] + '\" />\n')
	f.write('  </ItemGroup>\n')

	# output custom units
	f.write('  <ItemGroup>\n')
	for file in project['custom_files']:
		openCustomFileClDirective(f, project, file, output_path)
		outputCustomFileClDirective(f, make, project, file, output_path)
		outputPCHDirective(f, project, file)
		outputBigObjDirective(f, project, file)
		outputNoPchDirective(f, file)
		outputExcludeFileFromBuildDirective(f, file)
		closeCustomFileClDirective(f, project, file, output_path)
	f.write('  </ItemGroup>\n')

	# project dependencies
	common_links = copy.deepcopy(project['all_link'])	# links common to all configurations
	for cfg in project['configurations']:
		if cfg['links'] != None:
			common_links = [link for link in common_links if link in cfg['links']]

	for cfg in project['configurations']:				# links specific to this configuration
		if cfg['links'] != None:
			cfg['cfg_links'] = [link for link in cfg['links'] if link not in common_links]

	if common_links and len(common_links) > 0:
		f.write('  <ItemGroup>\n')
		for link in common_links:
			prj = getProject(projects, link)
			if prj != None:
				f.write('    <ProjectReference Include="' + prj['name'] +'.vcxproj">\n')
				f.write('      <Project>{' + prj['guid'] +'}</Project>\n')
				f.write('    </ProjectReference>\n')
		f.write('  </ItemGroup>\n')

	for cfg in project['configurations']:
		if 'cfg_links' in cfg and len(cfg['cfg_links']) > 0:
			f.write('  <ItemGroup ' + getCondition(cfg) + '>\n')
			for link in cfg['cfg_links']:
				prj = getProject(projects, link)
				if prj != None:
					f.write('    <ProjectReference Include="' + prj['name'] +'.vcxproj">\n')
					f.write('      <Project>{' + prj['guid'] +'}</Project>\n')
					f.write('    </ProjectReference>\n')
			f.write('  </ItemGroup>\n')

	# extensions
	f.write('  <Import Project="$(VCTargetsPath)\Microsoft.Cpp.targets" />\n')
	f.write('  <ImportGroup Label="ExtensionTargets">\n')
	f.write('  </ImportGroup>\n')

	f.write('  <ProjectExtensions>\n')
	outputProjectExtensionTag(f, make, project)
	f.write('  </ProjectExtensions>\n')

	# project done, next!
	f.write('</Project>\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def generateProject(make, ctx, toolchains, output_path):
	api.log("Generating project '" + ctx['project'] + "'...", 1)

	# begin generation
	project = {}
	project['ctx'] = copy.deepcopy(ctx)
	project['group'] = ctx['group']
	project['name'] = ctx['project']
	project['guid'] = str(uuid.uuid4()).upper()

	# configurations
	project['configurations'] = []

	# get builds
	builds = make.getConfigurationKeyValuesFilterByContext('build', ctx)

	for build in builds:
		for toolchain in toolchains:

			# generate a configuration for each targeted architecture
			for arch in toolchain['arch']:
				target = toolchain['target']
				vsplatform = platformFromTargetArchitecture(target, arch)

				if vsplatform == None:
					api.log('Ignoring unsupported target ' + target + ' on architecture ' + arch, 1)
					continue

				# setup configuration
				cfg = {'ctx': ctx.clone({'arch': arch, 'build': build, 'target': target}), 'vsplatform': vsplatform}

				if platformImpliesArch(vsplatform) == True:
					cfg['name'] = build
				else:
					cfg['name'] = build + ' ' + vsplatform + ' ' + arch

				project['configurations'].append(cfg)

	return project
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def getSolutionPlatformsFromProjects(projects):
	platforms = []
	for prj in projects:
		for cfg in prj['configurations']:
			platforms.append(cfg['qualified_name'])
	return list(set(platforms))

def outputSolutionLevelProjectDependencies(f, project, projects):
	if project['all_link'] == None:
		return
	link_list = []
	for link in project['all_link']:
		link_prj = getProject(projects, link)
		if link_prj != None:
			link_list.append(link_prj)
	if len(link_list) > 0:
		f.write('	ProjectSection(ProjectDependencies) = postProject\n')
		for link_prj in link_list:
			f.write('		{' + link_prj['guid'] + '} = {' + link_prj['guid'] + '}\n')
		f.write('	EndProjectSection\n')

def outputSolution(make, ctx, projects, output_path, output_name = None):
	solution = {}
	solution['guid'] = str(uuid.uuid4()).upper()


	fullPath = output_path + '/' + (output_name if output_name else ctx['workspace']) + '.sln'
	api.log('output solution: ' + fullPath)

	f = open(fullPath, 'w')

	f.write('Microsoft Visual Studio Solution File, Format Version 11.00\n')
	f.write('# Visual Studio 2010\n')

	# output projects
	for prj in projects:
		f.write('Project("{' + solution['guid'] + '}") = "' + prj['name'] + '", "' + prj['name'] + '.vcxproj", "{' + prj['guid'] + '}"\n')
		# this does not seem mandatory and I'm not too sure how this plays with the conditional references in the project files)
		# outputSolutionLevelProjectDependencies(f, prj, projects)
		f.write('EndProject\n')

	# solution folder
	groups = make.getConfigurationKeyValues('group')

	root_guid = '2150E333-8FDC-42A3-9474-1A3956D46DE8'	# solution folder guid
	group_projects = []
	for group in groups:
		if len([p for p in projects if p['group'] == group]) == 0:
			continue # make sure we have at least one project in this group before outputing it

		grp = {'name': group, 'root_guid': root_guid, 'guid': str(uuid.uuid4()).upper()}
		f.write('Project("{' + grp['root_guid'] + '}") = "' + group + '", "' + group + '", "{' + grp['guid'] + '}"\n')
		f.write('EndProject\n')
		group_projects.append(grp)

	f.write('Global\n')

	# pre solution
	f.write('	GlobalSection(SolutionConfigurationPlatforms) = preSolution\n')
	platforms = getSolutionPlatformsFromProjects(projects)
	for platform in platforms:
		f.write('		' + platform + ' = ' + platform + '\n')
	f.write('	EndGlobalSection\n')

	# post solution
	f.write('	GlobalSection(ProjectConfigurationPlatforms) = postSolution\n')
	for prj in projects:
		for cfg in prj['configurations']:
			f.write('		{' + prj['guid'] + '}.' + cfg['qualified_name'] + '.ActiveCfg = ' + cfg['qualified_name'] + '\n')
			if skipProjectBuild(cfg) == False:
				f.write('		{' + prj['guid'] + '}.' + cfg['qualified_name'] + '.Build.0 = ' + cfg['qualified_name'] + '\n')
	f.write('	EndGlobalSection\n')

	# project in solution folder
	if len(group_projects) > 0:
		f.write('	GlobalSection(NestedProjects) = preSolution\n')
		for group in group_projects:
			group_projects = make.getConfigurationKeyValuesFilterByContext('project', ctx.clone({'group': group['name']}), False)
			if group_projects != None:
				for name in group_projects:
					prj = getProject(projects, name)
					if prj != None:
						f.write('		{' + prj['guid'] + '} = {' + group['guid'] + '}\n')
		f.write('	EndGlobalSection\n')

	f.write('EndGlobal\n')
	return solution
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def outputSolutionFilters(make, ctx, projects, output_path):
	for project in projects:
		f = open(output_path + '/' + project['name'] + '.vcxproj.filters', 'w')

		f.write('<?xml version="1.0" encoding="utf-8"?>\n')
		f.write('<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">\n')

		f_files = []
		for file in project['files']:
			f_files.append(file['name'])
		project['common_prefix'] = os.path.commonprefix(f_files)

		assignProjectFilesFilter(project, output_path)

		# filter list
		def insertSolutionFilter(filter):
			nodes = filter.lstrip('\\').split('\\')
			path = ''
			if len(nodes) > 0:
				for node in nodes:
					path += node
					filters.append(path)
					path += '\\'

		filters = []
		for file in project['files']:
			if file['filter']:
				insertSolutionFilter(file['filter'])
		filters = list(set(filters))

		f.write('  <ItemGroup>\n')
		for filter in filters:
			if filter != '':
				f.write('    <Filter Include="' + filter + '">\n')
				f.write('      <UniqueIdentifier>{' + str(uuid.uuid4()).upper() + '}</UniqueIdentifier>\n')
				f.write('    </Filter>\n')
		f.write('  </ItemGroup>\n')

		# include/source/resource/custom elements
		def outputItemGroup(f, list, tag):
			f.write('  <ItemGroup>\n')
			for item in list:
				if item['filter']:
					f.write('    <' + tag + ' Include="' + item['name'] + '">\n')
					f.write('      <Filter>' + item['filter'].lstrip('\\') + '</Filter>\n')
					f.write('    </' + tag + '>\n')
			f.write('  </ItemGroup>\n')

		outputItemGroup(f, project['include_files'], 'ClInclude')
		outputItemGroup(f, project['source_files'], 'ClCompile')
		outputItemGroup(f, project['resource_files'], 'ResourceCompile')
		outputItemGroup(f, project['custom_files'], 'CustomBuild')
		f.write('</Project>\n')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def collectVSProjectDependencies(project, vs_projects):
	if not project['all_link']:
		return []
	links = []
	for name in project['all_link']:
		links.extend([l for l in vs_projects if l['name'] == name])
	return links

def outputPerProjectSolutions(make, ctx, vs_projects, output_path):
	for project in vs_projects:
		sub_vs_projects = collectVSProjectDependencies(project, vs_projects)
		sub_vs_projects.append(project)
		outputSolution(make, ctx, sub_vs_projects, output_path, per_project_solution_prefix + project['name'])

def outputPerGroupSolutions(make, ctx, vs_projects, groups, output_path):
	for group in groups:
		all_deps = []
		for project in vs_projects:
			if project['group'] == group:
				all_deps.append(project)
				all_deps.extend(collectVSProjectDependencies(project, vs_projects))

		# remove duplicates and output
		sub_vs_projects = [i for n, i in enumerate(all_deps) if i not in all_deps[n + 1:]]
		outputSolution(make, ctx, sub_vs_projects, output_path, per_group_solution_prefix + group)

def outputPerConditionSolutions(make, ctx, vs_projects, key, output_path):
	all_deps = []
	for project in vs_projects:
		expected = len(per_condition_solution_and_searchString)
		count = 0
		for searchString in per_condition_solution_and_searchString:
			if searchString in project[key]:
				count = count + 1

		if count == expected:
			count = 0
			for str in per_condition_solution_or_searchString:
				if str in project[key]:
					count = count + 1

			if count > 0:
				print(project[key])
				all_deps.append(project)
				all_deps.extend(collectVSProjectDependencies(project, vs_projects))

	# remove duplicates and output
	sub_vs_projects = [i for n, i in enumerate(all_deps) if i not in all_deps[n + 1:]]

	str = ''
	for searchString in per_condition_solution_and_searchString:
		if str != '':
			str = str + '_'
		str = str + searchString

	outputSolution(make, ctx, sub_vs_projects, output_path, per_condition_solution_prefix + str)
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def generateSolution(make, ctx, toolchains, output_path):
	api.log('VS2010 solution: ' + ctx['workspace'], 0)
	api.log('Target directory: ' + output_path, 1)

	if not os.path.exists(output_path):
	    os.makedirs(output_path)

	# convert projects
	groups = make.getConfigurationKeyValuesFilterByContext('group', ctx)

	vs_projects = []
	for group in groups:
		group_ctx = ctx.clone({'group': group})
		projects = make.getConfigurationKeyValuesFilterByContext('project', group_ctx)
		for project in projects:
			vs_projects.append(generateProject(make, group_ctx.clone({'project': project}), toolchains, output_path))

	# write projects
	for project in vs_projects:
		outputProject(make, project, vs_projects, output_path)

	# output solution filters (saved as one file per project)
	outputSolutionFilters(make, ctx, vs_projects, output_path)

	# output solutions
	if output_master_solution:
		api.log('Output Master Solution : Start...')
		outputSolution(make, ctx, vs_projects, output_path)
		api.log('Output Master Solution : Stop...')
	if output_per_project_solution:
		api.log('Output per project solution : Start...')
		outputPerProjectSolutions(make, ctx, vs_projects, output_path)
		api.log('Output per project solution : Stop...')
	if output_per_group_solution:
		api.log('Output per group solution : Start...')
		outputPerGroupSolutions(make, ctx, vs_projects, groups, output_path)
		api.log('Output per group solution : Stop...')
	if output_per_condition_solution and per_condition_solution_key:
		api.log('Output per name solution : Start...')
		outputPerConditionSolutions(make, ctx, vs_projects, per_condition_solution_key, output_path)
		api.log('Output per name solution : Stop...')

#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
def generate(make, toolchains, output_path):
	# retrieve all workspaces
	workspaces = make.getConfigurationKeyValues('workspace')

	# process all workspaces
	for workspace in workspaces:
		ctx = smack.context().clone({'workspace': workspace})
		generateSolution(make, ctx, toolchains, output_path)
#------------------------------------------------------------------------------
