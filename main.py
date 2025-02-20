from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import aiohttp
import asyncio

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
