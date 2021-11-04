import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models
import requests
import re
import time

def ReturnRecordId(Domain, SubDomain):
    # 获取指定记录的RecordId
    # Domain 主域名
    # SubDomain 待修改的子域
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = dnspod_client.DnspodClient(cred, "", clientProfile)

        req = models.DescribeRecordListRequest()
        params = {
            "Domain": Domain
        }
        req.from_json_string(json.dumps(params))

        resp = client.DescribeRecordList(req)
        for record in resp.RecordList:
            if record.Name == SubDomain:
                return record.RecordId
        print("未找到对应的记录值，请先创建相应的主机记录！")
        return -2

    except TencentCloudSDKException as err:
        print("获取域名的记录列表失败，请重试！")
        return -1

def ModifyDynamicDNS(RecordId, Domain ,SubDomain, Ip):
    # 动态域名解析API
    # RecordId 待修改记录ID
    # Domain 主域名
    # SubDomain 子域名
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = dnspod_client.DnspodClient(cred, "", clientProfile)

        req = models.ModifyDynamicDNSRequest()
        params = {
            "Domain": Domain,
            "SubDomain": SubDomain,
            "RecordId": RecordId,
            "RecordLine": "默认",
            "Value": Ip
        }
        req.from_json_string(json.dumps(params))

        resp = client.ModifyDynamicDNS(req)
        if str(RecordId) in resp.to_json_string():
            print("更新成功！")
        return 1
    except TencentCloudSDKException as err:
        return 0
   
def GetCurrentIP():
    resp = requests.get('https://ip.tool.lu/').content
    resp = resp.decode('utf8')
    IPPattern = '\d+.\d+.\d+.\d+' 
    matchObj = re.search(IPPattern, resp)
    return matchObj.group()

if __name__ == "__main__":
    SecretId = ""
    SecretKey = ""
    Domain = "eatrice.cn" # 主域名
    SubDomain = "homesource" # 指定要修改的子域名
    interval = 600 # 每10分钟检查一次IP
    RecordId = ReturnRecordId(Domain=Domain, SubDomain=SubDomain)
    if RecordId == -1:
        print("RecordList请求发生问题！")
        exit()
    if RecordId == -2:
        print("没有找到你要的子域名，请先新建一个！")
    OldIP = ""
    while True:
        CurrentIP = GetCurrentIP()
        if OldIP != CurrentIP:
            res = ModifyDynamicDNS(RecordId=RecordId, Domain=Domain, SubDomain=SubDomain, Ip = CurrentIP)
            if res:
                print(f'IP成功更新！原IP:{OldIP}，新IP:{CurrentIP}')
                OldIP = CurrentIP
            else:
                print('动态域名解析API出问题了，正在重试！')
                continue
        time.sleep(interval)