# CHUNITHMSP ottoNET

b30部分代码来自watagashi-uni/Unibot

demo : [aqua.monian.one](aqua.monian.one) (不定时开)

*本存储库中出现的图片、文本、视频等内容受株式会社SEGA版权保护。

项目数据库目前仅支持sqlite，请全局替换 `../rinsama-aqua/data/db.sqlite` (

## NET简介：

ottoNET是 适用于本地音游窝使用的 CHUNITHMSP独立NET服务，连接到Aqua数据库即可启动服务。

NET提供了快速登录等快捷功能，且没有完整的用户认证系统。因此不建议自行搭建后对外开放。

目前支持以下内容的查询：

- 个人信息
- 游玩记录
- b30
- 收藏品查看
- *企鹅换装

*企鹅换装功能会导出装扮的id，需要手动粘贴到数据库（鉴权没写好）

未来将会支持：

- *收藏品修改
- 歌曲详情
- 排行榜

*收藏品将通过扫描本地游戏文件建立数据库

## NET特色：

响应式布局，移动端也能用

提供快速登录功能，跳过繁琐验证

游戏记录中可查询乐曲rating、乐曲信息等内容

*一键获取b30图片，方便快捷

*b30部分代码来自watagashi-uni/Unibot

## TODO：

- 最新最热
- r10改为读表
- 独立数据库连接

## 开发者的话：

ottoNET是为 自己宿舍里的音游窝 开发的NET服务。

因为不想使用在线服却又想用NET，又不能硬看数据库，就变成自己从头写一个NET了。

本人并非计算机类专业，代码也写的很烂，prpr mottomotto。

在这里感谢：

- HoshimiRIN - 2.16的数据库支持
- わたがし - b30部分代码
- chatGPT - 我的外置大脑
- rin群群友 - 大家真的很热情

以上

24.03.22
