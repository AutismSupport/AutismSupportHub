# Autism Helper (Related to AutismChina)
# NiceGUI Ver
# 2023 By rgzz666 & fakeai
# Requires Python version 3.10+

from nicegui import ui,app,run
#from niceguiToolkit.layout import inject_layout_tool

import effects

#import openai
import chatgpt
import OpenAIConfig
import history

import time
import os
import sys
import json
#import threading
import requests


#inject_layout_tool()

# Change this line to restart the server

global_gpt=True #Run with '--nogpt' to disable everything related to ChatGPT
global_addr='fr_config' #Set it to 'fr_config' to read from ./config.json
global_ssl='fr_config' #Set it to 'fr_config' to read from ./config.json or use '--ssl' param to override everything
global_port=10008 #Run with '--port <PORT>' to override this with the given port in params
global_apikey='fr_secrets' #Set it to 'fr_secrets' to read from ./secrets.json or 'fr_list' to choose one automatically from ./api_keys.list
global_maxcontext=3
global_rule='fr_file' #Set it to 'fr_file' to read from ./gpt_rule.txt
global_adminpwd='fr_secrets' #Set it to 'fr_secrets' to read from ./secrets.json


##### CODE BELOW #####
visits=0
promps=0


def split_string_by_length(string, length):
    return [string[i:i+length] for i in range(0, len(string), length)]

def get_key_usage(key):
    queryUrl = 'https://api.openai.com/dashboard/billing/subscription'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Authorization': f'Bearer {key}',
        'Accept': '*/*',
        'Host': 'api.openai.com',
        'Connection': 'keep-alive'
    }
    
    r = requests.get(queryUrl, headers=headers)
    return r.json()

def choose_key(keys:list):
    # choose_key() can automatically choose an api key from the given key list by removing all
    # the expired ones and comparing the expire time of the rest of them. choose_key() requires
    # a list of OpenAI API keys which looks like this: ['<KEY 1>','<KEY 2>','<KEY 3>'].
    ###
    # In the Autism Support project which this function originally used in, the keys are read
    # from a config file which contains several keys if you set the internal API key config to
    # 'fr_list'.
    global global_gpt
    ok_list={}
    for k in keys:
        exp_time=get_key_usage(k)['access_until']
        if int(exp_time)>int(time.time()):
            ok_list[k]=exp_time
    if len(ok_list.keys())==0:
        print('ALL KEYS HAS EXPIRED! Please add some new keys to ./api_keys.list')
        global_apt=False
        return ''
    else:
        return [k for k,v in ok_list.items() if v==min(ok_list.values())][0]

f=open("./secrets.json",'r',encoding='utf-8')
fcontent=f.read()
f.close()
secrets=json.loads(fcontent)

f=open("./config.json",'r',encoding='utf-8')
fcontent=f.read()
f.close()
config=json.loads(fcontent)

if global_addr=='fr_config':
    global_addr=config['addr']

if '--ssl' in sys.argv:
    global_ssl=True
else:
    if global_ssl=='fr_config':
        global_ssl=config['ssl']

if global_rule=='fr_file':
    f=open("./gpt_rule.txt",'r',encoding='utf-8')
    fcontent=f.read()
    f.close()
    global_rule=fcontent

if global_apikey=='fr_secrets':
    global_apikey=secrets['apikey']
if global_apikey=='fr_list':
    f=open("./api_keys.list",'r',encoding='utf-8')
    apikeys=f.read().split('\n')
    for k in apikeys:
        if k[0]=='#': #remove comments
            apikeys.remove(k)
    global_apikey=choose_key(apikeys)

if global_adminpwd=='fr_secrets':
    global_adminpwd=secrets['admin_pwd']

if '--port' in sys.argv:
    global_port=int(sys.argv[sys.argv.index('--port')+1])

global_gpt=not '--nogpt' in sys.argv

if '--autoclear' in sys.argv:
    if os.name=='nt':
        os.system("cls")
    else:
        os.system("clear")


### Classes & Functions ###
# Code comments below might be written in Chinese #
def call_func_list(func_list):
    for func in func_list:
        func()

async def confirm(action=None,description='继续',detail=None):
    # 用法1：不传入actions参数或传入None，在函数外部用if语句判断confirm()结果，为True则执行后续代码
    # 用法2：向actions中传入lambda语句或函数，用户点击确认即执行参数内的代码
    def confirm_no(action=None,dlg=None):
        result=False
        if dlg!=None:
            dlg.submit(result)
            #dlg.close()
        return result
    def confirm_yes(action,dlg=None):
        if action==None:
            result=True
        else:
            result=action()
        if dlg!=None:
            dlg.submit(result)
            #dlg.close()
        return result
    with ui.dialog() as confirm_dlg,ui.card():
        ui.label("您确定要 "+str(description)+" 吗？").style("font-weight:bolder;font-size:18px")
        if detail!=None or detail!='':
            ui.label(str(detail))
        with ui.row().style("width:95%;align-self:center"):
            ui.button('取消',on_click=lambda:confirm_dlg.submit(confirm_no(action,confirm_dlg))).style("width:45%")
            ui.button('继续',on_click=lambda:confirm_dlg.submit(confirm_yes(action,confirm_dlg)),color='red').style("width:45%")
    #confirm_dlg.open()
    return await confirm_dlg

def admin_post_notice(title,text,notice_pt,bgcolor='#eeeeff'):
    with notice_pt:
        with ui.card().style("background-color:"+bgcolor+";width:100%"):
            ui.label(str(title)).style("font-weight:bolder;width:100%").classes("py-0")
            ui.markdown(text).style("width:100%").classes("py-0")
            ui.label(time.strftime("%Y/%m/%d %H:%M:%S")).style("font-size:12px").classes("py-0")

def load_history(historypt):
    hlist=app.storage.user['history']
    #hlist=app.storage.user.get('history',0)
    for h in hlist:
        match h['role']:
            case "user":
                with historypt:
                    ui.chat_message(h["content"],name='You',sent=True,stamp=time.strftime("%Y/%m/%d %H:%M:%S",
                                    time.localtime(time.time()))).style("align-self:end")
            case "assistant":
                with historypt:
                    with ui.chat_message(name='ChatGPT',sent=False,avatar="http://116.198.35.73:10007/chatgpt.png",
                                         stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))):
                        ui.markdown(h["content"])
            case _:
                pass
    historypt.scroll_to(percent=1)

async def askgpt(historylist,msg_placeholder,history_pt):
    global global_maxcontext,global_rule
    #if len(historylist)>global_maxcontext:
    #    listorylist=[{"role":"system","content":str(global_rule)},historylist[len(historylist)-2],historylist[len(historylist)-1]]
    try:
        context_list=historylist[len(historylist)-(global_maxcontext-1):]
        context_list.insert(0,{"role":"system","content":str(global_rule)})
        if context_list[len(context_list)-1]['content'].lower().startswith("/test"): #处理测试命令
            cmdpt=context_list[len(context_list)-1]['content'].lower().split('|')[0]
            if context_list[len(context_list)-1]['content'].split('|')[1]==global_adminpwd:
                match cmdpt.split(" ")[0].split(".")[1]:
                    case 'rule_unlock':
                        context_list.pop(0)
                    case _:
                        ui.notify("Ignoring invalid test command.")
            else:
                ui.notify("Admin password incorrect! Ignoring test command.")
            context_list[len(context_list)-1]['content']=context_list[len(context_list)-1]['content'].\
                replace(context_list[len(context_list)-1]['content'].split('|')[1]+'|','').\
                replace(context_list[len(context_list)-1]['content'].split('|')[0]+'|','')
        api=chatgpt.ChatCompletionsApi(global_apikey)
        config = OpenAIConfig.OpenAIConfig(
            model="gpt-3.5-turbo",
            messages=context_list)
        #print(historylist[len(historylist)-(global_maxcontext-1):])
        response = await run.io_bound(lambda:api.create_chat_completions(config,msg_placeholder,msglist=history_pt))
        return response
    except Exception as e:
        #a=abc #取消注释此行，产生错误，使异常处理失效，在控制台查看完整报错
        return 'Error: \n\n```'+str(e)+'```'

async def send_msg(prompt,history_pt,msg_input=None):
    global promps
    promps+=1
    #historylist=[] #暂时充当聊天记录列表
    #global history_pt
    history_pt.scroll_to(percent=1)
    with history_pt:
        ui.chat_message(str(prompt),name='您',sent=True,stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))).style("align-self:end")
        #historylist.append({"role":"user","content":prompt})
        #存储用户问题
        app.storage.user['history'].append({"role":"user","content":prompt})
    if msg_input!=None:
        msg_input.value=''
    with history_pt:
        with ui.chat_message(name='ChatGPT',sent=False,avatar="http://116.198.35.73:10007/chatgpt.png",stamp=time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))):
            reply_text=ui.markdown()
            #reply_text.on('change',history_pt.scroll_to(percent=1))
    history_pt.scroll_to(percent=1)
    #text = ""
    #turns = []
    #last_result = ""
    #问的问题
    #question = prompt
    #回复的东西
    response=await askgpt(app.storage.user['history'],reply_text,history_pt)
    #result = response
    #last_result = result
    #turns += [question] + [result]
    #if len(turns) <= 10:
    #    text = "".join(turns)
    #else:
    #    text = "".join(turns[-10:])
    with history_pt:
        #historylist.append({"role":"assistant","content":response})
        app.storage.user['history'].append({"role":"assistant","content":response})
    reply_text.set_content(str(response))
    history_pt.scroll_to(percent=1)

async def copy_text(text,notify='已复制文本'):
    global global_ssl
    if global_ssl:
        ui.run_javascript(f"navigator.clipboard.writeText('"+str(text)+"')")
        ui.notify(str(notify))
    else:
        ui.notify('站点未使用HTTPS，无法复制，请手动选中复制')


### COMPONENTS ###
def home_douknow(left_txt:str,right_txt:str,height:int=124):
    with ui.row().classes("justify-center").style("width:80%;align-self:center;height:"+str(height)+"px").props("justify-center"):
        with ui.card().style("width:45%;align-self:center;height:100%"):
            ui.markdown(left_txt)
        with ui.card().style("width:45%;align-self:center;height:100%"):
            placeholder=ui.markdown('')
            showans_btn=''
            showans_btn=ui.button("点我！",on_click=lambda:run.io_bound(lambda:call_func_list([showans_btn.delete,lambda:effects.typewriter(
                [right_txt],text_placeholder=placeholder,repeat=False,placeholder_type='markdown')]))).style("width:70%;align-self:center").props('flat')


### PAGES ###
@ui.page("/chat")
def chat_page():
    global visits
    visits+=1
    f=open("./help/chat_help.md",'r',encoding='utf-8')
    help_content=f.read()
    help_titles=[]
    for l in help_content.split("\n"):
        if l.startswith("### "):
            help_titles.append(l[4:])
    with ui.dialog() as help_dlg,ui.card():
        with ui.scroll_area().style("width:480px;max-width:100%;height:640px;max-width:100vh"):
            ui.markdown(help_content).style("width:100%;height:100%")
    with ui.left_drawer(bottom_corner=True).style('background-color: #f0f0f0') as left_drawer:
        with ui.card().style("width:100%"):
            ui.label('免责声明').style("font-weight:bolder")
            ui.label("此处替换为新免责声明").style("width:100%")
        ui.label('操作')
        with ui.card().style("width:100%").classes("space-y-0 gap-y-0"):
            ui.button('回到主页',on_click=lambda:ui.open("/")).props("flat color=black").style("width:100%")
            ui.button('导出记录',on_click=lambda:history.export(app.storage.user.get('history',0))).props("flat color=black").style("width:100%")
            ui.button('清除记录',on_click=lambda:confirm(history.clear,'清除历史记录','清除后记录将永久丢失，建议您先导出记录再清除')).\
                props("flat color=black").style("width:100%")
        with ui.card().style("width:100%").classes("space-y-0 gap-y-0"):
            title_txt=ui.label("需要帮助吗？")
            ui.button("查看帮助",on_click=help_dlg.open).props("flat color=black")
            run.io_bound(lambda:effects.typewriter(help_titles,title_txt))
    with ui.header(elevated=True).style('background-color: #303030').classes('items-center justify-between'):
        with ui.row():
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').style("align-self:center").props('flat color=white')
            ui.label('AUTISM SUPPORT').style("align-self:center")
        #ui.label('所有答复仅供参考，切勿直接按其行事，出现任何问题本项目概不负责')
    with ui.column().style("width:100%;height:85vh"):
        with ui.card().style("width:100%;max-width:720px;height:75%;background:#f0f0f0;align-self:center"):
            with ui.scroll_area().style("height:100%;width:100%") as history_pt:
                ui.label('消息历史')
        with ui.row().style("width:100%;max-width:720px;height:20%;align-self:center").classes("justify-center") as msginput_pt:
            msg_input=ui.textarea(placeholder='输入问题…').style("width:85%;height:100%").props('filled').classes("resize-none")
            ui.button(icon='send',on_click=lambda:send_msg(msg_input.value,history_pt,msg_input)).style("width:10%;height:100%")
    #print(app.storage.user.get('history',0),'  |  ',app.storage.user['history'])
    if app.storage.user.get('history',0)==0:
        app.storage.user['history']=[]
        ui.notify('已初始化用户数据')
    load_history(history_pt)
    ui.notify("已加载记录")
    #app.on_connect(lambda:init_page(history_pt))
    history_pt.scroll_to(percent=1)
    #print("hi?")

@ui.page("/admin",title='后台 | Autism Support')
def admin():
    global visits,promps
    with ui.right_drawer(bottom_corner=True).style("background-color:#cccccc").classes("px-0 py-0") as right_pt:
        with ui.scroll_area().style("width:100%;height:75%").classes("px-0,py-0") as notice_pt:
            if not global_gpt:
                #with ui.card().style("background-color:#ffeecc;width:100%"):
                admin_post_notice('ChatGPT已停用','ChatGPT已停用！请仅在服务器无法访问OpenAI API时采取该措施，若要启用，请去除`--nogpt`参数重启服务端。',notice_pt,'#ffeecc')
                    #ui.label('ChatGPT已停用').style("font-weight:bolder").classes("py-0")
                    #ui.markdown('ChatGPT已停用！请仅在服务器无法访问OpenAI API时采取该措施。若要启用ChatGPT，请去除`--nogpt`参数重新启动服务端。')
            if not global_ssl:
                #with ui.card().style("background-color:#ffeecc;width:100%"):
                admin_post_notice('未使用HTTPS（SSL）','未使用HTTPS，将导致所有文本复制不可用。请为域名配置SSL证书，然后在`./config.json`中启用SSL，或使用`--ssl`参数重启服务端。',notice_pt,'#ffeecc')
                    #ui.label('未使用HTTPS（SSL）').style("font-weight:bolder").classes("py-0")
                    #ui.markdown('未使用HTTPS，将导致所有文本复制不可用。请为域名配置SSL证书后，在`./config.json`内启用SSL，或使用`--ssl`参数重启服务端。')
        with ui.card().style("width:100%;height:25%;background-color:#eeeeff"):
            notice_input=ui.textarea(placeholder='后台留言').style("width:100%;height:70%").classes("py-0")
            ui.button("留言",on_click=lambda:admin_post_notice("后台留言",str(notice_input.value),notice_pt)).style("width:100%;height:25%").classes("py-0")
    with ui.header(elevated=True).style('background-color: #303030').classes('items-center justify-between'):
        with ui.row():
            ui.label('AUTISM SUPPORT | Admin').style("align-self:center")
    with ui.row().style("width:95%"):
        ui.label('操作').style("font-weight:bolder;font-size:24px")
        with ui.card().style("width:35%"):
            ui.label('快速操作')
            ui.button('关闭网页',on_click=lambda:confirm(app.shutdown,'关闭网页',detail='若未启用自动重载，继续会导致网页服务停止，仅可在服务器再次启动。'))
            ui.button('退出服务端',on_click=lambda:confirm(lambda:os._exit(1),'退出服务端',detail='若未启用自动重载则会推出服务端。退出后网页服务将停止，仅可在服务器再次启动。'))
        with ui.card().style("width:55%"):
            ui.label('发送系统命令')
            with ui.row().style("width:95%"):
                cmd_input=ui.input(placeholder='输入命令').style("width:65%")
                apply_btn=ui.button('执行',on_click=lambda:call_func_list([lambda:os.system(cmd_input.value),lambda:ui.notify("已执行")])).style("width:30%")
                apply_btn.disable()
            ui.label('点击启用该功能').style("color:#0078dc").on('click',lambda:confirm(lambda:call_func_list([apply_btn.enable,lambda:ui.notify('已启用远程命令执行功能')]),
                                                                                 '启用远程命令执行','直接执行命令可能会导致未知问题'))
    with ui.row().style("width:95%"):
        ui.label('统计').style("font-weight:bolder;font-size:24px")
        with ui.card().style("width:90%"):
            with ui.row().style("width:100%"):
                ui.label("注：访问统计数据从服务端启动/重启截至本次进入后台时").style("font-weight:bolder;color:#007000")
                ui.label("访问次数："+str(visits))
                ui.label("询问次数："+str(promps))
    # 管理密码输入框
    with ui.dialog().props('persistent') as pwd_dlg,ui.card():
        pwd_input=ui.input(placeholder='输入管理密码',password=True,password_toggle_button=True).style("width:100%")
        ui.button('进入后台',on_click=lambda:pwd_dlg.close() if pwd_input.value==global_adminpwd else ui.notify('密码错误')).style("width:100%")
        ui.label("管理密码明文存储于服务端目录下的secrets.json")
        pwd_dlg.open()

@ui.page("/")#.classes("px-0 py-0")
async def home():
    #ui.label('test')
    with ui.column().style("width:100%").classes("px-0 py-0"):
        with ui.column().style("align-self:center;width:100%;background:#303030").props('flat'):
            with ui.column().style("align-self:center;background:#303030"):
                ui.label("&nbsp;").style("font-size:48px;font-weight:bolder;color:#303030")
                ui.label("The").style("font-size:72px;font-weight:bolder;color:#ffffff")
                projname_txt=ui.label("Autism Support").\
                              style("font-size:120px;font-weight:bolder;background-image:linear-gradient(135deg, #DA5050 25%,#FFCE73 75%);background-clip:text;color: transparent")
                ui.label("Project").style("font-size:72px;font-weight:bolder;color:#ffffff")
                ui.label("WE NEED PEOPLE !").style("font-size:48px;font-weight:bolder;color:#303030")
        with ui.card().style("width:100%").props("flat"):
            with ui.row().style("align-self:center"):
                with ui.dialog() as copyurl_dlg,ui.card():
                    ui.label('复制本站链接，并发给身边有需要的人').style("align-self:center")
                    url_txt=ui.label('http://'+str(global_addr)+':'+str(global_port)+'/').style("width:100%;max-width:480px;background:#eeeeff;font-size:18px;align-self:center")
                    #copy_cmd='navigator.clipboard.writeText("'+'http://'+str(global_addr)+':'+str(global_port)+'/'+'")'
                    ui.button("复制到剪贴板",on_click=lambda:copy_text('http://'+str(global_addr)+':'+str(global_port)+'/')).style("width:100%")
                    #url_txt.value='http://'+str(global_addr)+':'+str(global_port)+'/'
                ui.button("开始提问",on_click=lambda:ui.open("/chat")).props("flat color=black")
                with ui.button("帮助我们").props("flat color=black"):
                    with ui.menu() as helpus_options:
                        ui.menu_item('传播本站',copyurl_dlg.open)
                        ui.menu_item('加入我们',lambda:ui.notify('感谢，但是我们目前不需要过多的人哦！'))
                ui.button("后台",on_click=lambda:ui.open("/admin")).props("flat color=light-gray")
                #ui.button("关于自闭症").props("flat color=black")
        #with ui.row().style("width:80%;align-self:center"):
        #    autism_count=500000000 #数据蒙眼乱编，仅供效果参考
        #    people_count=1400000000
        #    ui.echart({"type":"pie","data":[{"name":"Autism","value":autism_count},{"name":"Normal","value":people_count-autism_count}]})
        with ui.column().style("width:100%;max-width:720px;align-self:center;background:#f0f0f0"):
            ui.label('&nbsp;').style("font-size:28px;font-weight:bolder;align-self:center;color:#f0f0f0")
            with ui.card().style("width:85%;align-self:center"):
                ui.label('孤独症，也称为自闭症（英语：autism），是一种由脑部发育障碍所导致的疾病，其特征是情绪，言语和非言语的表达困难及社交互动障碍，\
会对限制性行为与重复性动作有明显的兴趣。家长一般会在孤独症孩童两到三岁时注意到其状况。其症状会渐渐加重，不过有些有孤独症的孩童在孤独症恶化之前，\
在一段时间内有着正常或接近正常的早期发展阶段（见儿童发展阶段），之后会出现一个或多个自闭症的特发特征，比如语言倒退等。').style("width:95%;align-self:center")
                ui.label('症状').style("align-self:center;font-weight:bolder")
                with ui.row().classes("justify-center").style(add="width:95%;align-self:center"):
                    with ui.card().style("background-color:#eeeeff;width:30%"):
                        ui.label("受损的人际关系").style("font-weight:bolder;align-self:center")
                    with ui.card().style("background-color:#eeeeff;width:30%"):
                        ui.label("言语和非言语交际").style("font-weight:bolder;align-self:center")
                    with ui.card().style("background-color:#eeeeff;width:30%"):
                        ui.label("局限和强迫的行为").style("font-weight:bolder;align-self:center")
                #ui.label('TITLE').style("align-self:center;font-weight:bolder")
                #with ui.row().props("justify-center").style(add="width:95%;align-self:center"):
                #    with ui.card().props("px-0 pe-0").style("background-color:#eeeeff;width:30%"):
                #        ui.label("Text 1").style("font-weight:bolder;align-self:center")
                #    with ui.card().props("px-0 pe-0").style("background-color:#eeeeff;width:30%"):
                #        ui.label("Text 2").style("font-weight:bolder;align-self:center")
                #    with ui.card().props("px-0 pe-0").style("background-color:#eeeeff;width:30%"):
                #        ui.label("Text 3").style("font-weight:bolder;align-self:center")
            ui.label('您知道吗？').style("font-size:28px;font-weight:bolder;align-self:center")
            home_douknow("患自闭症的概率为0.07%，","但是如果我们告诉您，**每100个儿童中就有一个患自闭症**呢？")
            home_douknow("目前没有可以治愈孤独症的方式，",
                         "但是早期的言语治疗或应用行为分析可以帮助有孤独症的儿童学习自我照顾、社交及沟通技能。**目前已有孩童撤销的案例。**")
            with ui.card().style("width:"+str(int(0.95*0.80*100))+"%;align-self:center"):
                ui.label("目前已有发展一种孤独症文化，有些孤独症者是希望康复，而有些认为孤独症只需视为个体差异，不应该当成是疾病。").\
                                                                                   style("width:95%;max-width:400px;align-self:center;text-align:center")
            ui.label('你居然看到底了欸！但是……【很闲吗？】').style("font-size:28px;font-weight:bolder;align-self:center;color:#f0f0f0")


### Print Config ###
if not '--noclear' in sys.argv:
    if os.name=='nt':
        os.system("cls")
    else:
        os.system("clear")
    print("["+time.strftime("%Y/%m/%d %H:%M:%S",time.localtime(time.time()))+"] 程序启动，已清屏\n（若要禁用启动时清屏，请在启动时传入“--noclear”参数）\n\n")

console_w=os.get_terminal_size().columns

print("=====本次启动/重启的配置内容=====")
print("--是否启用ChatGPT："+str(global_gpt))
print("--API Key："+global_apikey[0:len(global_apikey)-20-1]+"********************")
print("--端口："+str(global_port))
print("--上下文限制："+str(global_maxcontext)+"(-1)")
print("--问答规则：")
for l in global_rule.split('\n'):
    for t in split_string_by_length(l,console_w):
        print("| "+t)
#print(global_rule)
print("")


### Run UI ###
ui.run(title='Autism Support',port=global_port,storage_secret='autism_storage')
