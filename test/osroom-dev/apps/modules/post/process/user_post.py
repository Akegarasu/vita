#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
import json
import markdown
from bson import ObjectId
from flask import request
from flask_babel import gettext
from flask_login import current_user
import time
from apps.core.flask.reqparse import arg_verify
from apps.modules.message.process.user_message import insert_user_msg
from apps.modules.upload.process.tempfile import clean_tempfile
from apps.utils.content_evaluation.content import content_inspection_text
from apps.utils.format.obj_format import json_to_pyseq
from apps.utils.text_parsing.text_parsing import richtext_extract_img
from apps.app import mdbs
from apps.core.utils.get_config import get_config
from apps.utils.validation.str_format import content_attack_defense


def post_issue():

    tid = request.argget.all('id')
    title = request.argget.all('title', "").strip()
    content = request.argget.all('content', "")
    content_text = request.argget.all('content_text', "")
    editor = request.argget.all('editor')
    category = request.argget.all('category')
    tags = json_to_pyseq(request.argget.all('tags', []))
    issue_way = request.argget.all('issue_way', 'issue')
    cover_url = request.argget.all('cover_url')

    # 标签处理验证
    tag_max_num = get_config("post", "TAG_MAX_NUM")
    if len(tags) > tag_max_num:
        data = {"msg": gettext("Up to {} tags are used").format(tag_max_num),
                "msg_type": "w", "custom_status": 403}
        return data

    tags = list(set(tags))
    temp_tags = ""
    for tag in tags:
        s, r = arg_verify(
            reqargs=[
                (gettext("tag"), tag)], max_len=get_config(
                "post", "TAG_MAX_LEN"))
        if not s:
            return r
        temp_tags = "{} {}".format(tag, temp_tags)

    # 分类验证
    try:
        ObjectId(category)
    except BaseException:
        category = None
    # Title 处理
    s, r = arg_verify(
        reqargs=[
            (gettext("title"), title.strip())], max_len=get_config(
            "post", "TITLE_MAX_LEN"), required=True)
    if not s:
        return r
    # content
    s, r = arg_verify(
        reqargs=[
            (gettext("content"), content.strip()), ("editor", editor)], required=True)
    if not s:
        return r

    text_l = len(content_text)
    if text_l > get_config("post", "BRIEF_LEN"):
        brief_content = content_text[0:get_config("post", "BRIEF_LEN")]
    else:
        brief_content = content_text
    s, r = arg_verify(
        reqargs=[
            (gettext("content"), content_text)], max_len=int(
            get_config(
                "post", "MAX_LEN")))
    if not s:
        data = r
    else:
        if issue_way == "issue":
            issue_way = 1
        else:
            issue_way = 0
        # 获取已上传的文章图片
        old_imgs = []
        if tid:
            # 文章更新
            post = mdbs["web"].db.post.find_one(
                {"_id": ObjectId(tid), "user_id": current_user.str_id})
            if post["issue_time"]:
                # 有发布时间，则发布时间不改变
                issue_time = post["issue_time"]
            elif issue_way:
                # 第一次发布
                issue_time = time.time()
            else:
                # 不发布
                issue_time = 0

            old_imgs = post["imgs"]

        elif issue_way:
            # 发布时间
            issue_time = time.time()
        else:
            # 不发布就不需要发布时间
            issue_time = 0

        # 获取文章中使用的图片
        # 如果是markdown
        if editor == "markdown":
            srcs = richtext_extract_img(richtext=markdown.markdown(content))
        else:
            srcs = richtext_extract_img(richtext=content)
        imgs = clean_tempfile(user_id=current_user.str_id,
                              type="image", old_file=old_imgs,
                              keey_file=srcs)

        if not cover_url and len(imgs) > 0:
            cover_url = imgs[0]

        if issue_way:
            r = content_inspection_text(
                "{} {} {}".format(
                    title, content, temp_tags))
            audit_score = r["score"]
            audit_label = r["label"]
            if r["label"] == "detection_off" or (
                    "suggestion" in r and r["suggestion"] == "review"):
                # 未开启审核或无法自动鉴别,　等待人工审核
                audited = 0
                audit_way = "artificial"

            elif r["label"] == "no_plugin":
                # 没有检查插件
                audited = 0
                audit_way = "artificial"

            else:
                audit_label = r["label"]
                audited = 1
                audit_way = "auto"
        else:
            # 草稿
            audit_label = None
            audited = audit_score = 0
            audit_way = "auto"
        content = content_attack_defense(content)["content"]
        brief_content = content_attack_defense(brief_content)["content"]
        post = {
            "title": title.strip(),
            "content": content.strip(),
            "brief_content": brief_content,
            "category": category,
            "tags": tags,
            "issued": issue_way,
            "issue_time": issue_time,
            "update_time": time.time(),
            "audited": audited,
            "audit_score": audit_score,
            "audit_user_id": None,
            "audit_way": audit_way,
            "audit_label": audit_label,
            "word_num": text_l,
            "is_delete": 0,
            "imgs": imgs,
            "cover_url": cover_url
        }

        if tid:
            mdbs["web"].db.post.update_one({"_id": ObjectId(tid), "user_id": current_user.str_id}, {
                                       "$set": post}, upsert=True)
        else:
            post["comment_num"] = 0
            post["like"] = 0
            post["like_user_id"] = []
            post["user_id"] = current_user.str_id
            post["editor"] = editor
            r = mdbs["web"].db.post.insert_one(post)
            tid = r.inserted_id

        # 如果已审核, 并且分数高于最高检查违规分, 给用户通知
        if audited and issue_way and audit_score >= get_config(
                "content_inspection", "ALLEGED_ILLEGAL_SCORE"):
            insert_user_msg(
                user_id=post["user_id"],
                ctype="notice",
                label="audit_failure",
                title=gettext("[Label:{}]Post allegedly violated").format(audit_label),
                content={
                    "text": post["brief_content"]},
                target_id=str(tid),
                target_type="post")
        if issue_way:
            data = {
                "msg": gettext("Issue success"),
                "msg_type": "s",
                "custom_status": 201}
        else:
            data = {
                "msg": gettext("Save success"),
                "msg_type": "s",
                "custom_status": 201}
    return data


def post_delete():

    ids = json_to_pyseq(request.argget.all('ids', []))
    recycle = int(request.argget.all('recycle', 1))

    if recycle:
        is_delete = 1
        msg = gettext("Removed to recycle bin")
    else:
        is_delete = 2
        msg = gettext("Delete the success")

    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)
    r = mdbs["web"].db.post.update_one({"_id": {"$in": ids},
                                    "user_id": current_user.str_id},
                                   {"$set": {"is_delete": is_delete}})
    if r.modified_count:
        data = {"msg": gettext("{},{}").format(msg, r.modified_count),
                "msg_type": "s", "custom_status": 201}
    else:
        data = {
            "msg": gettext("No match to relevant data"),
            "msg_type": "w",
            "custom_status": 400}
    return data


def post_restore():

    ids = json_to_pyseq(request.argget.all('ids', []))
    if not isinstance(ids, list):
        ids = json.loads(ids)
    for i, tid in enumerate(ids):
        ids[i] = ObjectId(tid)

    r = mdbs["web"].db.post.update_one({"_id": {"$in": ids},
                                    "user_id": current_user.str_id,
                                    "is_delete": 1},
                                   {"$set": {"is_delete": 0}})
    if r.modified_count:
        data = {"msg": gettext("Restore success,{}").format(r.modified_count),
                "msg_type": "s", "custom_status": 201}
    else:
        data = {
            "msg": gettext("Restore failed"),
            "msg_type": "w",
            "custom_status": 400}
    return data
