import time
import warnings

# Animation effects must be run with await to keep nicegui connections alive

# Text animation - Typewriter
def typewriter(textlist:list,text_placeholder,typespeed:float=0.05,stoptime:int=2,delspeed:float=0.02,repeat:bool=False,placeholder_type='label',curchar:str='|'):
    while True:
        index=0
        for text in textlist:
            nowtext=''
            for char in str(text):
                nowtext+=char
                match placeholder_type.lower():
                    case 'label':
                        text_placeholder.set_text(nowtext+curchar)
                    case 'markdown':
                        text_placeholder.set_content(nowtext+curchar)
                    case 'variable':
                        text_placeholder=str(nowtext+curchar)
                    case _:
                        warnings.warn("Unsupported placeholder type")
                time.sleep(typespeed)
            match placeholder_type.lower():
                case 'label':
                    text_placeholder.set_text(nowtext)
                case 'markdown':
                    text_placeholder.set_content(nowtext)
                case 'variable':
                    text_placeholder=str(nowtext)
                case _:
                    warnings.warn("Unsupported placeholder type")
            with_curchar=False
            for i in range(stoptime*2):
                time.sleep(0.5)
                if with_curchar:
                    match placeholder_type.lower():
                        case 'label':
                            text_placeholder.set_text(nowtext)
                        case 'markdown':
                            text_placeholder.set_content(nowtext)
                        case 'variable':
                            text_placeholder=str(nowtext)
                        case _:
                            warnings.warn("Unsupported placeholder type")
                    with_curchar=False
                else:
                    match placeholder_type.lower():
                        case 'label':
                            text_placeholder.set_text(nowtext+curchar)
                        case 'markdown':
                            text_placeholder.set_content(nowtext+curchar)
                        case 'variable':
                            text_placeholder=str(nowtext+curchar)
                        case _:
                            warnings.warn("Unsupported placeholder type")
                    with_curchar=True
            if not ((not repeat) and index==len(textlist)-1):
                for i in range(len(str(text))):
                    match placeholder_type.lower():
                        case 'label':
                            text_placeholder.set_text(nowtext[0:len(str(text))-i-1]+curchar)
                        case 'markdown':
                            text_placeholder.set_content(nowtext[0:len(str(text))-i-1]+curchar)
                        case 'variable':
                            text_placeholder=str(nowtext[0:len(str(text))-i-1]+curchar)
                        case _:
                            warnings.warn("Unsupported placeholder type")
                    time.sleep(delspeed)
            time.sleep(0.1)
            #print('Typewriter looped')
        if not repeat:
            break
