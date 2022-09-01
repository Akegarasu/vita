
<div align=center><img width="auto" height="50" src="https://raw.githubusercontent.com/osroom/osroom/dev/apps/static/sys_imgs/logo.png" alt="osroom"/></div>


> dev(开放更新中,可在Tag中可以选择以往的其他版本)

- 当前更新比较多，请及时更新新版本

- 低版本更新到v2.2后，如果出现ROOT用户权限问题，[注销登录]后再次登录

** 注意：更新到v2.2的童鞋请先看[这篇文章](https://demo.osroom.com/post?id=5e1c27773f677efbf48e40ab) **

|   Version  |   Status  |  Other   |
| --- | --- | --- |
|   [dev](https://github.com/osroom/osroom)    |  开发...   |    v1.x.x更新到dev版本时需要重新配置数据库文件
|   [v2.2](https://github.com/osroom/osroom/tree/v2.2)    |     | v1.x.x更新到v2.2版本时需要重新配置数据库文件
|   [v2.1](https://github.com/osroom/osroom/tree/v2.1)    |     | v1.x.x更新到v2.1版本时需要重新配置数据库文件
|   [v2.0](https://github.com/osroom/osroom/tree/v2.0)    |     | v1.x.x更新到v2.0版本时需要重新配置数据库文件
|   [v2.0 Beta](https://github.com/osroom/osroom/tree/v2.0beta)    |     | v1.x.x更新到v2.0beta版本时需要重新配置数据库文件
|   [v1.1.1](https://github.com/osroom/osroom/tree/v1.1.1)    |  不建议使用 |  v1.x.x更新到dev版本时需要重新配置数据库文件   |


OSROOM是使用Python3(>=3.4) 语言,基于Flask微型框架 + Mongodb(>=3.4)+ Redis开发的一个Web系统（CMF , Rest Api）.

可用于搭建（开发）个人网站,  企业官网, 也可以作为其他平台的服务端, 比如小程序客户端可以调用OSROOM Api请求操作数据.
功能支持方便,可以自己开发更多的插件或者扩展模块，让功能更全面!
目前只在Ubuntu 14.04, 16.04，18.04和Centos 6测试过，其余Linux发行版还未测试。

### 文档

使用前请更新python lib

```shell
pip install -U -r requirements.txt
```

长期可访问文档地址: https://osroom.github.io/osroom-doc

其他相关问题解决方案: [OSROOM问题](https://demo.osroom.com/corpus?id=5c8271171d41c812d7169e00)

### Demo

Demo网站使用默认主题(osr-style)，安装了文件存储插件(用于作为图床)，文本内容检查插件，IP识别地址插件

https://demo.osroom.com

目前Demo安装的属于测试版本，如有BUG请提交

官网: http://osroom.com (该站可能已下线)


### 功能与支持

> 功能

- 可做Web 服务端Api, Restful api，简单修改即可做微信小程序的Api.

- 管理端和默认主题osr-style都支持富文本和MarkDown编辑器.

- 内容发布:

  发布-每个用户可独立发布文章与评论.

  管理-管理人员可在管理端管理全部内容，可通过插件实现自动审核或人工审核用户发布的内容.

- 多媒体功能:管理者可再管理端上传图片/音频/视频等供网站使用.

- 权限控制功能:

  Api/page-可以设置每一个Api和Page需要的请求权限.

  Role-用户角色, 可赋于每个Role拥有的权限.

  User-为用户指定角色,即可获取相关权限.

- 网站设置: 大量设置可以在管理端直接修改，无需改动代码.

- 部分功能支持插件开发

- 支持多语言翻译

- 还有用户管理, 验证码发送, 图片验证码, 邮件管理, 消息, 主题内容管理, 等...

更多功能请访问demo网站

> 支持开发

- 插件开发，官方插件Github地址: https://github.com/osroom-plugins
- 主题开发，官方主题Github地址: https://github.com/osroom
- 扩展 

### 为何开发？

那就是基于自己对Web编程的兴趣与学习更多的编程知识.

### Admin首页

![Admin主页](http://osshare.oss-cn-shenzhen.aliyuncs.com/Introduction/admin.png)

详情请访问demo网站

### License
[BSD2](http://opensource.org/licenses/BSD-2-Clause)
Copyright (c) 2017-present, Allen Woo
