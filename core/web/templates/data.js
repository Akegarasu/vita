var datas = {
    "basic": {
        "totleNum": "100",
        "criticalLevel":"10",
        "highLevel":"10",
        "mediumLevel":"50",
        "lowLevel":"20",
        "prompt":"10"
    },
    "problems":[{
        "language":"go",
        "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
        "match_type":"ast",
        "match_rule":"eval",
        "description":"命令执行",
        "file_path":"/etc/passwd/main.go",
        "severity":"critical",
        "ptype":"木马/后门",
        "confidence":"0.5"
    },{
        "language":"python",
        "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
        "match_type":"regex",
        "match_rule":"fsdf",
        "description":"和覅士大夫",
        "file_path":"/etc/passwd/main.py",
        "severity":"high",
        "ptype":"漏洞",
        "confidence":"1.0"
    },{
      "language":"python",
      "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
      "match_type":"regex",
      "match_rule":"fsdf",
      "description":"和覅士大夫",
      "file_path":"/etc/passwd/main.py",
      "severity":"high",
      "ptype":"漏洞",
      "confidence":"0.1"
  },{
    "language":"python",
    "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
    "match_type":"regex",
    "match_rule":"fsdf",
    "description":"和覅士大夫",
    "file_path":"/etc/passwd/main.py",
    "severity":"prompt",
    "ptype":"漏洞",
    "confidence":"0.1"
  },{
    "language":"python",
    "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
    "match_type":"regex",
    "match_rule":"fsdf",
    "description":"和覅士大夫",
    "file_path":"/etc/passwd/main.py",
    "severity":"medium",
    "ptype":"漏洞",
    "confidence":"0.1"
  },{
    "language":"python",
    "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
    "match_type":"regex",
    "match_rule":"fsdf",
    "description":"和覅士大夫",
    "file_path":"/etc/passwd/main.py",
    "severity":"low",
    "ptype":"漏洞",
    "confidence":"0.1"
  },{
    "language":"go",
    "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
    "match_type":"ast",
    "match_rule":"eval",
    "description":"命令执行",
    "file_path":"/etc/passwd/main.go",
    "severity":"critical",
    "ptype":"木马/后门",
    "confidence":"0.5"
  },{
    "language":"python",
    "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
    "match_type":"regex",
    "match_rule":"fsdf",
    "description":"和覅士大夫",
    "file_path":"/etc/passwd/main.py",
    "severity":"high",
    "ptype":"漏洞",
    "confidence":"1.0"
  },{
  "language":"python",
  "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
  "match_type":"regex",
  "match_rule":"fsdf",
  "description":"和覅士大夫",
  "file_path":"/etc/passwd/main.py",
  "severity":"high",
  "ptype":"漏洞",
  "confidence":"0.1"
  },{
  "language":"python",
  "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
  "match_type":"regex",
  "match_rule":"fsdf",
  "description":"和覅士大夫",
  "file_path":"/etc/passwd/main.py",
  "severity":"prompt",
  "ptype":"漏洞",
  "confidence":"0.1"
  },{
  "language":"python",
  "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
  "match_type":"regex",
  "match_rule":"fsdf",
  "description":"和覅士大夫",
  "file_path":"/etc/passwd/main.py",
  "severity":"medium",
  "ptype":"漏洞",
  "confidence":"0.1"
  },{
  "language":"python",
  "context":"    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] \u626b\u63cf\u7ed3\u675f,\u8017\u65f6: %s\", t)\n    13   }",
  "match_type":"regex",
  "match_rule":"fsdf",
  "description":"和覅士大夫",
  "file_path":"/etc/passwd/main.py",
  "severity":"low",
  "ptype":"漏洞",
  "confidence":"0.1"
  }]
  }