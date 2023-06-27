from code_analyzer import CodeAnalyzer
from bot_message import *


class Scene:
    """Класс блока сценария Telegram-бота"""

    def __init__(self, name, messages, waitingElements):
        self.sceneMessages = messages
        self.name = name
        self.trash = waitingElements

    def getName(self):
        return self.name

    def getSceneMessages(self):
        return self.sceneMessages


def getScenery(words, resPath):
    elements = []
    token = ""
    text = ""

    # для сцен
    currentSceneName = ""
    scenes = []
    currentScene = None
    
    waitSomething = []

    def getSceneByName(sceneName):
        for sc in scenes:
            if sc.getName()==sceneName:
                return sc

    # для группы
    groupMessageFlag = False
    textFound = False
    groupMessage = []
    
    print('=== НАЧИНАЕМ СБОРКУ ПРОЕКТА. СОБИРАЕМ БЛОКИ... ===')
    ind = 0 # индекс текущего кортежа
    while True:
        print(words)
        if words[ind][0]==CodeAnalyzer.BOT and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1
            if words[ind][2]==CodeAnalyzer.STRING:
                token = words[ind][0][1:len(words[ind][0])-1]
                # print(token) 
                ind += 1
                if not words[ind][0]==CodeAnalyzer.COLON:
                    raise Exception(f'Ожидилось ключевое слово {CodeAnalyzer.COLON} . Строка {words[ind-1][1]}')
                else:
                    ind +=1
            else:
                raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.BOT}. Строка {words[ind-1][1]}')
        elif words[ind][0]==CodeAnalyzer.BOT_END and words[ind][2]==CodeAnalyzer.KEYWORD:
            break
        elif words[ind][0]==CodeAnalyzer.BLOCK and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1
            if words[ind][2]==CodeAnalyzer.STRING:
               currentSceneName =  words[ind][0][1:len(words[ind][0])-1]
               # print(currentSceneName)
               ind += 1
               if not words[ind][0]==CodeAnalyzer.COLON:
                   raise Exception(f'Ожидилось ключевое слово {CodeAnalyzer.COLON} . Строка {words[ind-1][1]}')
               else:
                   ind +=1
            else:
                 raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.BLOCK}. Строка {words[ind-1][1]}')
        elif words[ind][0]==CodeAnalyzer.BLOCK_END and words[ind][2]==CodeAnalyzer.KEYWORD:
            scenes.append(Scene(currentSceneName, elements, waitSomething))
            elements = []
            # print(waitSomething)
            waitSomething = []
            currentName = ""
            ind += 1
        elif words[ind][0]==CodeAnalyzer.TEXT and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1
            if words[ind][2]==CodeAnalyzer.STRING:
                el = TextPost(words[ind][0][1:len(words[ind][0])-1])               
                if groupMessageFlag:
                   if not textFound:
                       groupMessage.append(el)
                       textFound = True
                   else:
                       raise Exception(f'В текущей группе уже есть текст! Строка {words[ind-1][1]}')
                else:
                   elements.append(el)
                # print("текст "+words[ind][0][1:len(words[ind][0])-1])
                ind += 1
            else:
                 raise Exception(f'Ожидилась строка(и) в кавычках после ключевого слова {CodeAnalyzer.TEXT}. Строка {words[ind-1][1]}')
        elif words[ind][0]==CodeAnalyzer.PHOTO and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1
            try:
                el = ImagePost(resPath+words[ind][0][1:len(words[ind][0])-1])
            except Exception as e:
                raise Exception (str(e)+f" Строка {words[ind][1]}")
            if groupMessageFlag:
                groupMessage.append(el)
            else:
                elements.append(el)
            #print(words[ind][0][1:len(words[ind][0])-1])
            ind += 1                
            #if words[ind][2]==CodeAnalyzer.KEYWORD:
            #        raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.PHOTO}. Строка {words[ind-1][1]}')                
        elif words[ind][0]==CodeAnalyzer.VOICE and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1
            try:
                elements.append(VoicePost(resPath+words[ind][0][1:len(words[ind][0])-1]))
            except Exception as e:
                raise Exception (str(e)+f" Строка {words[ind][1]}")
            #print(words[ind][0][1:len(words[ind][0])-1])
            ind += 1
            #if words[ind][2]==CodeAnalyzer.KEYWORD:
            #    raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.VOICE}. Строка {words[ind-1][1]}')                
        elif words[ind][0]==CodeAnalyzer.AUDIO and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1 
            try:
                el = AudioPost(resPath+words[ind][0][1:len(words[ind][0])-1])                    
            except Exception as e:
                raise Exception (str(e)+f" Строка {words[ind][1]}")
            if groupMessageFlag:
                groupMessage.append(el)
            else:
                elements.append(el)
            #print(words[ind][0][1:len(words[ind][0])-1])
            ind += 1
            #if words[ind][2]==CodeAnalyzer.KEYWORD:
            #   raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.AUDIO}. Строка {words[ind-1][1]}')                
        elif words[ind][0]==CodeAnalyzer.VIDEO and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1 
            try:
                el = VideoPost(resPath+words[ind][0][1:len(words[ind][0])-1])
            except Exception as e:
                raise Exception (str(e)+f" Строка {words[ind][1]}")
            if groupMessageFlag:
                groupMessage.append(el)
            else:
                elements.append(el)
            #print(words[ind][0][1:len(words[ind][0])-1])
            ind += 1        
            #if words[ind][2]==CodeAnalyzer.KEYWORD:
            #    raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.VIDEO}. Строка {words[ind-1][1]}')            
        elif words[ind][0]==CodeAnalyzer.GIF and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1  
            try:
                elements.append(GifPost(resPath+words[ind][0][1:len(words[ind][0])-1]))
            except Exception as e:
                raise Exception (str(e)+f" Строка {words[ind][1]}")
            #print(words[ind][0][1:len(words[ind][0])-1])
            ind += 1
            #if words[ind][2]==CodeAnalyzer.KEYWORD:
            #    raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.GIF}. Строка {words[ind-1][1]}')            
        elif words[ind][0]==CodeAnalyzer.DOC and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1
            try:
                el = DocPost(resPath+words[ind][0][1:len(words[ind][0])-1])
            except Exception as e:
                raise Exception (str(e)+f" Строка {words[ind][1]}")
            if groupMessageFlag:
                groupMessage.append(el)
            else:
                elements.append(el)
            #print(words[ind][0][1:len(words[ind][0])-1])
            ind += 1
            #if words[ind][2]==CodeAnalyzer.KEYWORD:
            #    raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.DOC}. Строка {words[ind-1][1]}')            
        elif words[ind][0]==CodeAnalyzer.STICKER and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1  
            try:
                elements.append(StickerPost(resPath+words[ind][0][1:len(words[ind][0])-1]))
            except Exception as e:
                raise Exception (str(e)+f" Строка {words[ind][1]}")
            #print(words[ind][0][1:len(words[ind][0])-1])
            ind += 1
            #if words[ind][2]==CodeAnalyzer.KEYWORD:
            #    raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.STICKER}. Строка {words[ind-1][1]}')            
        elif words[ind][0]==CodeAnalyzer.GROUP and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1
            groupMessageFlag = True
            # print("Группа найдена!")
            if words[ind][0]!=CodeAnalyzer.COLON:
                raise Exception(f'Ожидилось ключевое слово {CodeAnalyzer.COLON} . Строка {words[ind-1][1]}')
            else:
                ind += 1
        elif words[ind][0]==CodeAnalyzer.GROUP_END and words[ind][2]==CodeAnalyzer.KEYWORD:
            ind += 1
            groupMessageFlag = False
            elements.append(GroupPost(groupMessage))
            textFound = False
            groupMessage = []
        elif words[ind][0]==CodeAnalyzer.BUTTONS and words[ind][2]==CodeAnalyzer.KEYWORD:
            buttons = []
            waitSomething.append(words[ind])
            ind += 1
            waitSomething.append(words[ind])
            if words[ind][2]==CodeAnalyzer.STRING:
                buttonsDescription = words[ind][0][1:len(words[ind][0])-1]
                if groupMessageFlag:
                   raise Exception(f'Кнопки не могут входить в группу! Строка {words[ind-1][1]}')
                else:
                    pass
                   # print(buttonsDescription)
                ind += 1
                waitSomething.append(words[ind])
                if not words[ind][0]==CodeAnalyzer.COLON:
                    raise Exception(f'Ожидилось ключевое слово {CodeAnalyzer.COLON} . Строка {words[ind-1][1]}')
                else:
                    ind +=1
                    waitSomething.append(words[ind])
                    while words[ind][0]!=CodeAnalyzer.BUTTONS_END:
                        if words[ind][2]==CodeAnalyzer.STRING:
                            buttons.append(Button(words[ind][0][1:len(words[ind][0])-1]))
                            # print(words[ind][0][1:len(words[ind][0])-1])
                            ind += 1 
                            waitSomething.append(words[ind])
                            if words[ind][0]!=CodeAnalyzer.DOUBLE_DASH:
                                raise Exception(f"Ожидалось ключевое слово {CodeAnalyzer.DOUBLE_DASH}. Строка {words[ind-1][1]}")
                            else:
                                ind += 1
                                waitSomething.append(words[ind])
                                if words[ind-1][1]!=words[ind][1]:
                                    raise Exception(f"Отсутствует действие у кнопки. Строка {words[ind-1][1]}")
                            # print(f'Действие: {words[ind][0]}')
                            ind += 1
                            waitSomething.append(words[ind])
                    #waitSomething.append(words[ind])
                    #if words[ind][2]==CodeAnalyzer.KEYWORD and words[ind][1]!=words[ind-1][1]:
                    #   raise Exception(f'Ожидилось ключевое слово {CodeAnalyzer.BUTTONS_END}. Строка {words[ind][1]}')
                    #print(f'Действие: {words[ind-1][0]}')                    
                    elements.append(ButtonsPost(buttonsDescription, buttons))
            else:
                 raise Exception(f'Ожидилась строка(и) в кавычках после ключевого слова {CodeAnalyzer.BUTTONS}. Строка {words[ind-1][1]}')
        elif words[ind][0]==CodeAnalyzer.WAIT_AUDIO and words[ind][2]==CodeAnalyzer.KEYWORD:
            waitSomething.append(words[ind])
            ind += 1
            while words[ind][0]!=CodeAnalyzer.WAIT_END:
                waitSomething.append(words[ind])
                ind += 1
            waitSomething.append(words[ind])
        elif words[ind][0]==CodeAnalyzer.WAIT_TEXT and words[ind][2]==CodeAnalyzer.KEYWORD:
            waitSomething.append(words[ind])
            ind += 1            
            while words[ind][0]!=CodeAnalyzer.WAIT_END:
                waitSomething.append(words[ind])
                ind += 1
            waitSomething.append(words[ind])
        elif words[ind][0]==CodeAnalyzer.TRANSITION and words[ind][2]==CodeAnalyzer.KEYWORD:
            waitSomething.append(words[ind])
            ind += 1
            if words[ind][2]==CodeAnalyzer.KEYWORD:
                raise Exception(f'Ожидилась строка в кавычках после ключевого слова {CodeAnalyzer.PHOTO}. Строка {words[ind-1][1]}')
            waitSomething.append(words[ind])
        else:
            ind += 1
            if ind>len(words)-1:
                break
    print('=== БЛОКИ СОБРАНЫ. УСТАНАВЛИВАЕМ ПЕРЕХОДЫ... ===')
    remove_quotes(scenes)
    transitions = get_transitions(scenes)
    set_transitions(scenes, transitions)
    print('=== ПЕРЕХОДЫ УСТАНОВЛЕНЫ. ПРОЕКТ СОБРАН ===')
    first_message = scenes[0].getSceneMessages()[0]
    return [token, first_message]


def find_scene_by_name(scenes, name):
    for scene in scenes:
        if scene.getName() == name:
            return scene
    return None


def remove_quotes(scenes):
    for scene in scenes:
        words = scene.trash
        for i in range(len(words)):
            if words[i][2] == CodeAnalyzer.STRING:
                scene.trash[i] = (words[i][0].replace('"', ''), words[i][1], words[i][2])


def get_transitions(scenes):
    transitions = []  # [(from_scene_name, requiered, next_scene_name, is_keyword)]
    for scene in scenes:
        if scene.trash:
            # есть непроанализированные слова (для переходов)
            if scene.trash[0][0] == CodeAnalyzer.WAIT_AUDIO or scene.trash[0][0] == CodeAnalyzer.WAIT_TEXT:
                if len(scene.trash)<2:
                    raise Exception(f'Блок {scene.trash[0][0]} не закрыт. Строка {scene.trash[0][1]}.')
                if scene.trash[1][0] != CodeAnalyzer.COLON or scene.trash[1][2] != CodeAnalyzer.KEYWORD:
                    raise Exception(f'Пропущено двоеточие. Строка {scene.trash[0][1]}.')
                end_idx = 0
                for i in range(1, len(scene.trash)):
                    if scene.trash[i][0] == CodeAnalyzer.WAIT_END and\
                       scene.trash[i][2] == CodeAnalyzer.KEYWORD:
                        end_idx = i
                        break
                if end_idx == 0:
                    raise Exception(f'Блок {scene.trash[0][0]} не закрыт. Строка {scene.trash[0][1]}.')
                content = scene.trash[2:end_idx]
                if not content:
                    raise Exception(f'Блок {scene.trash[0][0]} пуст. Строка {scene.trash[0][1]}.')
                requiered = None
                next_scene = None
                is_keyword = None
                for i in range(len(content)):
                    if content[i][2] == CodeAnalyzer.STRING:
                        if requiered is None:
                            if is_keyword is None:
                                is_keyword = False
                            requiered = content[i][0]
                        elif next_scene is None:
                            if find_scene_by_name(scenes, content[i][0]) is None:
                                raise Exception(f'Сцена {content[i][0]} не найдена. Строка {content[i][1]}.')
                            next_scene = content[i][0]
                        else:
                            raise Exception(f'Ожидалось {CodeAnalyzer.DOUBLE_DASH}. Строка {content[i][1]}.')
                    elif content[i][2] == CodeAnalyzer.KEYWORD:
                        # if content[i][0] == CodeAnalyzer.ASTERISK:
                        #     is_keyword = True
                        #     # if is_keyword is None and requiered is None:
                        #     #     is_keyword == True
                        #     # else:
                        #     #     raise Exception(f'Ключевое слово {CodeAnalyzer.ASTERISK} не на своём месте. Строка {content[i][1]}.')
                        # elif content[i][0] == CodeAnalyzer.DOUBLE_DASH:
                        if content[i][0] == CodeAnalyzer.DOUBLE_DASH:
                            pass
                        elif content[i][0] == CodeAnalyzer.ELSE:
                            if requiered is None:
                                requiered = Transition.SEND_ELSE
                                is_keyword = False
                            else:
                                raise Exception(f'Ключевое слово {CodeAnalyzer.ELSE} не на своём месте. Строка {content[i][1]}.')
                        else:
                            raise Exception(f'Неожиданное ключевое слово {content[i][0]} в блоке {scene.trash[0][0]}. Строка {content[i][1]}.')
                    if not (requiered is None or next_scene is None):
                        transitions.append((scene.name, requiered, next_scene, is_keyword))
                        requiered = None
                        next_scene = None
                        is_keyword = None
            elif scene.trash[0][0] == CodeAnalyzer.BUTTONS:
                if len(scene.trash)<4:
                    raise Exception(f'Блок {scene.trash[0][0]} не закрыт. Строка {scene.trash[0][1]}.')
                if scene.trash[2][0] != CodeAnalyzer.COLON or scene.trash[2][2] != CodeAnalyzer.KEYWORD:
                    raise Exception(f'Пропущено двоеточие. Строка {scene.trash[0][1]}.')
                end_idx = 0
                for i in range(1, len(scene.trash)):
                    if scene.trash[i][0] == CodeAnalyzer.BUTTONS_END and\
                       scene.trash[i][2] == CodeAnalyzer.KEYWORD:
                        end_idx = i
                        break
                if end_idx == 0:
                    raise Exception(f'Блок {scene.trash[0][0]} не закрыт. Строка {scene.trash[0][1]}.')
                content = scene.trash[3:end_idx]
                if not content:
                    raise Exception(f'Блок {scene.trash[0][0]} пуст. Строка {scene.trash[0][1]}.')
                requiered = None
                next_scene = None
                for i in range(len(content)):
                    if content[i][2] == CodeAnalyzer.STRING:
                        if requiered is None:
                            requiered = content[i][0]
                        elif next_scene is None:
                            if find_scene_by_name(scenes, content[i][0]) is None:
                                raise Exception(f'Сцена {content[i][0]} не найдена. Строка {content[i][1]}.')
                            next_scene = content[i][0]
                        else:
                            raise Exception(f'Ожидалось {CodeAnalyzer.DOUBLE_DASH}. Строка {content[i][1]}.')
                    elif content[i][2] == CodeAnalyzer.KEYWORD:
                        if content[i][0] != CodeAnalyzer.DOUBLE_DASH:
                            raise Exception(f'Неожиданное ключевое слово {content[i][0]} в блоке {scene.trash[0][0]}. Строка {content[i][1]}.')
                    if not (requiered is None or next_scene is None):
                        transitions.append((scene.name, requiered, next_scene, CodeAnalyzer.BUTTONS))
                        requiered = None
                        next_scene = None
                        is_keyword = None
            elif scene.trash[0][0] == CodeAnalyzer.TRANSITION:
                if len(scene.trash)<1:
                    raise Exception(f'Пустой переход. Строка {scene.trash[0][1]}.')
                if scene.trash[1][2] != CodeAnalyzer.STRING:
                    raise Exception(f'Ожидалось название сцены для перехода. Строка {scene.trash[0][1]}.')
                if find_scene_by_name(scenes, scene.trash[1][0]) is None:
                    raise Exception(f'Сцена {scene.trash[1][0]} не найдена. Строка {scene.trash[1][1]}.')
                transitions.append((scene.name, Transition.SEND_IMMEDIATELY, scene.trash[1][0], scene.trash[1][0]))
    return transitions


def set_transitions(scenes, transitions):
    # устанавливаем безусловные переходы внутри сцены
    for scene in scenes:
        posts = scene.getSceneMessages()
        stop = len(posts)-1
        for i in range(stop):
            posts[i].add_next(posts[i+1])
    # устанавливаем условные переходы между сценами
    for from_scene_name, requiered, next_scene_name, is_keyword in transitions:
        from_post = find_scene_by_name(scenes, from_scene_name).getSceneMessages()[-1]
        next_post = find_scene_by_name(scenes, next_scene_name).getSceneMessages()[0]
        if is_keyword != CodeAnalyzer.BUTTONS:
            from_post.add_next(next_post, requiered)
        else:
            for button in from_post.content:
                if button.text == requiered:
                    from_post.add_next(next_post, button)
