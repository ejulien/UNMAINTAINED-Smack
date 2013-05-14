# smack - Emmanuel Julien 2013 (ejulien@owloh.com)
# MIT Licensed

import pydot, smack

def generate(make, output_path):

	def getExe(name):
		return 'C:/Program Files (x86)/Graphviz2.30/bin/' + name + '.exe'

	graph = pydot.Dot(graph_type='digraph', ranksep='1.0', nodesep='0.3')
	graph.set_graphviz_executables({'dot': getExe('dot'), 'twopi': getExe('twopi'), 'neato': getExe('neato'), 'circo': getExe('circo'), 'fdp': getExe('fdp')})

	#
	ctx = smack.context({'workspace': 'gs', 'group': '*'})
	projects = make.getConfigurationKeyValuesFilterByContext('project', ctx)

	#
	nodes = []
	for project in projects:
		node = pydot.Node(project, shape='record', style='rounded', fillcolor='#777799', fontname='Arial')
		graph.add_node(node)
		nodes.append({'project': project, 'node': node})

	def findProjectNode(project):
		for node in nodes:
			if node['project'] == project:
				return node
		return None

	# insert dependencies
	for project in projects:
		node = findProjectNode(project)
		if node == None:
			continue

		deps = make.get('depends', ctx.clone({'project': project}))
		if deps != None:
			for dep in deps:
				dep_node = findProjectNode(dep)
				if dep_node != None:
					graph.add_edge(pydot.Edge(node['node'], dep_node['node']))

	# setup groups

	graph.write_png('deps.png')
