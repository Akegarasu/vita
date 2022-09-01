#!/usr/bin/env python
# -*-coding:utf-8-*-
# @Time : 2017/11/1 ~ 2019/9/1
# @Author : Allen Woo
from bson import Code
import time
from flask import request
from apps.core.utils.get_config import get_config
from apps.utils.format.time_format import time_to_utcdate
from apps.app import mdbs


def post_access():

    days = int(request.argget.all("days", 7))
    data = {}
    # 草稿
    query_conditions = {'issued': 0, 'is_delete': 0}
    data["draft"] = post_access_time(query=query_conditions, days=days)

    # recycle
    query_conditions = {'is_delete': 1}
    data["recycle"] = post_access_time(query=query_conditions, days=days)

    # Normal post
    query_conditions = {
        'issued': 1,
        'is_delete': 0,
        'audit_score': {
            "$lt": get_config(
                "content_inspection",
                "ALLEGED_ILLEGAL_SCORE")}}
    data["normal"] = post_access_time(query=query_conditions, days=days)
    return data


def post_access_time(query={}, days=7):

    now_time = time.time()
    s_time = now_time - 86400 * days - now_time % 86400
    query["$or"] = [{"issue_time": {"$gte": s_time}},
                    {"update_time": {"$gte": s_time}}]
    m = Code("""
        function(){
            var newDate = new Date();
            newDate.setTime(this.update_time*1000);
            var   year=newDate.getFullYear();
            var   month=newDate.getMonth()+1;
            var   date=newDate.getDate();
            var g_f = {"date":year*10000+month*100+date, "update_time":this.update_time-this.update_time%86400}

            var value = {count:1}
            emit(g_f, value);
        }
    """)

    r = Code("""

        function(key,values){
            var ret = {count:0};
            values.forEach(
                function(v){
                    ret.count += v.count;
                }
            );
            return ret;
        }
    """)
    result = mdbs["web"].db.post.map_reduce(
        m, r, out={"inline": 1}, full_response=True, query=query)
    if result['counts']["output"] > 0:
        temp_result = sorted(result["results"], key=lambda x: x["_id"]["date"])
        last_time = s_time - 86400
        for r in temp_result:
            r_time = r["_id"]["update_time"] - r["_id"]["update_time"] % 86400
            if r_time > last_time + 86400:
                for i in range(1, int((r_time - last_time) / 86400)):

                    last_time += 86400
                    result["results"].append({"_id": {"update_time": last_time, "date": time_to_utcdate(
                        last_time, "%Y%m%d")}, "value": {"count": 0}})
                last_time += 86400
            else:
                last_time += 86400
        result["results"] = sorted(
            result["results"],
            key=lambda x: x["_id"]["date"])
        return result["results"]
    else:
        return {}
