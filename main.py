from astrbot.api.message_components import *
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
import aiohttp


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
        # 检查是否配置了API URL
        if not self.api_url:
            yield event.plain_result("\n请先在配置文件中设置API地址")
            return
        # 创建一个不验证SSL的连接上下文
        ssl_context = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=ssl_context) as session:
            for i in range(n):
                try:
                    # 构建消息链
                    chain = [
                        Plain("正在发送~~~"),

                        Image.fromURL(self.nh_url)  # 从URL加载图片
                    ]

                    yield event.chain_result(chain)
                except Exception as e:
                    yield event.plain_result(f"\n请求失败: {str(e)}")

    @filter.command("imgh")
    async def get_setu(self, event: AstrMessageEvent):
        # 检查是否配置了API URL
        if not self.api_url:
            yield event.plain_result("\n请先在配置文件中设置API地址")
            return

        # 创建一个不验证SSL的连接上下文
        ssl_context = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=ssl_context) as session:
            try:

                # 构建消息链
                chain = [
                    Plain("正在发送~~~"),
                    Image.fromURL(self.h_url)  # 从URL加载图片
                ]

                yield event.chain_result(chain)
            except Exception as e:
                yield event.plain_result(f"\n请求失败: {str(e)}")
