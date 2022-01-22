from typing import Text
import requests
from requests.api import head
import json
import time
from requests.models import parse_header_links
class bilibili:
    def __init__(self):
        self.cookie = {
            "cookie": "innersign=0; buvid3=032DBD12-089C-20C3-E9C7-C1F64B85CB6E43674infoc; b_lsid=7CBA4BA3_17E6214F43B; _uuid=849D8928-7EB5-F597-2C63-E1C10A6452108C47492infoc; buvid_fp=736374E4-FE4E-F8AF-1D3B-0030747158D988266infoc; fingerprint=9a108c9c103085fb8057ddb9be1272e5; buvid_fp_plain=F4041468-440B-0ECE-CB25-44569596A36238809infoc; SESSDATA=485c46e0%2C1657875082%2C8606f%2A11; bili_jct=3b952edeec8c1da448ba1a78912bd2bc; DedeUserID=380058213; DedeUserID__ckMd5=606a83eea588e3b0; sid=6wpv1s1r; i-wanna-go-back=-1; b_ut=5; bp_video_offset_380058213=616259078918190100; PVID=2"
        }
        self.head = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        }
        self.uid = 380058213


    def get_csrf(self):
        for i in self.cookie["cookie"].split(";"):
            if 'bili_jct=' in i:
                strList = i.split('=')
                return strList[1]

    def Check(self):
        url_unread = 'https://api.bilibili.com/x/msgfeed/unread?build=0&mobi_app=web'
        r = requests.get(url_unread,cookies=self.cookie,headers=self.head)
        params = json.loads(r.text)
        return params["data"]["at"]
        print(json.dumps(params,sort_keys=True,ensure_ascii=False,indent=4))
        print(params["data"]["at"])

    def get_at(self):
        url_at = 'https://api.bilibili.com/x/msgfeed/at?build=0&mobi_app=web'
        r = requests.get(url_at,cookies=self.cookie,headers=self.head)
        params = json.loads(r.text)
        # print(json.dumps(params,sort_keys=True,ensure_ascii=False,indent=4))
        return params["data"]["items"]

    #dynamic_id = subject_id
    #replytype = business_id
    #root = target_id
    #parent = source_id
    #ordering = 该参数疑似无用
    #csrf = 从cookie中获取
    def add_comment(self,dynamic_id,replytype,root,parent,comment,csrf):
        data = {
            "oid": dynamic_id,
            "type": replytype,
            "root":root,
            "parent":parent,
            "message": comment,
            "plat": "1",
            "jsonp": "jsonp",
            "csrf": csrf
        }
        url = 'https://api.bilibili.com/x/v2/reply/add'
        r = requests.post(url,headers=self.head,cookies=self.cookie,data=data)
        # r_json = json.loads(r.text)
        # print(json.dumps(r_json,sort_keys=True,indent=4,ensure_ascii=False))

    #通过api获取共同关注
    def get_vup(self,uid):
        url = 'https://api.bilibili.com/x/relation/same/followings?vmid={}'.format(uid)
        r = requests.get(url,headers=self.head,cookies=self.cookie)
        params = json.loads(r.text)
        # r_json = json.loads(r.text)
        # print(json.dumps(r_json,sort_keys=True,indent=4,ensure_ascii=False))
        if params["code"] == 22115:
            print("未打开关注列表")
            return params["code"]
        else:
            nameList = []
            for i in params["data"]["list"]:
                nameList.append(i['uname'])
            return nameList
        r_json = json.loads(r.text)
        print(json.dumps(r_json,sort_keys=True,indent=4,ensure_ascii=False))

    #发送私信
    def send_msg(self,uid,message,csrf):
        data = {
            'msg[sender_uid]': self.uid,
            'msg[receiver_id]': uid,
            'msg[receiver_type]': '1',
            'msg[msg_type]': '1',
            'msg[msg_status]': '0',
            # 'msg[content]': str({"content":"{}".format(message)}),
            'msg[content]': str({"content": "{}".format(message)}).replace("\'", "\""),
            'msg[timestamp]': int(time.time()),
            'msg[new_face_version]': '0',
            'msg[dev_id]': 'E2B3CA11-7A0D-438D-B420-0A41434C0C83',
            # 'from_firework': '0',
            # 'build': '0',
            # 'mobi_app': 'web',
            'csrf_token': csrf,
            'csrf': csrf,
        }
        url = 'https://api.vc.bilibili.com/web_im/v1/web_im/send_msg'
        r = requests.post(url,cookies=self.cookie,headers=self.head,data=data)
        # r_json = json.loads(r.text)
        # print(json.dumps(r_json,sort_keys=True,indent=4,ensure_ascii=False))
    def get_uid(self, root, oid, thetype):
        url = 'https://api.bilibili.com/x/v2/reply/jump?rpid={}&oid={}&type={}'.format(root,oid,thetype)
        r = requests.get(url)
        data_json = r.json()
        # r_json = json.loads(r.text)
        # print(json.dumps(r_json,sort_keys=True,indent=4,ensure_ascii=False))
        if data_json['code'] == 0:
            for i in data_json['data']['replies']:
                if i['rpid'] == root:
                    return i['mid'], i['member']['uname']
                else:
                    try:
                        for j in i['replies']:
                            if j['rpid'] == root:
                                return j['mid'], j['member']['uname']
                    except Exception:
                        continue
    def run(self):
        # while True:
            num = self.Check()
            # print(num)
            if(num != 0):
                params = self.get_at()
                for i in range(num):
                    
                    dynamic_id = params[i]['item']["subject_id"]
                    replytype = params[i]['item']["business_id"]
                    root = params[i]['item']["target_id"]
                    #parent = params[i]['item']["source_id"]
                    csrf = self.get_csrf()
                    uid,name = self.get_uid(root,dynamic_id,replytype)
                    sender_uid = params[0]['user']['mid']
                    print(uid)
                    if root != 0:
                        vups = self.get_vup(uid)
                        message = ''
                        if vups == 22115:
                            message = '此人未打开关注'
                        elif not vups:
                            message = '未关注任何vup'
                        else:
                            for vup in vups:
                                message = message+' '+vup
                            
                        self.send_msg(uid = sender_uid,message=message,csrf = csrf)
                        print(message)
                        # time.sleep(5)

if __name__ == '__main__':
    bilibili().run()
    # params = bilibili().get_at()
    # print(params)
    # dynamic_id = params[0]['item']["subject_id"]
    # replytype = params[0]['item']["business_id"]
    # root = params[0]['item']["target_id"]
    # print(bilibili().get_uid(root,dynamic_id,replytype))
    # parent = params[0]['item']["source_id"]
    
    # csrf = bilibili().get_csrf()
    
    # # comment = 'hello'
    # # bilibili().add_comment(dynamic_id,replytype,root,parent,comment,csrf)
    # #uid = params[0]['user']['mid']
    # vups = bilibili().get_vup(20109634)
    # message = ''
    # if vups == 22115:
    #     print("未打开")
    # elif not vups:
    #     print("无")
    # else:
        
    #     for vup in vups:
    #         message = message+' '+vup
    # print(message)
    # bilibili().send_msg(uid =23709126,message=message,csrf = csrf)