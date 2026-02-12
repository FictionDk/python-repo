
ipython

import gitlab
base_url = 'https://gitlab.stpass.com'
token = 'glpat-H-iRjsgFoyIN3GqAztje1m86MQp1OjMH.01.0w16l5u9w'

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

gl = gitlab.Gitlab(base_url, private_token=token, ssl_verify=False)

project = gl.projects.get(4)

i1 = project.issues.get(458)


