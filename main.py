from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import aiohttp
import asyncio
import hashlib
import random
import string
import requests
import xml.etree.ElementTree as ET
import subprocess
import re
import glob
from astrbot.api.message_components import Video
@register("fish_apiimg", "案板上的鹹魚", "从API获取图片。双路径：使用 /img 和/imgh 获取。(自用)", "1.0")
class SetuPlugin(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        self.api_url = config.get("api_url", "")
        self.h_url = self.api_url +'/H'
        self.nh_url = self.api_url +'/NON-H'
    @filter.command("img")
    async def get_tu(self, event: AstrMessageEvent,n: int = 1):
        if n>20 :
            yield event.plain_result("你要恁多干哈？")
            return
        # 检查是否配置了API URL
        if not self.api_url:
            yield event.plain_result("\n请先在配置文件中设置API地址")
            return
        # 创建一个不验证SSL的连接上下文
        ssl_context = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.head(self.nh_url, timeout=2) as resp:
                    if resp.status != 200:
                        raise ValueError(f"图片 URL 无效，状态码: {resp.status}")
            except Exception as e:
                yield event.plain_result(f"请求失败: {str(e)}")
                return
            for i in range(n):
                try:

                    # 构建消息链
                    chain = [

                        Plain(f"正在发送~~~({i + 1}/{n})"),
                        Image.fromURL(self.nh_url)  # 从URL加载图片

                    ]
                    yield event.chain_result(chain)
                    await asyncio.sleep(1)
                except Exception as e:
                    yield event.plain_result(f"\n请求失败: {str(e)}")

    @filter.command("imgh")
    async def get_setu(self, event: AstrMessageEvent,n: int = 1):
        if n>20 :
            yield event.plain_result("你要恁多干哈？")
            return
        # 检查是否配置了API URL
        if not self.api_url:
            yield event.plain_result("\n请先在配置文件中设置API地址")
            return

        # 创建一个不验证SSL的连接上下文
        ssl_context = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession() as session:
            try:
                async with session.head(self.h_url, timeout=2) as resp:
                    if resp.status != 200:
                        raise ValueError(f"图片 URL 无效，状态码: {resp.status}")
            except Exception as e:
                yield event.plain_result(f"请求失败: {str(e)}")
                return
            for i in range(n):
                try:

                    # 构建消息链
                    chain = [
                        Plain(f"正在发送~~~({i+1}/{n})"),
                        Image.fromURL(self.h_url)  # 从URL加载图片
                    ]

                    yield event.chain_result(chain)
                except Exception as e:
                    yield event.plain_result(f"\n请求失败: {str(e)}")

    def sanitize_filename(self,filename):
        """ 清理文件名非法字符 """
        return re.sub(r'[\\/:*?"<>|]', '_', filename)

    def convert_to_wechat_mp3(self,input_file, output_file):
        """
        使用 ffmpeg 把歌曲转换成微信语音格式（amr-nb 8000Hz 单声道）
        """
        command = [
            'ffmpeg',
            '-i', input_file,  # 输入文件
            '-ar', '8000',  # 采样率22.05kHz（降低采样率以减少文件大小）
            '-ac', '1',  # 单声道
            '-b:a', '32k',  # 比特率32kbps（极限压缩）
            '-y',  # 覆盖已有文件
            output_file  # 输出文件（记得保证后缀是.mp3）
        ]
        subprocess.run(command, check=True)
        command = [
            'ffmpeg',
            '-i', input_file,  # 输入文件
            '-ar', '8000',  # 设置采样率为 8000 Hz
            '-ac', '1',  # 单声道
            '-b:a', '32k',  # 设置比特率为 32 kbps
            '-f', 'segment',  # 使用分段模式
            '-segment_time', '59',  # 每段最大时长为 59 秒
            '-y',  # 强制覆盖已有文件
            'output%03d.wav'  # 输出文件（多个分段的文件）
        ]
        subprocess.run(command, check=True)
        output_files = glob.glob('output*.wav')
        subprocess.run(['rm', input_file], check=True)
        return output_files

    @filter.command("getsong")
    async def get_song(self, event: AstrMessageEvent):
        try:
            username = 'admin'
            password = 'qwer3866373'
            size = "1"
            # 生成一个随机盐值（至少6个字符）
            salt = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            # 计算 token
            token = hashlib.md5(f'{password}{salt}'.encode('utf-8')).hexdigest()
            url = f'https://music.icystar.de/rest/getRandomSongs?u={username}&t={token}&s={salt}&v=1.16.1&c=myapp&size={size}'
            response = requests.get(url)
            root = ET.fromstring(response.text)
            # 解析 XML 时，处理命名空间
            namespace = {'subsonic': 'http://subsonic.org/restapi'}
            # 提取歌曲信息
            songs = root.findall('.//subsonic:randomSongs/subsonic:song', namespace)

            song=songs[0]
            song_id = song.get('id')
            title = song.get('title')
            album = song.get('album')
            artist = song.get('artist')
            year = song.get('year')
            duration = song.get('duration')
            path = song.get('path')
            suffix = song.get('suffix')
            url = f'https://music.icystar.de/rest/download?u={username}&t={token}&s={salt}&v=1.16.1&c=myapp&id={song_id}'
            download_response = requests.get(url)
            filename = f"{title}.{suffix}"
            with open(filename, 'wb') as file:
                file.write(download_response.content)
            print(f"已保存: {filename}")
            input_file = filename
            output_file = title + '.wav'
            # 执行转换
            output_files=self.convert_to_wechat_mp3(input_file, output_file)
            chain=[]
            for item in output_files:
                chain.append(Record.fromFileSystem(item))
            chain.append(Plain("已经发送音乐"))
            yield event.chain_result(chain)
            subprocess.run(['rm', output_file], check=True)

        except Exception as e:
            yield event.plain_result(f"\n请求失败: {str(e)}")