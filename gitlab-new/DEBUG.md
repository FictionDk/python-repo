
ipython

import gitlab
base_url = 'https://gitlab.stpass.com'
token = 'glpat-H-iRjsgFoyIN3GqAztje1m86MQp1OjMH.01.0w16l5u9w'

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

gl = gitlab.Gitlab(base_url, private_token=token, ssl_verify=False)

project = gl.projects.get(4)
p1 = gl.projects.get(1)
p1.namespace.get('name')

i1 = project.issues.get(458)

i2 = project.issues.get(822)

c1 = project.commits.list(ref_name='dev')