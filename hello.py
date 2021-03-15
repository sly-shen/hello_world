import requests
from plotly.graph_objs import Bar
from plotly import offline
import plotly.graph_objs as go

#执行API调用并存储响应
url='https://api.github.com/search/repositories?q=language:python&sort=stars'
headers={'accept':'application/vnd.github.v3+json'}
r=requests.get(url)
print(f'status code:{r.status_code}')

#处理结果
response_dict=r.json()
repo_dicts=response_dict['items']
repo_links,stars,labels=[],[],[]
for repo_dict in repo_dicts:
    repo_name=repo_dict['name']
    repo_url=repo_dict['html_url']
    repo_link=f"<a href='{repo_url}'>{repo_name}</a>"
    repo_links.append(repo_link)
    
    stars.append(repo_dict['stargazers_count'])

#可视化
date=[{
'type':'bar',
'x':repo_links,
'y':stars,
'marker':{
    'color':'rgb(60,100,150)',
    'line':{'width':1.5,'color':'rgb(25,25,25)'}
    },
'opacity':0.6,
}]
'''marker:条形设计;opacity:不透明度'''
my_layout={
'title':'Github上最受欢迎的Python项目',
'xaxis':{
    'title':'Repository',
    'titlefont':{'size':24},
    'tickfont':{'size':14},
    },
'yaxis':{
    'title':'Stars',
    'titlefont':{'size':24},
    'tickfont':{'size':14},
    },
}
'''titlefont:指定图标名称的字号;tickfont:刻度标签字号的设置'''
fig=go.Figure(date,layout=my_layout)
offline.plot(fig,filename='python_repos.html')
