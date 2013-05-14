# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

# Example of a build file (this is the actual build file for gamestart)

import api, smack

# -----------------------------------------------------------------------------
cpp_filter = ['*.c', '*.cpp', '*.cc', '*.h']

def rootPath(path = ''): return '../' + path
def corePath(path = ''): return rootPath('core/') + path
def modPath(path = ''): return rootPath('modules/') + path
def extPath(path = ''): return rootPath('extern/') + path
def sdkPath(path = ''): return rootPath('sdk/') + path
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
make = smack.make()
make.set('cflags', ['use-utf8', 'fp-fast'])	# global cflags

#------------------------------------------------------------------------------
# Workspace
#------------------------------------------------------------------------------
make.setWorkspace('gs')
make.set('type', 'staticlib')
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Projects
#------------------------------------------------------------------------------
make.push()

make.setGroup('os')

make.setProject('platform')
make.set('include_path', rootPath('platform'))
make.set('files', api.inputs().add(rootPath('platform'), cpp_filter))

make.setProject('framework')
make.set('depends', 'platform')
make.set('include_path', rootPath('framework'))
make.set('files', api.inputs().add(rootPath('framework'), cpp_filter))

make.setGroup('engine')

make.setProject('engine')
make.set('depends', 'framework')
make.set('include_path', rootPath('core'))
make.set('files', api.inputs().add(corePath('engine'), cpp_filter))
make.setModContext('link', 'd3d9', {'target': 'windows', 'build': 'Debug'})

make.setProject('script')
make.set('depends', 'framework')
make.set('include_path', rootPath('core'))
make.set('files', api.inputs().add(corePath('script'), cpp_filter))

#------------------------------------------------------------------------------
# Modules
#------------------------------------------------------------------------------
make.setGroup('modules')

make.setProject('http_curl')
make.set('depends', ['platform', 'curl'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('http_curl'), cpp_filter))
make.set('define', 'CURL_STATICLIB')

make.setProject('network_enet')
make.set('depends', ['enet', 'platform'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('network_enet'), cpp_filter))

make.setProject('io_net')
make.set('depends', ['framework', 'network_enet'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('io_net'), cpp_filter))

make.setProject('io_zip')
make.set('depends', ['platform', 'unzip'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('io_zip'), cpp_filter))

make.setProject('archive')
make.set('depends', ['framework', 'zlib'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('archive'), cpp_filter))

make.setProject('io_archive')
make.set('depends', ['framework', 'archive'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('io_archive'), cpp_filter))

make.setProject('audio_stream_ogg')
make.set('depends', 'framework')
make.set('include_path', [modPath(), extPath('stb_vorbis')])
make.set('files', api.inputs().add(modPath('audio_stream_ogg'), cpp_filter))

make.setProject('font_freetype')
make.set('depends', ['framework', 'freetype'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('font_freetype'), cpp_filter))

make.setProject('pict_io_jpeglib')
make.set('depends', ['framework', 'jpeglib'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('pict_io_jpeglib'), cpp_filter))

make.setProject('pict_io_stb')
make.set('depends', 'framework')
make.set('include_path', [modPath(), extPath('stb_image')])
make.set('files', api.inputs().add(modPath('pict_io_stb'), cpp_filter))

make.setProject('debug_enet')
make.set('depends', ['engine', 'network_enet'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('debug_enet'), cpp_filter))

make.setProject('import_fbx')
make.set('depends', 'engine')
make.set('include_path', [modPath(), sdkPath('FbxSdk/include')])
make.set('files', api.inputs().add(modPath('import_fbx'), cpp_filter))
make.setModContext('lib_path', sdkPath('FbxSdk/lib/vs2010/x86'), {'target': 'windows', 'arch': 'x86'})
make.setModContext('lib_path', sdkPath('FbxSdk/lib/vs2010/x64'), {'target': 'windows', 'arch': 'x64'})
make.setModContext('link', 'fbxsdk-2013.2-mdd', {'target': 'windows', 'build': 'Debug'})
make.setModContext('link', 'fbxsdk-2013.2-md', {'target': 'windows', 'build': 'Release'})
make.setModContext('link', 'fbxsdk-2013.2-md', {'target': 'windows', 'build': 'Master'})
make.setModContext('pflags', 'skip_build', {'target': '!windows'})

make.setProject('import_obj')
make.set('depends', 'engine')
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('import_obj'), cpp_filter))

make.setProject('nav_detour')
make.set('depends', ['engine'])
make.set('include_path', [modPath(), extPath('Detour/Include'), extPath('Recast/Include')])
make.set('files', api.inputs().add(modPath('nav_detour'), cpp_filter))

make.setProject('physic_bullet')
make.set('depends', ['engine', 'bullet'])
make.set('include_path', [modPath(), extPath('bullet/src')])
make.set('files', api.inputs().add(modPath('physic_bullet'), cpp_filter))

make.setProject('raytracer')
make.set('depends', 'engine')
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('raytracer'), cpp_filter))

make.setProject('script_squirrel')
make.set('depends', ['script', 'squirrel', 'enet'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('script_squirrel'), cpp_filter))

make.setProject('tools')
make.set('depends', 'engine')
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('tools'), cpp_filter))

make.setProject('viewer_base')
make.set('depends', ['physic_bullet', 'script_squirrel', 'debug_enet', 'font_freetype', 'raytracer'])
make.set('include_path', modPath())
make.set('files', api.inputs().add(modPath('viewer_base'), cpp_filter))

# extern
make.setGroup('extern')

make.setProject('unzip')
make.set('depends', 'zlib')
make.set('include_path', extPath('unzip'))
make.set('files', api.inputs().add(extPath('unzip'), cpp_filter))
make.setModContext('skip_files', extPath('unzip/iowin32.c'), {'target': '!windows'})

make.setProject('zlib')
make.set('include_path', extPath('zlib'))
make.set('files', api.inputs().add(extPath('zlib'), cpp_filter))

make.setProject('squirrel')
make.set('include_path', extPath('squirrel/include'))
make.set('files', api.inputs().add(extPath('squirrel'), cpp_filter))

make.setProject('freetype')
make.set('include_path', extPath('freetype/include'))
make.set('files', api.inputs().add(extPath('freetype/src'), cpp_filter))

make.setProject('enet')
make.set('include_path', extPath('enet/include'))
make.set('files', api.inputs().add(extPath('enet'), cpp_filter))
make.setModContext('link', 'winmm', {'target': 'windows'})
make.setModContext('skip_files', extPath('enet/win32.c'), {'target': '!windows'})

make.setProject('curl')
make.set('include_path', extPath('libcurl/include'))
make.set('files', api.inputs().add(extPath('libcurl/lib'), cpp_filter))
make.setModContext('link', ['Ws2_32', 'Wldap32'], {'target': 'windows'})
make.set('define', 'CURL_STATICLIB')

make.setProject('bullet')
make.set('include_path', extPath('bullet/src'))
make.set('files', api.inputs().add(extPath('bullet/src'), cpp_filter).exclude(extPath('bullet/src/BulletMultiThreaded'), cpp_filter))

make.setProject('jpeglib')
make.set('include_path', extPath('jpeglib'))
make.set('files', api.inputs().add(extPath('jpeglib'), cpp_filter))

make.setProject('gtest')
make.set('include_path', [extPath('gtest'), extPath('gtest/include')])
make.set('files', extPath('gtest/src/gtest-all.cc'))
#------------------------------------------------------------------------------

make.setGroup('renderer')

#------------------------------------------------------------------------------
# OpenGL
#------------------------------------------------------------------------------
make.setProject('egl')
make.set('depends', 'engine')
make.set('include_path', [rootPath('egl'), sdkPath('GL')])
make.set('files', api.inputs().add(rootPath('egl'), cpp_filter))
make.setModContext('link', 'OpenGL32', {'target': 'windows'})
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# DirectX 11
#------------------------------------------------------------------------------
make.setProject('dx11')
make.set('type', 'dynamiclib')
make.set('depends', ['engine', 'win_platform'])
make.set('include_path', [rootPath('dx11'), sdkPath('Microsoft DirectX SDK (June 2010)/Include')])
make.set('link', ['d3d11', 'DXGI', 'dxguid', 'Dbghelp', 'D3dcompiler'])
make.set('files', api.inputs().add(rootPath('dx11'), cpp_filter))

make.setModContext('pflags', 'skip_build', {'target': '!windows'})	# skip for all but windows
#------------------------------------------------------------------------------

make.setGroup('mixer')

#------------------------------------------------------------------------------
# OpenAL
#------------------------------------------------------------------------------
make.setProject('openal')
make.set('depends', 'engine')
make.set('include_path', rootPath('openal'))

make.push()

# windows
make.setTarget('windows')
make.set('include_path', sdkPath('OpenAL 1.1 SDK/include'))
make.set('lib_path', sdkPath('OpenAL 1.1 SDK/libs/Win32'))
make.set('link', 'OpenAL32')

make.setTarget('android')
make.set('include_path', [rootPath('android/openal_ndk/lowlatency/include'), rootPath('android/openal_ndk/lowlatency/OpenAL32/Include')])

make.pop()
make.set('files', api.inputs().add(rootPath('openal'), cpp_filter).getList())
#------------------------------------------------------------------------------

make.setGroup('windows')
make.setModContext('pflags', 'skip_build', {'target': '!windows'})

#------------------------------------------------------------------------------
# Windows platform
#------------------------------------------------------------------------------
make.push()

make.setProject('win_platform')
make.set('depends', 'platform')
make.set('include_path', rootPath('win/source'))
make.set('lib_path', sdkPath('Microsoft DirectX SDK (June 2010)/Lib/x86'))
make.set('files', api.inputs().add(rootPath('win/source'), cpp_filter))
make.set('link', ['xinput', 'dxguid', 'dinput8'])

# Stand-alone viewer
make.setProject('viewer')
make.set('type', 'executable')
make.set('depends', ['egl', 'openal', 'http_curl', 'io_archive', 'io_net', 'io_zip', 'audio_stream_ogg', 'pict_io_jpeglib', 'pict_io_stb', 'viewer_base', 'win_platform'])
make.set('subsystem', 'console')
make.set('include_path', rootPath('win/viewer'))
make.set('files', api.inputs().add(rootPath('win/viewer'), cpp_filter))

make.pop()
#------------------------------------------------------------------------------

make.setGroup('unix')

#------------------------------------------------------------------------------
# Unix platform
#------------------------------------------------------------------------------
make.setProject('unix_platform')
make.set('type', 'staticlib')
make.set('depends', 'platform')
make.set('include_path', rootPath('unix/source'))
make.set('files', api.inputs().add(rootPath('unix/source/platform'), cpp_filter))
make.setModContext('skip_files', api.inputs().add(rootPath('unix/source/x11'), cpp_filter), {'target': 'android'})
make.setModContext('pflags', 'skip_build', {'target': 'windows'})
#------------------------------------------------------------------------------

make.setGroup('android')

#------------------------------------------------------------------------------
# Android projects
#------------------------------------------------------------------------------

# Android platform
make.setProject('android_platform')
make.set('type', 'staticlib')
make.set('depends', 'unix_platform')
make.set('include_path', [rootPath('android/source'), rootPath('unix/source')])
make.set('files', api.inputs().add(rootPath('android/source/platform'), cpp_filter))
make.setModContext('pflags', 'skip_build', {'target': '!android'})	# skip on all but android target

# Android OpenAL implementation
make.setProject('android_openal')
make.set('type', 'dynamiclib')
make.set('include_path', [rootPath('android/openal_ndk/lowlatency/include'), rootPath('android/openal_ndk/lowlatency/OpenAL32/Include')])
make.set('define', ['AL_BUILD_LIBRARY', 'AL_ALEXT_PROTOTYPES'])
make.set('files', api.inputs().add(rootPath('android/openal_ndk/lowlatency'), cpp_filter))
make.set('link', 'log')
make.setModContext('pflags', 'skip_build', {'target': '!android'})	# skip on all but android target

# Android viewer base
make.setProject('android_viewer_base')
make.set('type', 'dynamiclib')
make.set('depends', ['egl', 'openal', 'http_curl', 'io_archive', 'io_net', 'io_zip', 'audio_stream_ogg', 'pict_io_jpeglib', 'pict_io_stb', 'android_platform', 'viewer_base'])
make.set('link', ['z', 'log', 'GLESv2'])
make.set('files', api.inputs().add(rootPath('android/source/viewer'), cpp_filter))
make.setModContext('pflags', 'skip_build', {'target': '!android'})	# skip on all but android target
#------------------------------------------------------------------------------

make.setGroup('editor')

#------------------------------------------------------------------------------
# Editor
#------------------------------------------------------------------------------
import vs2010_qt
vs2010_qt.install()

make.setProject('editor')
make.set('type', 'executable')
make.set('cflags', ['use-rtti', 'use-exceptions'])
make.set('depends', ['egl', 'import_fbx', 'import_obj', 'tools', 'openal', 'http_curl', 'io_archive', 'io_net', 'io_zip', 'audio_stream_ogg', 'pict_io_jpeglib', 'pict_io_stb', 'viewer_base', 'win_platform'])
make.set('include_path', rootPath('editor'))
make.set('use_pch', 'editor_pch.h')
make.set('create_pch', rootPath('editor/editor_pch.cpp'))
make.set('files', api.inputs().add(rootPath('editor'), cpp_filter + vs2010_qt.qt_filter))
make.set('qt', '4.8.4')
make.set('qt_res', api.inputs().add(rootPath('editor/resource/icons'), '*.*'))		# will rebuild qrc if any of these inputs has been modified
make.set('qt_modules', ['core', 'gui', 'opengl', 'script', 'webkit', 'network'])
#------------------------------------------------------------------------------

make.setGroup('unit_test')

#------------------------------------------------------------------------------
# Unit testing
#------------------------------------------------------------------------------
make.setProject('unit_test')
make.set('type', 'executable')
make.set('subsystem', 'console')
make.set('depends', ['gtest', 'network_enet', 'io_net', 'io_zip', 'http_curl'])
make.setModContext('depends', 'win_platform', {'target': 'windows'})
make.set('include_path', rootPath('unit-test'))
make.set('files', api.inputs().add(rootPath('unit-test'), cpp_filter))

#
make.pop()

#------------------------------------------------------------------------------
# Builds
#------------------------------------------------------------------------------
make.push()

make.setBuild('Debug')
make.set('cflags', ['debug', 'O0'])
make.set('define', '_DEBUG')

make.setBuild('Release')
make.set('cflags', ['O3', 'optimize', 'use-sse2'])
make.set('define', 'NDEBUG')

make.setBuild('Master')
make.set('cflags', ['O3', 'optimize'])
make.set('define', ['NDEBUG', '__ENGINE_RETAIL__=1'])

make.pop()
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Targets
#------------------------------------------------------------------------------
make.push()

make.setTarget('android')
make.set('define', ['__PLATFORM_ANDROID_NDK__=1', '__PLATFORM_UNIX__=1'])
make.set('cflags', ['use-stlport', 'W2'])
#make.set('android_toolset', '4.6')
make.set('bin_path', '../bin/android')

make.setTarget('windows')
make.set('define', '__PLATFORM_WINDOWS__=1')
make.set('cflags', 'W3')
make.set('bin_path', '../bin/win')

make.pop()
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# Architectures
#------------------------------------------------------------------------------
make.setModContext('define', 'WIN32', {'target': 'windows', 'arch': 'x86'})

# Set suffix for all supported build and architectures
for arch in ['x86', 'x64', 'ARMv7', 'ARMv5', 'Mips']:
	for build in ['Debug', 'Release', 'Master']:
		make.setModContext('bin_suffix', '-' + build.lower() + '-' + arch.lower(), {'build': build, 'arch': arch})
# -----------------------------------------------------------------------------

# toolchains to support
toolchains = [
	{
		'target': 'android',
		'arch': ['ARMv7', 'ARMv5', 'Mips', 'x86', 'All'],
	},
	{
		'target': 'windows',
		'arch': ['x86', 'x64'],
	},
]

# -----------------------------------------------------------------------------
import vs2010, vs2010_android
vs2010_android.install()
vs2010.generate(make, toolchains, 'vs')
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
import android_mk
android_mk.generate(make, toolchains, '../android/eclipse/viewer/jni')
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
import dot_map
dot_map.generate(make, 'graph')
# -----------------------------------------------------------------------------
