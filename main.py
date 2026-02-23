from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Plain, Video 
import aiohttp
import tempfile
import os

from astrbot.api import AstrBotConfig,logger

@register("video_plugin", "YourName", "astrbot_plugin_video", "1.0.0", "https://github.com/guowenye/astrbot_plugin_video")
class DwoVideoPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

        logger.info("測試config",self.config)

        # 支持直接保存配置
        self.config.save_config() # 保存配置


        self.api_url = "https://v2.xxapi.cn/api/meinv"
        self.session = aiohttp.ClientSession()


    async def terminate(self):
        await self.session.close()
    @filter.command("video", alias={"小视频", "短视频"})
    async def get_dwo_video(self, event: AstrMessageEvent):
        try:
            params = {"v": "xd"}
            headers = {
            "Authorization": f"Bearer {self.config.get('api_key', '')}"  # 這裡填你的 token
            }

            async with self.session.get(self.api_url, params=params, headers=headers) as response:
                if response.status != 200:
                    yield event.plain_result(f"请求失败：状态码{response.status}")
                    return
                content_type = response.headers.get("content-type", "")
                
                # 根據 Content-Type 判斷如何讀取
                if "application/json" in content_type:
                    context = await response.json()  # 讀取 JSON
                elif "text/" in content_type:
                    context = await response.text()  # 讀取文字
                else:
                    context = await response.read()  # 讀取原始 bytes


                logger.info(f"API 响应内容类型：{content_type}")
                logger.info(f"視頻信息：{context}")
                
                video_url = str(context.get("data", ""))

                video_component = Video.fromURL(video_url)
                logger.info(f"視頻組件：{video_component}")

                message_chain = [
                    Plain("视频获取成功！") ,
                    video_component,
                    Plain(f"视频链接：{video_url}")
                   
                ]

                yield event.chain_result(message_chain)
        
                if self.config.get("debug_mode", False):
                    message_chain = [
                        Plain(f"\u200b\n响应内容类型：{content_type}"),
                        Plain(f"\nAPI 响应内容：{context}\u200b")
                    ]
                    yield event.chain_result(message_chain)
        
        except aiohttp.ClientError as e:
            yield event.plain_result(f"网络请求出错：{str(e)}")
        except Exception as e:
            yield event.plain_result(f"发生未知错误：{str(e)}")
            import traceback
            traceback.print_exc()
