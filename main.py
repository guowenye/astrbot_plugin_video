from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Plain, Video 
import aiohttp
import tempfile
import os

@register("video_plugin", "YourName", "astrbot_plugin_video", "1.0.0", "https://github.com/guowenye/astrbot_plugin_video")
class DwoVideoPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_url = "https://api.dwo.cc/api/video"
        self.session = aiohttp.ClientSession()
    async def terminate(self):
        await self.session.close()
    @filter.command("video", alias={"小视频", "短视频"})
    async def get_dwo_video(self, event: AstrMessageEvent):
        try:
            params = {"v": "xd"}
            async with self.session.get(self.api_url, params=params) as response:
                if response.status != 200:
                    yield event.plain_result(f"请求失败：状态码{response.status}")
                    return
                content_type = response.headers.get("content-type", "")
                video_url = str(response.url)
                video_component = Video.fromURL(video_url)
                message_chain = [
                    video_component,
                    Plain("视频获取成功！") 
                ]
                yield event.chain_result(message_chain)
        except aiohttp.ClientError as e:
            yield event.plain_result(f"网络请求出错：{str(e)}")
        except Exception as e:
            yield event.plain_result(f"发生未知错误：{str(e)}")
            import traceback
            traceback.print_exc()