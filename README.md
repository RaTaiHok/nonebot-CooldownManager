# 适用于Nonebot2的低配指令冷却器

> [!NOTE]
> 由于是本人第一次完全规范化（应该？）编写代码，如有不适欢迎修改和pr

## 关于

使用class方法进行编写，使用时需要先进行初始化

## 使用示例

本人使用的是```Satori Adapter```，其他适配器同理

```
from nonebot import on_command
from cooldown import CooldownManager
from nonebot.adapters.satori import MessageEvent

cooldown_manager = CooldownManager('cooldown.json', 300, 600) # 可触发指令时间段为300s，冷却时长600s

matcher = on_command()
@matcher.handle()
async def _(event: MessageEvent):
    # 在可触发指令时间段过后进入冷却
    in_cooldown, remaining_time = await cooldown_manager.check_and_update_cooldown(group_id)

    # 如果在触发指令后280s后且在进入冷却前触发指令，则重置冷却时间
    in_cooldown, remaining_time = await cooldown_manager.check_and_update_cooldown(group_id, 280) 
    
    if in_cooldown:
        minutes, seconds = divmod(remaining_time, 60)
        await matcher.send("指令在冷却哦\n剩余时间：{int(minutes)}分{int(seconds)}秒")
    else:
        await matcher.send("指令已执行！")
```