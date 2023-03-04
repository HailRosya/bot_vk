import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


def check_admins_of_chat(vk,chat_id:int) -> list:
    list_of_admins_from_chat_id = []
    members = vk.method('messages.getConversationMembers', {'peer_id': chat_id})

    for user in members["items"]:
        admin = user.get("is_admin", False)
        if admin:
            list_of_admins_from_chat_id.append(user["member_id"])
    return list_of_admins_from_chat_id


def get_not_allowed_links_from_file(filename:str) -> list:
    links = []
    with open(filename,"r") as f:
        for line in f:
            links.append(f.replace("\n",""))
    return links


def check_user_message(user_id:int,message_id:int,peer_id:int,request:str,not_allowed_links:list):
    if not (request.find("http://") or request.find("https://")):
        return
    list_of_admins = check_admins_of_chat(vk,peer_id)
    if user_id in list_of_admins:
        return  
    for link in not_allowed_links:
        # Каменная логика действий
        if (request.find(link) < 0):
            continue
        delete_msg(vk,peer_id, message_id)
        remove_from_chat(vk,peer_id, user_id)
        return


# Удаляет одно сообщение для всех в чате
def delete_msg(vk,peer_id:int, message_to_delete_id:int):
    vk.method('messages.delete', {'peer_id': peer_id, 'message_ids': message_to_delete_id,'delete_for_all': 1})


# Исключает пользователя из чата
def remove_from_chat(vk,peer_id:int, user_id:int):
    vk.method('messages.removeChatUser', {'chat_id':(peer_id-2000000000), 'member_id':user_id})


def main(vk):

    not_allowed_links = get_not_allowed_links_from_file('not_allowed_links.txt')
    
    # Работа с сообщениями
    longpoll = VkLongPoll(vk)

    # Основной цикл
    for event in longpoll.listen():

        # Если пришло новое сообщение
        if (event.type != VkEventType.MESSAGE_NEW):
            continue
        # Если оно имеет метку для меня(то есть бота) и пришло из группового чата
        if not (event.to_me and event.from_chat):
            continue
        # Сообщение от пользователя
        user_text = event.text
        check_user_message(event.user_id,event.message_id,event.peer_id,user_text,not_allowed_links)


if __name__ == "__main__":
    with open("GROUP_TOKEN.txt","r") as f:

        #API-ключ созданный ранее
        TOKEN = f.read().replace("\n","")

    #Авторизуемся как сообщество
    vk = vk_api.VkApi(token=TOKEN)
    main(vk)