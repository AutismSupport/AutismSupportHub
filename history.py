from nicegui import app,ui

async def export(history_list):
    #ui.notify('Under Construction')
    exported_history=''
    for h in history_list:
        if h['role']=='user':
            for l in h['content'].split('\n'):
                exported_history+='> '+h['content']+'\n> \n'
            exported_history+='\n'
        if h['role']=='assistant':
            exported_history+=h['content']+'\n\n'
            exported_history+='---\n\n'
    ui.download(exported_history.encode('utf-8'),'history.md')

def clear():
    app.storage.user['history']=[]
    ui.notify('已清除历史记录，请刷新页面！')