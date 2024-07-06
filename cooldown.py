import time
import json

from typing import Optional, Tuple, Dict

class CooldownManager:
    def __init__(self, file_path: str, execution_period: int, cooldown_duration: int):
        """
        该class需要初始化

        file_path: 要保存冷却信息的json路径（如果文件不存在则会在初始化时创建）
        execution_period: 指令可触发时间段（秒），在此之后进入冷却
        cooldown_duration: 冷却时长
        """
        self.file_path = file_path
        self.execution_period = execution_period
        self.cooldown_duration = cooldown_duration
        self.cooldowns: Dict[str, Dict[str, int]] = self.load_cooldowns()

    def load_cooldowns(self) -> Dict[str, Dict[str, int]]:
        """
        从json文件加载冷却数据。如果文件不存在或为空，则创建一个空文件并加载
        """
        try:
            with open(self.file_path, 'r') as f: 
                # 检查json是否为空
                content = f.read().strip()
                if content:
                    return json.loads(content)
                else:
                    return {}
        except FileNotFoundError:
            # json不存在时创建一个空json并初始化
            with open(self.file_path, 'w') as f:
                json.dump({}, f)
            return {}

    def save_cooldowns(self) -> None:
        """
        将冷却数据保存到文件
        """
        with open(self.file_path, 'w') as f:
            json.dump(self.cooldowns, f, indent=4)

    async def check_and_update_cooldown(self, group_id: str, response_time: Optional[int] = None) -> Tuple[bool, int]:
        """
        检查冷却状态并更新

        group_id: 群组ID
        response_time: 可等待的响应时间（秒），可选

        return: 包含是否处于冷却状态和剩余冷却时间的Tuple
        """
        current_time = int(time.time())
        if group_id in self.cooldowns:
            command_trigger = self.cooldowns[group_id]['command_trigger']
            cooldown_start = self.cooldowns[group_id]['cooldown_start']
            cooldown_end = self.cooldowns[group_id]['cooldown_end']
            await self.update_trigger(group_id) # 每次触发都进行触发时间的更新

            if response_time != None and current_time - command_trigger > response_time and current_time < cooldown_start: # 进入冷却前长时间未响应后触发指令，重置冷却
                await self.start_cooldown(group_id)
                return False, 0
            if current_time < cooldown_start: # 触发时还未到冷却期开始时间
                return False, 0
            elif current_time < cooldown_end: # 触发时已经进入冷却期
                remaining_time = cooldown_end - current_time
                return True, remaining_time
            else:
                await self.start_cooldown(group_id)
                return False, 0
        else:
            await self.start_cooldown(group_id)
            return False, 0

    async def update_trigger(self, group_id: str) -> None:
        """
        更新指令触发时间
        """
        command_trigger = int(time.time())
        if group_id in self.cooldowns:
            self.cooldowns[group_id]['command_trigger'] = command_trigger
        self.save_cooldowns()

    async def start_cooldown(self, group_id: str) -> None:
        """
        开始冷却
        """
        current_time = int(time.time())
        command_trigger = current_time # 指令触发时间
        cooldown_start = current_time + self.execution_period # 冷却开始时间
        cooldown_end = cooldown_start + self.cooldown_duration # 冷却结束时间
        if group_id in self.cooldowns:
            self.cooldowns[group_id]['cooldown_start'] = cooldown_start
            self.cooldowns[group_id]['cooldown_end'] = cooldown_end
        else:
            self.cooldowns[group_id] = {
                'command_trigger': command_trigger,
                'cooldown_start': cooldown_start,
                'cooldown_end': cooldown_end
            }
        self.save_cooldowns()
