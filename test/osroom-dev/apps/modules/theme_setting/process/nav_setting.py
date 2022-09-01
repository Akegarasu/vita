#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2019/12/2 14:43
# @Author : Allen Woo
from bson import ObjectId
from flask import request, g
from flask_babel import gettext
from apps.app import mdbs, cache
from apps.core.flask.reqparse import arg_verify
from apps.utils.format.obj_format import json_to_pyseq, objid_to_str, str_to_num


@cache.cached(timeout=86400, key_base64=False, db_type="redis")
def get_global_theme_navs(theme_name, lang):
    langs = g.site_global["language"]["all_language"].keys()
    navs = mdbs["sys"].dbs["theme_nav_setting"].find(
        {
            "language": lang,
            "theme_name": theme_name
        },
        {"_id": 0}
    ).sort([("order", 1)])
    if navs.count(True):
        return list(navs)
    else:
        for la in langs:
            if la == lang:
                continue
            navs = mdbs["sys"].dbs["theme_nav_setting"].find(
                {
                    "language": la,
                    "theme_name": theme_name
                },
                {"_id": 0}
            ).sort([("order", 1)])
            if navs.count(True):
                return list(navs)
    return []


def get_navs():
    theme_name = request.argget.all("theme_name")
    lang = request.argget.all("language")
    s, r = arg_verify(
        [
         (gettext("theme name"), theme_name),
         (gettext("language"), lang)
         ],
        required=True
    )
    if not s:
        return r
    navs = mdbs["sys"].dbs["theme_nav_setting"].find(
        {"language": lang, "theme_name": theme_name}
    ).sort([("order", 1)])
    navs = objid_to_str(navs)
    data = {
        "navs": navs
    }
    return data


def nav_setting():
    """
    Update
    :RETURN:
    """

    cid = request.argget.all("id")
    theme_name = request.argget.all("theme_name")
    lang = request.argget.all("language")
    display_name = request.argget.all("display_name")
    order = str_to_num(request.argget.all("order", 99))
    json_data = json_to_pyseq(request.argget.all("json_data"))
    s, r = arg_verify(
        [(gettext("Display name"), display_name),
         (gettext("theme name"), theme_name),
         (gettext("language"), lang),
         (gettext("Json data"), json_data)
         ],
        required=True
    )
    if not s:
        return r

    if not isinstance(json_data, dict):
        data = {
            "msg": gettext('Value must be of type json'),
            "msg_type": "e",
            "custom_status": 400
        }
        return data

    if not cid:
        updata = {
            'theme_name': theme_name,
            'display_name': display_name,
            'language': lang,
            'json_data': json_data,
            "order": order
        }
        r = mdbs["sys"].dbs["theme_nav_setting"].insert_one(updata)
        if r.inserted_id:
            data = {
                "msg": gettext("Navigation added successfully"),
                "msg_type": "s",
                "custom_status": 200
            }
        else:
            data = {
                "msg": gettext("Failed to add navigation"),
                "msg_type": "w",
                "custom_status": 400
            }
    else:
        updata = {
            'theme_name': theme_name,
            'display_name': display_name,
            'language': lang,
            'json_data': json_data,
            "order": order
        }
        r = mdbs["sys"].dbs["theme_nav_setting"].update_one(
            {"_id": ObjectId(cid)},
            {"$set": updata}
        )
        if r.modified_count:
            data = {
                "msg": gettext("Updated successfully"),
                "msg_type": "s",
                "custom_status": 200
            }
        elif r.matched_count:
            data = {
                "msg": gettext("Unmodified"),
                "msg_type": "w",
                "custom_status": 200
            }
        else:
            data = {
                "msg": gettext("Update failed"),
                "msg_type": "w",
                "custom_status": 400
            }
    cache.delete_autokey(
        fun="get_global_theme_navs",
        theme_name=".*",
        lang=".*",
        db_type="redis",
        key_regex=True
    )
    return data


def del_navs():
    ids = json_to_pyseq(request.argget.all("ids"))
    s, r = arg_verify(
        [(gettext("ids"), ids)],
        required=True
    )
    if not s:
        return r
    del_ids = []
    for id in ids:
        del_ids.append(ObjectId(id))

    r = mdbs["sys"].dbs["theme_nav_setting"].delete_many({"_id": {"$in": del_ids}})
    if r.deleted_count:
        data = {
            "msg": gettext("Deleted successfully"),
            "msg_type": "s",
            "custom_status": 200
        }
    else:
        data = {
            "msg": gettext("Delete failed"),
            "msg_type": "s",
            "custom_status": 200
        }
    cache.delete_autokey(
        fun="get_global_theme_navs",
        theme_name=".*",
        lang=".*",
        db_type="redis",
        key_regex=True
    )
    return data
