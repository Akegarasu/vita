#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from importlib import import_module
from flask import Blueprint
from apps.configs.sys_config import ADMIN_TEMPLATE_FOLDER, THEME_TEMPLATE_FOLDER, API_URL_PREFIX, ADMIN_URL_PREFIX, \
    STATIC_PATH, STATIC_URL_PREFIX, OPEN_API_URL_PREFIX, STATIC_HTML_TEMPLATE_FOLDER, STATIC_HTML_PAGE_PREFIX, \
    ADMIN_STATIC_URL_PREFIX, ADMIN_STATIC_FOLDER
from apps.core.plugins_blueprint import plugins_routing_moudel

"""
蓝本:配置路由,url
"""
# api
api = Blueprint(
    'api',
    __name__,
    url_prefix=API_URL_PREFIX
)
open_api = Blueprint(
    'open_api',
    __name__,
    url_prefix=OPEN_API_URL_PREFIX
)

# html
admin_view = Blueprint(
    'admin_view',
    __name__,
    url_prefix=ADMIN_URL_PREFIX,
    template_folder=ADMIN_TEMPLATE_FOLDER
)

theme_view = Blueprint(
    'theme_view',
    __name__,
    template_folder=THEME_TEMPLATE_FOLDER
)

static_html_view = Blueprint(
    'static_html_view',
    __name__,
    url_prefix=STATIC_HTML_PAGE_PREFIX,
    template_folder=STATIC_HTML_TEMPLATE_FOLDER)

# static
static = Blueprint(
    'static', __name__,
    url_prefix=STATIC_URL_PREFIX,
    template_folder=STATIC_PATH
)

admin_static_file = Blueprint(
    'static_file', __name__,
    url_prefix=ADMIN_STATIC_URL_PREFIX,
    template_folder=ADMIN_STATIC_FOLDER
)

routing_moudel = [
    {"from": "apps.routing", "import": ["static_route", "admin_views", "theme_views", "static_page_route"]},
    {"from": "apps.modules.permission.apis", "import": ["url_permission", "permission"]},
    {"from": "apps.modules.user.apis", "import": ["online", "role",
                                                  "inspection_query", "adm_user",
                                                  "email", "profile",
                                                  "password", "avatar_upload"]},
    {"from": "apps.modules.category.apis", "import": ["category", "adm_category", "theme_category"]},
    {"from": "apps.modules.post.apis", "import": ["post", "user_post", "adm_post"]},
    {"from": "apps.modules.comments.apis", "import": ["comment", "amd_comment"]},
    {"from": "apps.modules.verification_code.apis", "import": ["code"]},
    {"from": "apps.modules.setting.apis", "import": ["settings", "get_file_log",
                                                     "host_setting", "session_set"]},
    {"from": "apps.modules.report.apis", "import": ["post_access", "comment_access",
                                                    "basic_access"]},
    {"from": "apps.modules.upload.apis", "import": ["upload_file"]},

    {"from": "apps.modules.audit.apis", "import": ["Python-rules"]},
    {"from": "apps.modules.theme_setting.apis", "import": ["static_file", "page", "themes", "display_setting"]},
    {"from": "apps.modules.media.apis", "import": ["adm_media"]},
    {"from": "apps.modules.global_data.apis", "import": ["global_data"]},
    {"from": "apps.modules.message.apis", "import": ["user_message", "adm_message", "send_msg"]},
    {"from": "apps.modules.message.apis", "import": ["sys_message"]},
    {"from": "apps.modules.token.apis", "import": ["rest_token"]},
    {"from": "apps.modules.plug_in_manager.apis", "import": ["manager", "setting"]},
    {"from": "apps.modules.follow.apis", "import": ["user_follow"]},
    {"from": "apps.modules.content_inform.apis", "import": ["inform"]},
    {"from": "apps.modules.search.apis", "import": ["search"]}
]

for rout_m in routing_moudel:
    for im in rout_m["import"]:
        moudel = "{}.{}".format(rout_m["from"], im)
        import_module(moudel)

for rout_m in plugins_routing_moudel:
    for im in rout_m["import"]:
        moudel = "{}.{}".format(rout_m["from"], im)
        try:
            import_module(moudel)
        except BaseException:
            pass
