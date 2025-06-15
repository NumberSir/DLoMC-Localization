import json
import re

from loguru._logger import Logger
from lxml import etree
from lxml.etree import Element, ElementTree

from src.config import *
from src.log import logger
from src.schema import *


class Tweaker:
    """tiny tweaks"""
    def __init__(self):
        self._logger = logger.bind(project_name="Tweaker")

    def tweak(self):
        self.logger.info("")
        self.logger.info("======= TWEAK START =======")
        self.tweak_game_title()
        self.tweak_game_plugins()

    def tweak_game_title(self):
        with (GAME_ROOT / "www" / "index.html").open("r", encoding="utf-8") as fp:
            root: Element = etree.HTML(fp.read())

        newtitle = etree.Element("title")
        newtitle.text = settings.game.name_translation

        head = root.find("head").__copy__()
        head.remove(head.find("title"))
        head.append(newtitle)

        root.remove(root.find("head"))
        root.insert(0, head,)

        tree: ElementTree = etree.ElementTree(root)
        (DIR_RESULT / "www").mkdir(parents=True, exist_ok=True)
        tree.write(DIR_RESULT / "www" / "index.html", encoding="utf-8", method="html")
        self.logger.success("Tweak game title successfully.")

    def tweak_game_plugins(self):
        with (GAME_ROOT / "www" / "js" / "plugins.js").open("r", encoding="utf-8") as fp:
            content = fp.read()

        pattern = re.compile(r"var \$plugins =\s*(\[[\s\S]+?]);")
        plugins_string = re.findall(pattern, content)[0]
        plugins_data = json.loads(plugins_string)

        plugins = [
            GamePluginModel(**plugin)
            for plugin in plugins_data
        ]
        for idx, plugin in enumerate(plugins):
            if plugin.name == "YEP_SaveCore":
                plugins[idx] = self._tweak_game_plugin_save_core(plugin)
                continue
            if plugin.name == "MOG_TimeSystem":
                plugins[idx] = self._tweak_game_plugin_time_system(plugin)
                continue
            if plugin.name == "Galv_QuestLog":
                plugins[idx] = self._tweak_game_plugin_questlog(plugin)
                continue
            if plugin.name == "RecipeCrafting":
                plugins[idx] = self._tweak_game_plugin_recipe_crafting(plugin)
                continue
            if plugin.name == "SRD_CreditsPlugin":
                plugins[idx] = self._tweak_game_plugin_credit(plugin)
                continue

        plugins = [
            model.model_dump()
            for model in plugins
        ]
        content = content.replace(plugins_string, json.dumps(plugins, ensure_ascii=False))
        (DIR_RESULT / "www" / "js").mkdir(parents=True, exist_ok=True)
        with (DIR_RESULT / "www" / "js" / "plugins.js").open("w", encoding="utf-8") as fp:
            fp.write(content)
        self.logger.success("Tweak game plugins successfully.")

    def _tweak_game_plugin_save_core(self, plugin: GamePluginModel) -> GamePluginModel:
        """Save menu related function"""
        name_mapping = {
            "Load Command": "加载",
            "Save Command": "保存",
            "Delete Command": "删除",
            "Select Help": "请选中一处文件位。",
            "Load Help": "从游戏存档中加载数据。",
            "Save Help": "保存当前游戏进度。",
            "Delete Help": "删除所选存档中的所有数据。",
            "Invalid Game Text": "所选存档是另一个游戏的。",
            "Empty Game Text": "空白",
            "Map Location": "地图位置：",
            "Playtime": "游玩时间：",
            "Save Count": "存档总数：",
            "Web Config": "RPG %1 设置",
            "Web Global": "RPG %1 全局",
            "Web Save": "RPG %1 文件%2",
            "Load Text": "你确定要加载这个存档吗？",
            "Save Text": "你确定要覆盖这个存档吗？",
            "Delete Text": "你确定要删除这个存档吗？",
            "Confirm Yes": "是",
            "Confirm No": "否"
        }
        plugin.parameters |= name_mapping
        return plugin

    def _tweak_game_plugin_time_system(self, plugin: GamePluginModel) -> GamePluginModel:
        """Time system ingame"""
        name_mapping = {
            "Day Week Names": "星期日,星期一,星期二,星期三,星期四,星期五,星期六",
            "Season Names": "春季,夏季,秋季,冬季",
            "Month Names": "一月,二月,三月,四月,五月,六月,七月,八月,九月,十月,十一月,十二月",
            "Time Word": "时间",
            "Day Word": "日",
            "Day Week Word": "周",
            "Month Word": "月",
            "Season Word": "季",
            "Year Word": "年",
            "Play Time Word": "游玩时间",
        }
        plugin.parameters |= name_mapping
        return plugin

    def _tweak_game_plugin_questlog(self, plugin: GamePluginModel) -> GamePluginModel:
        """Quests ingame"""
        name_mapping = {
            "Categories": "主要任务|#ffcc66,支线任务|#ffff99,制作任务|#ccccff,日常任务|#FFF5E3",
            "Quest Command": "任务日志",
            "Active Cmd Txt": "活跃的任务",
            "Completed Cmd Txt": "完成的任务",
            "Failed Cmd Txt": "失败的任务",
            "Desc Txt": "任务细节",
            "Objectives Txt": "任务目标",
            "Difficulty Txt": "任务难度",
            "No Tracked Quest": "未选中任何任务",
            "Pop New Quest": "新任务领取：",
            "Pop Complete Quest": "任务已完成：",
            "Pop Fail Quest": "任务已失败：",
            "Pop New Objective": "新任务目标：",
            "Pop Complete Objective": "任务目标已完成：",
            "Pop Fail Objective": "任务目标未完成："
        }
        plugin.parameters |= name_mapping
        return plugin

    def _tweak_game_plugin_recipe_crafting(self, plugin: GamePluginModel) -> GamePluginModel:
        """Recipes ingame"""
        name_mapping = {
            "Main Menu String": "制作合成",
            "Required Level Text": "所需等级：",
            "Required Material Text": "所需材料：",
            "Returned Material Text": "返还材料：",
            "Reverse Recipe Prefix": "拆除",
            "Success Rate Text": "成功率：",
            "Exp Gained Text": "制作获取经验：",
            "Crafting Cost Text": "制作消耗：",
            "Crafting Text": "制作",
            "Crafted Text": "制作完成！",
            "Crafting Failed": "制作失败！",
            "Dismantle Text": "拆除",
            "Dismantled Text": "返还了！",
            "Dismantle Fail": "什么都没得到！",
        }
        plugin.parameters |= name_mapping
        return plugin

    def _tweak_game_plugin_credit(self, plugin: GamePluginModel) -> GamePluginModel:
        """Credits in main menu"""
        parameters = plugin.parameters
        rawdata: str = parameters["Credit Data"]
        parsed_data = json.loads(rawdata)
        parsed_data = [json.loads(_) for _ in parsed_data]

        name_mapping = {
            "Plugins": "插件",
            "Art Assets": "美术",
            "Music": "音乐",
            "Patron": "赞助",
        }
        for idx, data in enumerate(parsed_data):
            parsed_data[idx]["Name"] = name_mapping[data["Name"]]

        # localization_credits = await Credit().build_paratranz_members()
        newdata = {
            "Name": "游戏汉化",
            "Credits": json.dumps([
                json.dumps({
                    "Name": "牛津街大学英语A1-2025级", "URL": "", "Description": ""
                }, ensure_ascii=False)
            ], ensure_ascii=False),
        }
        parsed_data.append(newdata)

        revert_data = json.dumps([json.dumps(_, ensure_ascii=False) for _ in parsed_data], ensure_ascii=False)
        plugin.parameters["Credit Data"] = revert_data
        plugin.parameters["Command Name"] = "致谢名单"
        return plugin

    @property
    def logger(self) -> Logger:
        return self._logger


__all__ = [
    "Tweaker"
]