#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from flask import request
from flask_babel import gettext
from flask_login import current_user
from apps.core.utils.get_config import get_config
from apps.utils.upload.file_up import file_up
from apps.utils.upload.get_filepath import get_file_url
from apps.app import mdbs


def file_upload(
        return_url_key="urls",
        return_state_key="state",
        return_success="success",
        return_error="error",
        save_temporary_url=False,
        file_type="image",
        return_key=False,
        prefix=""):

    try:
        return_success = int(return_success)
    except BaseException:
        pass
    try:
        return_error = int(return_error)
    except BaseException:
        pass
    if request.files:
        files = request.files.values()
        if files:

            r = file_up(files, prefix=prefix, file_name=None)
            if r:
                urls = []
                if save_temporary_url:
                    for key in r:
                        if key:
                            r1 = mdbs["web"].db.tempfile.update_one({"type": file_type,
                                                                 "user_id": current_user.str_id},
                                                                {"$addToSet": {"paths": key}},
                                                                upsert=True)
                            if not r1.modified_count:
                                mdbs["web"].db.tempfile.insert_one({"type": file_type,
                                                                "user_id": current_user.str_id,
                                                                "paths": [key]})
                            urls.append(get_file_url(key))
                else:
                    for key in r:
                        if key:
                            urls.append(get_file_url(key))
                if urls:
                    data = {return_url_key: urls,
                            return_state_key: return_success,
                            "msg": gettext("Uploaded successfully"),
                            "msg_type": "s", "custom_status": 201}
                    if return_key:
                        data["keys"] = r
                else:
                    data = {
                        return_state_key: return_error,
                        "msg": gettext("Upload failed"),
                        "msg_type": "e", "custom_status": 400
                    }

            else:
                data = {
                    return_state_key: return_error,
                    "msg": gettext("Get file error"),
                    "msg_type": "e", "custom_status": 400
                }
        else:
            data = {
                return_state_key: return_error,
                "msg": gettext("Get file error"),
                "msg_type": "e",
                "custom_status": 400}
    else:
        data = {
            return_state_key: return_error,
            "msg": gettext("No file submitted"),
            "msg_type": "e",
            "custom_status": 400}
    return data
