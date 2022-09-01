#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
__readme__ = '''
################################################################################
1.配置文件
a.除了OVERWRITE_DB外, 其他配置都可以在平台管理端页面修改
b.启动网站/重启网站的时候，系统会自动合并数据库中保存的配置,实现数据库使用的参数的Key和该文件一致.
c.如果你是开发人员,需要手动修改配置文件，请阅读下面说明

2.自动合并过程中:
a.对于本文件新增加的key会添加到数据库
b.本文文件没有的,而数据库有保存的key会在数据库删除
c.两边都存在的key, 则value使用数据库的

##如果你不想合并配置, 想用本地配置数据覆盖掉数据库中的配置数据,请修改变量OVERWRITE_DB

变量说明
*OVERWRITE_DB
启动系统时, 配置更新是否来自数据库, 以数据库中的value为主.
如果为True, 则完全以本文件数据上传到数据库中
如果为False, 按照上述[2.自动合并过程中],当次有效, 启动后会自动变为True

*CONFIG　
1.每个配置项中的__sort__作为在管理的显示的时候的排序使用, 如果不存在__sort__,表示该配置不可以在管理端配置
2.配置表,表中没有__restart__的项目将不会出现在管理端的设置中
###############################################################################
'''
# Danger: If True, the database configuration data will be overwritten
# 危险:如果为True, 则会把该文件配置覆盖掉数据库中保存的配置
SYS_CONFIG_VERSION = 2.2
OVERWRITE_DB = False
CONFIG = {
    "user_model": {
        "__restart__": "not_must",
        "EDITOR": {
            "sort": 99,
            "value": "rich_text",
            "type": "string",
            "info": "新用户默认编辑器类型rich_text或markdown"
        },
        "__info__": "用户Model",
        "__sort__": 99
    },
    "weblogger": {
        "SING_IN_LOG_KEEP_NUM": {
            "sort": 99,
            "value": 30,
            "type": "int",
            "info": "登录日志保留个数"
        },
        "USER_OP_LOG_KEEP_NUM": {
            "sort": 99,
            "value": 30,
            "type": "int",
            "info": "用户操作日志保留个数"
        },
        "__restart__": "not_must",
        "__info__": "操作日志设置",
        "__sort__": 99
    },
    "comment": {
        "TRAVELER_COMMENT": {
            "sort": 99,
            "value": False,
            "type": "bool",
            "info": "游客评论开关,是否打开?"
        },
        "NUM_PAGE": {
            "sort": 99,
            "value": 10,
            "type": "int",
            "info": "每个页面获取几条评论, 如果请求获取评论时指定了指定了per参数, 则此配置无效(此配置也对管理端无效)"
        },
        "__restart__": "not_must",
        "__info__": "评论内容设置",
        "INTERVAL": {
            "sort": 99,
            "value": 30,
            "type": "int",
            "info": "控制评论频繁度时间(s)"
        },
        "__sort__": 3,
        "MAX_LEN": {
            "sort": 99,
            "value": 300,
            "type": "int",
            "info": "发布评论最多几个字符"
        },
        "NUM_OF_INTERVAL": {
            "sort": 99,
            "value": 3,
            "type": "int",
            "info": "控制评论频繁度时间内最多评论几次"
        },
        "NUM_PAGE_MAX": {
            "sort": 99,
            "value": 30,
            "type": "int",
            "info": "每个页面最多获取几条评论(此配置对管理端无效)"
        },
        "OPEN_COMMENT": {
            "sort": 99,
            "value": False,
            "type": "bool",
            "info": "评论开关,是否打开评论功能?"
        }
    },
    "category": {
        "CATEGORY_TYPE": {
            "sort": 99,
            "value": {
                "其他": "other",
                "视频库": "video",
                "文集": "post",
                "图库": "image",
                "文本内容": "text",
                "音频库": "audio"
            },
            "type": "dict",
            "info": "分类的品种只能有这几种"
        },
        "__restart__": "not_must",
        "__info__": "Web参数设置",
        "CATEGORY_MAX_LEN": {
            "sort": 99,
            "value": 15,
            "type": "int",
            "info": "分类名称类型名最多几个字符"
        },
        "__sort__": 7
    },
    "post": {
        "GET_POST_CACHE_TIME_OUT": {
            "sort": 99,
            "value": 60,
            "type": "int",
            "info": "获取多个post数据时, 缓存超时时间(s), 为0表示不缓存数据.<br><span style='color:red;'>只对获取已公开发布的, 并且不是当前用户发布的post有效</span>"
        },
        "TAG_MAX_LEN": {
            "sort": 99,
            "value": 10,
            "type": "int",
            "info": "POST标签最多几个字"
        },
        "__restart__": "not_must",
        "__info__": "文章内容设置",
        "__sort__": 2,
        "MAX_LEN": {
            "sort": 99,
            "value": 5000,
            "type": "int",
            "info": "发布文章最多几个字符"
        },
        "TITLE_MAX_LEN": {
            "sort": 99,
            "value": 50,
            "type": "int",
            "info": "文章Title最大长度"
        },
        "BRIEF_LEN": {
            "sort": 99,
            "value": 80,
            "type": "int",
            "info": "获取文章简要的字数"
        },
        "TAG_MAX_NUM": {
            "sort": 99,
            "value": 5,
            "type": "int",
            "info": "POST标签最大个数"
        },
        "NUM_PAGE_MAX": {
            "sort": 99,
            "value": 30,
            "type": "int",
            "info": "每个页面最多获取几篇文章(此配置对管理端无效)"
        },
        "NUM_PAGE": {
            "sort": 99,
            "value": 10,
            "type": "int",
            "info": "每个页面获取几篇文章, 如果请求获取文章时指定了指定了per参数, 则此配置无效(此配置也对管理端无效)"
        }
    },
    "content_inspection": {
        "AUDIO_OPEN": {
            "sort": 99,
            "value": False,
            "type": "bool",
            "info": "开启音频检测.需要hook_name为content_inspection_audio的音频检测插件"
        },
        "VEDIO_OPEN": {
            "sort": 99,
            "value": False,
            "type": "bool",
            "info": "开启视频检测.需要hook_name为content_inspection_vedio的视频检测插件"
        },
        "__restart__": "not_must",
        "__info__": "内容检查配置(需要安装相关插件该配置才生效).<br>检测开关:<br>1.如果开启, 并安装有相关的自动检查插件, 则会给发布的内容给出违规评分.如果未安装自动审核插件,则系统会给予评分100分(属涉嫌违规,网站工作人员账户除外).<br>2.如果关闭审核，则系统会给评分0分(不违规)",
        "__sort__": 5,
        "IMAGE_OPEN": {
            "sort": 99,
            "value": False,
            "type": "bool",
            "info": "开启图片检测.需要hook_name为content_inspection_image的图片检测插件"
        },
        "TEXT_OPEN": {
            "sort": 99,
            "value": True,
            "type": "bool",
            "info": "开启text检测.需要hook_name为content_inspection_text的文本检测插件"
        },
        "ALLEGED_ILLEGAL_SCORE": {
            "sort": 99,
            "value": 99,
            "type": "float",
            "info": "内容检测分数高于多少分时属于涉嫌违规(0-100分,对于需要检查的内容有效)"
        }
    },
    "security": {
        "SWITCH": {
            "sort": 1,
            "value": True,
            "type": "bool",
            "info": "安全审核开关，建议打开，防止部分内容注入攻击"
        },
        "LINK_WHITELIST": {
            "sort": 99,
            "value": [],
            "type": "list",
            "info": "Link白名单: 当SWITCH开启时生效，post(文章)和comment(评论)等提交的内容都会对除白名单的Link/URL外Link做修改"
        },
        "__restart__": "not_must",
        "__info__": "网站安全设置",
        "__sort__": 99
    },
    "content_audit": {
        "AUDIT_PROJECT_KEY": {
            "sort": 99,
            "value": {
                "class_name": "审核一些短的分类名称, 如category, tag",
                "username": "审核用户名(username)",
                "content_security": "审核post(文章)和comment(评论)等长内容的安全性"
            },
            "type": "dict",
            "info": "审核项目的Key(键),审核时会使用一个Key来获取审核规则,正则去匹配用户输入的内容"
        },
        "__restart__": "not_must",
        "__info__": "名称,内容验证, 如用户名,分类名称",
        "__sort__": 8
    },

    "key": {
        "SECURITY_PASSWORD_SALT": {
            "sort": 99,
            "value": "ceavewrvwtrhdyjydj",
            "type": "string",
            "info": "安全密码码盐值"
        },
        "__restart__": "must",
        "SECRET_KEY": {
            "sort": 99,
            "value": "ceavewrvwtrhdyjydj",
            "type": "string",
            "info": "安全验证码"
        },
        "__info__": "安全Key（建议技术管理人员使用）",
        "__sort__": 99
    },
    "email": {
        "MAIL_DEFAULT_SENDER": {
            "sort": 99,
            "value": [
                "OSR DEMO",
                "system@osroom.com"
            ],
            "type": "list",
            "info": "默认发送者邮箱　(显示名称, 邮箱地址)顺序不能调换"
        },
        "MAIL_SERVER": {
            "sort": 99,
            "value": "smtp.mxhichina.com",
            "type": "string",
            "info": "邮箱服务器smtp"
        },
        "MAIL_ASCII_ATTACHMENTS": {
            "sort": 99,
            "value": True,
            "type": "bool",
            "info": "MAIL ASCII ATTACHMENTS"
        },
        "__sort__": 10,
        "MAIL_PASSWORD": {
            "sort": 99,
            "value": "<Your password>",
            "type": "password",
            "info": "邮箱密码, 是用于发送邮件的密码"
        },
        "APP_NAME": {
            "sort": 99,
            "value": "OSR DEMO",
            "type": "string",
            "info": "在邮件中显示的APP(WEB)名称(1.不填写则不显示.2.如果主题邮件发送html模板不支持，也不显示)"
        },
        "MAIL_PORT": {
            "sort": 99,
            "value": 465,
            "type": "int",
            "info": "邮箱服务器端口"
        },
        "__restart__": "must",
        "__info__": "邮件发送参数设置（建议技术管理人员使用）",
        "MAIL_FOOTER": {
            "sort": 99,
            "value": "OSROOM开源网站系统",
            "type": "string",
            "info": "发送邮件的页尾"
        },
        "MAIL_USERNAME": {
            "sort": 99,
            "value": "system@osroom.com",
            "type": "string",
            "info": "邮箱用户名"
        },
        "MAIL_SUBJECT_SUFFIX": {
            "sort": 99,
            "value": "OSROOM",
            "type": "string",
            "info": "发送邮件的标题后缀"
        },
        "APP_LOG_URL": {
            "sort": 99,
            "value": "https://avatars1.githubusercontent.com/u/14039952?s=460&v=4",
            "type": "string",
            "info": "在邮件中显示的LOGO图片URL(1.不填写则不显示.2.如果主题邮件发送html模板不支持，也不显示)"
        },
        "MAIL_USE_TLS": {
            "sort": 99,
            "value": False,
            "type": "bool",
            "info": "是否使用TLS"
        },
        "MAIL_USE_SSL": {
            "sort": 99,
            "value": True,
            "type": "bool",
            "info": "是否使用SSL"
        }
    },
    "cache": {
        "CACHE_MONGODB_COLLECT": {
            "sort": 99,
            "value": "osr_cache",
            "type": "string",
            "info": "保存cache的collection,当CACHE_TYPE为mongodb时有效"
        },
        "USE_CACHE": {
            "sort": 99,
            "value": True,
            "type": "bool",
            "info": "是否使用缓存功能,建议开启"
        },
        "CACHE_DEFAULT_TIMEOUT": {
            "sort": 99,
            "value": 600,
            "type": "int",
            "info": "(s秒)默认缓存时间,当单个缓存没有设定缓存时间时会使用该时间"
        },
        "__sort__": 99,
        "CACHE_TYPE": {
            "sort": 99,
            "value": "redis",
            "type": "string",
            "info": "缓存使用的类型,可选择redis,mongodb"
        },
        "__restart__": "must",
        "CACHE_KEY_PREFIX": {
            "sort": 99,
            "value": "osr_cache",
            "type": "string",
            "info": "所有键(key)之前添加的前缀,这使得它可以为不同的应用程序使用相同的memcached(内存)服务器."
        },
        "__info__": "Web缓存参数设置（建议技术管理人员使用）"
    },
    "babel": {
        "BABEL_DEFAULT_LOCALE": {
            "sort": 99,
            "value": "zh_CN",
            "type": "string",
            "info": "默认语言:可以是zh_CN, en_US等()"
        },
        "__restart__": "must",
        "LANGUAGES": {
            "sort": 99,
            "value": {
                "en_US": {
                    "name": "English",
                    "alias": "En"
                },
                "zh_CN": {
                    "name": "中文",
                    "alias": "中文"
                }
            },
            "type": "dict",
            "info": "管理端支持的语言"
        },
        "__info__": "多语言设置",
        "__sort__": 9
    },
    "py_venv": {
        "VENV_PATH": {
            "sort": 99,
            "value": "/home/work/project/venv3",
            "type": "string",
            "info": "python虚拟环境路径"
        }
    },
    "theme_global_conf": {
        "FREE": {
            "sort": 99,
            "value": {"post_cover": {"url": "<url>", "name": "文章默认图片封面"}},
            "type": "dict",
            "info": "提供给主题的自由设置项, 可以在此自由添加各种设置(需要主题支持)格式:标准Json"
        },
        "__restart__": "not_must",
        "TOP_NAV": {
            "sort": 99,
            "value": {
                "关于": {
                    "next_lev": [
                        {
                            "link": "/about-us",
                            "nav": "关于我们"
                        },
                        {
                            "link": "/contact",
                            "nav": "联系我们"
                        }
                    ],
                    "nav": "关于",
                    "link": ""
                },
                "1": {
                    "next_lev": None,
                    "nav": "首页",
                    "link": "/"
                },
                "2": {
                    "next_lev": None,
                    "nav": "图库",
                    "link": "/photo"
                }
            },
            "type": "dict",
            "info": "已废弃，待删除, 请勿使用"
        },
        "__info__": "主题的一些全局配置(只对主题有效, 并需要主题支持)",
        "__sort__": 99
    },
    "rest_auth_token": {
        "REST_ACCESS_TOKEN_LIFETIME": {
            "sort": 99,
            "value": 172800,
            "type": "int",
            "info": "给客户端发补的访问Token AccessToken的有效期"
        },
        "__sort__": 99,
        "__restart__": "not_must",
        "MAX_SAME_TIME_LOGIN": {
            "sort": 99,
            "value": 3,
            "type": "int",
            "info": "最多能同时登录几个使用JWT验证的客户端,超过此数目则会把旧的登录注销"
        },
        "LOGIN_LIFETIME": {
            "sort": 99,
            "value": 2592000,
            "type": "int",
            "info": "jwt 登录BearerToken有效期(s)"
        },
        "__info__": "Web参数设置"
    },
    "seo": {
        "__restart__": "not_must",
        "SPIDER_RECOGNITION_ENABLE": {
            "sort": 99,
            "value": True,
            "type": "bool",
            "info": "是否开启spider识别"
        },
        "SUPPORTED_SPIDERS": {
            "sort": 99,
            "value": ["Googlebot", "Baiduspider", "bingbot", "Sogou web spider", "Sosospider"],
            "type": "list",
            "info": "填入需要支持的蜘蛛的名称, User-Agent中特有的如: Googlebot, Baiduspider. 将会对它们返回静态文章页面"
        },
        "THEME_PAGE_FOR_STATIC_PAGE": {
            "sort": 99,
            "value": {
                "post_page": "/post?id=<id>"
            },
            "type": "dict",
            "info": "OSROOM自带的静态文章页面对应的你使用的主题文章页面规则. id位标记为<id>, 目前只支持文章页"
        },
        "DEFAULT_DESCRIPTION": {
            "sort": 99,
            "value": "开源Web系统, 可以作为企业网站, 个人博客网站, 微信小程序Web服务端",
            "type": "string",
            "info": "网站的页面默认简单描述"
        },
        "DEFAULT_KEYWORDS": {
            "sort": 99,
            "value": "开源, 企业网站, 博客网站, 微信小程序, Web服务端",
            "type": "string",
            "info": "网站的页面默认关键词"
        },
        "__info__": "针对网页客户端的简单的SEO配置<br>此模块所有的KEY值, 都可以直接请求全局Api(<br><span style='color:red;'>/api/global</span>)获取.<br>也可以直接在主题中使用Jinjia2模板引擎获取(<br><span style='color:red;'>g.site_global.site_config.XXXX</span>)",
        "__sort__": 4
    },
    "account": {
        "USERNAME_MAX_LEN": {
            "sort": 99,
            "value": 20,
            "type": "int",
            "info": "用户名最大长度"
        },
        "__restart__": "not_must",
        "USER_AVATAR_MAX_SIZE": {
            "sort": 99,
            "value": 10.0,
            "type": "float",
            "info": "用户头像不能上传超过此值大小(单位Mb)的图片作头像"
        },
        "__sort__": 6,
        "DEFAULT_AVATAR": {
            "sort": 99,
            "value": "/static/sys_imgs/avatar_default.png",
            "type": "string",
            "info": "新注册用户默认头像的URL"
        },
        "USER_AVATAR_SIZE": {
            "sort": 99,
            "value": [
                "360",
                "360"
            ],
            "type": "list",
            "info": "用户头像保存大小[<width>, <height>]像素"
        },
        "__info__": "账户设置"
    },
    "site_config": {
        "MB_LOGO_DISPLAY": {
            "sort": 4,
            "value": "name",
            "type": "string",
            "info": "移动端用App name 还是Logo image 作为APP(Web)的Logo显示, 为空则App name优先<br>可填logo或name(需要主题支持)"
        },
        "DOES_NOT_EXIST_URL": {
            "sort": 11,
            "value": "/static/sys_imgs/does_not_exist.png",
            "type": "string",
            "info": "当一个文件或图片不存在的时候, 返回此Image URL"
        },
        "__sort__": 1,
        "TITLE_SUFFIX": {
            "sort": 8,
            "value": "OSROOM开源Web DEMO",
            "type": "string",
            "info": "APP(Web)Title后缀"
        },
        "SITE_URL": {
            "sort": 11,
            "value": "http://www.osroom.com",
            "type": "string",
            "info": "Web站点URL(如果没有填写, 则使用默认的当前域名首页地址)"
        },
        "FAVICON": {
            "sort": 10,
            "value": "/static/sys_imgs/osroom-logo.ico",
            "type": "string",
            "info": "APP(Web)favicon图标的URL"
        },
        "FRIEND_LINK": {
            "sort": 11,
            "value": {
                "文章地图": {
                    "level": 2,
                    "url": "/st-html/posts/1",
                    "icon_url": "",
                    "aliases": "文章地图"

                },
                "码云": {
                    "level": 1,
                    "url": "https://gitee.com/osroom/osroom",
                    "icon_url": "",
                    "aliases": "码云"
                },
                "Github": {
                    "level": 1,
                    "url": "https://github.com/osroom/osroom",
                    "icon_url": "",
                    "aliases": "Github"
                }
            },
            "type": "dict",
            "info": "友情链接:值(Value)格式为{'url':'友情链接', 'logo_url':'logo链接'}"
        },
        "APP_NAME": {
            "sort": 1,
            "value": "OSROOM",
            "type": "string",
            "info": "APP(站点)名称,将作为全局变量使用在平台上"
        },
        "PC_LOGO_DISPLAY": {
            "sort": 3,
            "value": "name",
            "type": "string",
            "info": "PC端用App name 还是Logo image 作为APP(Web)的Logo显示, 为空则显示Logo和App name<br>可填logo或name(需要主题支持)"
        },
        "__restart__": "not_must",
        "FOOTER_CODE": {
            "sort": 13,
            "value": "",
            "type": "string",
            "info": "用于放入html中<br><span style='color:red;'>body标签</span>内的js/css/html代码(如Google分析代码/百度统计代码)"
        },
        "STATIC_FILE_VERSION": {
            "sort": 12,
            "value": 20190531022907,
            "type": "int",
            "info": "静态文件版本(当修改了CSS,JS等静态文件的时候，修改此版本号)"
        },
        "LOGO_IMG_URL": {
            "sort": 2,
            "value": "/static/sys_imgs/logo.png",
            "type": "string",
            "info": "APP(Web)Logo的URL"
        },
        "TITLE_SUFFIX_ADM": {
            "sort": 9,
            "value": "OSROOM管理端",
            "type": "string",
            "info": "APP(Web)管理端Title后缀"
        },
        "BACKGROUND_IMG_URL": {
            "sort": 5,
            "value": "/static/sys_imgs/background.jpg",
            "type": "string",
            "info": "网页背景图片(需要主题支持)"
        },
        "HEAD_CODE": {
            "sort": 13,
            "value": "",
            "type": "string",
            "info": "用于放入html中<br><span style='color:red;'>head标签</span>内的js/css/html代码(如Google分析代码/百度统计代码)"
        },
        "TITLE_PREFIX": {
            "sort": 6,
            "value": "",
            "type": "string",
            "info": "APP(Web)Title前缀"
        },
        "__info__": "基础设置: APP(Web)全局数据设置<br>此模块所有的KEY值, 都可以直接请求全局Api(/api/global)获取.也可以直接在主题中使用Jinjia2模板引擎获取(g.site_global.site_config.XXXX)",
        "TITLE_PREFIX_ADM": {
            "sort": 7,
            "value": "",
            "type": "string",
            "info": "APP(Web)管理端Title前缀"
        },
        "FOOTER_CONTENT": {
            "sort": 11,
            "value": """ <div>
                  {{_('欢迎使用')}}
                  <a style="color:#f1c27e" href="http://www.osroom.com" target="_blank">
                  <img src="/static/sys_imgs/logo.png?h=40&v={{g.site_global.site_config.STATIC_FILE_VERSION}}" height="17px" width="auto" alt="OSROOM">
                      OSROOM
                  </a>. {{_('版本')}} {{g.site_global.site_config.sys_version}}
            
                      Licensed under <a class="osr-color-secondary" href="http://opensource.org/licenses/BSD-2-Clause" target="_blank">
                      BSD license
                    </a>.
                    <a href="https://github.com/osroom/osroom" target="_blank" >
                      <i class="am-icon-github"></i> GitHub.
                    </a>
            </div> """,
            "type": "string",
            "info": "页面底部展示代码"
        },
    },
    "system": {
        "MAX_CONTENT_LENGTH": {
            "sort": 1,
            "value": 50.0,
            "type": "float",
            "info": "拒绝内容长度大于此值的请求进入，并返回一个 413 状态码(单位:Mb)"
        },
        "__restart__": "must",
        "__sort__": 99,
        "TEMPLATES_AUTO_RELOAD": {
            "sort": 3,
            "value": True,
            "type": "bool",
            "info": "是否自动加载页面(html)模板.开启后,每次html页面修改都无需重启Web"
        },
        "KEY_HIDING": {
            "sort": 2,
            "value": True,
            "type": "bool",
            "info": "开启后,管理端通过/api/admin/xxx获取到的数据中，密钥类型的值，则会以随机字符代替.<br><span style='color:red;'>如某个插件配置中有密码, 不想让它暴露在浏览器, 则可开启.</span>"
        },
        "__info__": "其他web系统参数设置（建议技术管理人员使用）"
    },
    "upload": {
        "SAVE_DIR": {
            "sort": 99,
            "value": "media",
            "type": "string",
            "info": "上传:保存目录,如何存在'/'则会自动切分创建子目录"
        },
        "__restart__": "not_must",
        "__info__": "文件上传配置（建议技术管理人员使用）",
        "UP_ALLOWED_EXTENSIONS": {
            "sort": 99,
            "value": [
                "xls",
                "xlxs",
                "excel",
                "txt",
                "pdf",
                "png",
                "jpg",
                "jpeg",
                "gif",
                "ico",
                "mp4",
                "rmvb",
                "avi",
                "mkv",
                "mov",
                "mp3",
                "wav",
                "wma",
                "ogg",
                "zip",
                "gzip",
                "tar"
            ],
            "type": "list",
            "info": "上传:允许上传的文件后缀(全部小写),每个用英文的','隔开"
        },
        "__sort__": 99
    },
    "theme": {
        "VERSION": {
            "sort": 99,
            "value": "v0.1",
            "type": "string",
            "info": "当前主题版本"
        },
        "__restart__": "not_must",
        "__info__": "主题配置",
        "CURRENT_THEME_NAME": {
            "sort": 99,
            "value": "osr-theme-w",
            "type": "string",
            "info": "当前主题名称,需与主题主目录名称相同"
        }
    },
    "verify_code": {
        "MIN_IMG_CODE_INTERFERENCE": {
            "sort": 99,
            "value": 10,
            "type": "int",
            "info": "图片验证码干扰程度的最小值,最小值小于10时无效"
        },
        "__restart__": "not_must",
        "MAX_NUM_SEND_SAMEIP_PERMIN": {
            "sort": 99,
            "value": 15,
            "type": "int",
            "info": "同一IP地址,同一用户(未登录的同属一匿名用户), 允许每分钟调用API发送验证码的最大次数"
        },
        "EXPIRATION": {
            "sort": 99,
            "value": 600,
            "type": "int",
            "info": "验证码过期时间(s)"
        },
        "MAX_IMG_CODE_INTERFERENCE": {
            "sort": 99,
            "value": 40,
            "type": "int",
            "info": "图片验证码干扰程度的最大值"
        },
        "__sort__": 11,
        "SEND_CODE_TYPE": {
            "sort": 99,
            "value": {
                "int": 6,
                "string": 0
            },
            "type": "dict",
            "info": "发送的验证码字符类型，与字符个数"
        },
        "MAX_NUM_SEND_SAMEIP_PERMIN_NO_IMGCODE": {
            "sort": 99,
            "value": 1,
            "type": "int",
            "info": "同一IP地址,同一用户(未登录的同属同一匿名用户),允许每分钟在不验证[图片验证码]的时候,调用API发送验证码最大次数.<br>超过次数后API会生成[图片验证码]并返回图片url对象(也可以自己调用获取图片验证码API获取).<br>如果你的客户端(包括主题)不支持显示图片验证码,请设置此配置为99999999"
        },
        "__info__": "验证码(建议技术管理员配置)",
        "IMG_CODE_DIR": {
            "sort": 99,
            "value": "verify_code",
            "type": "string",
            "info": "图片验证码保存目录"
        }
    },
    "login_manager": {
        "LOGIN_IN_TO": {
            "sort": 99,
            "value": "/",
            "type": "string",
            "info": "登录成功后,api会响应数据会带上需要跳转到路由to_url"
        },
        "__restart__": "not_must",
        "__info__": "在线管理（建议技术管理人员使用）",
        "LOGIN_OUT_TO": {
            "sort": 99,
            "value": "/",
            "type": "string",
            "info": "退出登录后,api会响应数据会带上需要跳转到路由to_url"
        },
        "__sort__": 99,
        "OPEN_REGISTER": {
            "sort": 99,
            "value": True,
            "type": "bool",
            "info": "开放注册"
        },
        "LOGIN_VIEW": {
            "sort": 99,
            "value": "/sign-in",
            "type": "string",
            "info": "需要登录的页面,未登录时,api会响应401,并带上需要跳转到路由to_url"
        },
        "PW_WRONG_NUM_IMG_CODE": {
            "sort": 99,
            "value": 5,
            "type": "int",
            "info": "同一用户登录密码错误几次后响应图片验证码, 并且需要验证"
        }
    },
    "session": {
        "SESSION_KEY_PREFIX": {
            "sort": 99,
            "value": "osroom",
            "type": "string",
            "info": "添加一个前缀,之前所有的会话密钥。这使得它可以为不同的应用程序使用相同的后端存储服务器"
        },
        "__restart__": "must",
        "PERMANENT_SESSION_LIFETIME": {
            "sort": 99,
            "value": 2592000,
            "type": "int",
            "info": "永久会话的有效期."
        },
        "__sort__": 99,
        "SESSION_PERMANENT": {
            "sort": 99,
            "value": True,
            "type": "bool",
            "info": "是否使用永久会话"
        },
        "SESSION_TYPE": {
            "sort": 99,
            "value": "redis",
            "type": "string",
            "info": "保存Session会话的类型,可选redis, mongodb. 推荐redis"
        },
        "SESSION_MONGODB_COLLECT": {
            "sort": 99,
            "value": "osr_session",
            "type": "string",
            "info": "Mongodb保存session的collection,当SESSION_TYPE为mongodb时有效"
        },
        "__info__": "Session参数设置（建议技术管理人员使用）"
    }
}