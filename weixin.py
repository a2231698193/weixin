import datetime
import json
import random
import time
import requests
import yaml


class Weixin:
    def __init__(self):
        fp = open('config.yaml', 'r', encoding='utf-8')
        msg = yaml.load(fp, Loader=yaml.FullLoader)
        fp.close()
        week_list = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        year = time.strftime('%Y', time.localtime(time.time()))
        month = time.strftime('%m', time.localtime(time.time()))
        day = time.strftime('%d', time.localtime(time.time()))
        self.date = time.strftime('%Y-%m-%d', time.localtime(time.time())) + ' ' + week_list[
            datetime.date(int(year), int(month), int(day)).weekday()]
        # 地区
        self.region = msg['region']
        # appID
        self.appID = msg['appID']
        # appsecret
        self.appsecret = msg['appsecret']
        # 模板id
        self.template_id = msg['template_id']
        self.openid_list = []
        # 相恋日期
        self.xlday_num = msg['xlday_num']
        # 阳历生日
        self.birthday = msg['birthday']
        # 天气地区id
        self.location = '101010100'
        # 天气key
        self.weather_key = msg['weather_key']

    def get_user_birthday(self):
        birthdays = self.birthday.split('-')
        birthday = datetime.datetime(int(birthdays[0]), int(birthdays[1]), int(birthdays[2]))
        return birthday

    def calculate_dates(self, original_date, now):
        date1 = now
        date2 = datetime.datetime(now.year, original_date.month, original_date.day)
        delta = date2 - date1
        days = delta.total_seconds() / 60 / 60 / 24

        return days

    # 获取颜色
    def random_color(self):
        colors1 = '0123456789ABCDEF'
        num = "#"
        for i in range(6):
            num += random.choice(colors1)
        return num

    # 获取天气
    def get_weather(self):
        url = f"https://devapi.qweather.com/v7/weather/now?location={self.location}&key={self.weather_key}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return json.loads(response.text)

    # 获取金山词句
    def get_jinshan(self):
        url = "http://open.iciba.com/dsapi/"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return json.loads(response.text)

    def get_xlday(self):
        url = "https://www.aiunv.com/rqjsq/search"

        payload = json.dumps({
            "start": self.xlday_num,
            "end": time.strftime('%Y-%m-%d', time.localtime(time.time()))
        })
        headers = {
            'Content-Type': 'application/json',
            'Cookie': 'PHPSESSID=c5708950a3d34dba9d4fd63c7235e2f3'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return json.loads(response.text)

    # 获取token
    def get_token(self):
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appID}&secret={self.appsecret}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return json.loads(response.text)

    # 获取关注用户列表
    def get_user_list(self):
        url = f"https://api.weixin.qq.com/cgi-bin/user/get?access_token={self.get_token()['access_token']}"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        self.openid_list = json.loads(response.text)['data']['openid']

    # 推送模板消息
    def send_template(self, touser):
        bd = self.get_user_birthday()
        now = datetime.datetime.now()
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={self.get_token()['access_token']}"

        get_weather = self.get_weather()
        data_body = {
            "touser": touser,
            "template_id": self.template_id,
            "url": "https://baidu.com",
            "topcolor": self.random_color(),
            "data": {
                "date": {
                    "value": self.date,
                    "color": self.random_color()
                },
                "region": {
                    "value": self.region,
                    "color": self.random_color()
                },
                "weather": {
                    "value": f"{get_weather['now']['text']}",
                    "color": self.random_color()
                },
                "temp": {
                    "value": get_weather['now']['temp'] + '℃',
                    "color": self.random_color()
                },
                "wind_dir": {
                    "value": f"{get_weather['now']['windDir']}",
                    "color": self.random_color()
                },
                "love_day": {
                    "value": self.get_xlday()['data'],
                    "color": self.random_color()
                },
                "birthday": {
                    "value": int(self.calculate_dates(bd, now)),
                    "color": self.random_color()
                },
                "note_en": {
                    "value": self.get_jinshan()['note'],
                    "color": self.random_color()
                },
                "note_ch": {
                    "value": self.get_jinshan()['content'],
                    "color": self.random_color()
                },
            }
        }
        data = json.dumps(data_body)
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=data)

        print(f"推送成功：{touser} - {response.text}")


if __name__ == "__main__":
    weixin = Weixin()
    weixin.get_user_list()
    weixin.send_template('oStYf5qXLC57m4NOhpoyb_iXvPB8')
    # for i in weixin.openid_list:
    #     weixin.send_template(i)
    #     time.sleep(1)
