var datas = {"problems": [{"language": "go", "match_type": "ast", "match_rule": "Printf", "description": "输出文字", "file_path": ".\\gotest\\test.go", "severity": "critical", "context": "    9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n--> 12   \tfmt.Printf(\"[*] 扫描结束,耗时: %s\", t)\n    13   }", "ptype": "待定", "confidence": "NAN"}, {"language": "go", "match_type": "ast", "match_rule": "Printf", "description": "输出文字", "file_path": ".\\gotest\\test.go", "severity": "critical", "context": "    9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n--> 12   \tfmt.Printf(\"[*] 扫描结束,耗时: %s\", t)\n    13   }", "ptype": "待定", "confidence": "NAN"}, {"language": "go", "match_type": "ast", "match_rule": "common", "description": "commoncve", "file_path": ".\\gotest\\test.go", "severity": "prompt", "context": "    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] 扫描结束,耗时: %s\", t)\n    13   }", "ptype": "待定", "confidence": "NAN"}, {"language": "go", "match_type": "ast", "match_rule": "common", "description": "commoncve", "file_path": ".\\gotest\\test.go", "severity": "prompt", "context": "    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] 扫描结束,耗时: %s\", t)\n    13   }", "ptype": "待定", "confidence": "NAN"}, {"language": "go", "match_type": "ast", "match_rule": "common", "description": "commoncve", "file_path": ".\\gotest\\test.go", "severity": "prompt", "context": "    6       start := time.Now()\n    7   \tvar Info common.HostInfo\n    8   \tcommon.Flag(&Info)\n--> 9   \tcommon.Parse(&Info)\n    10   \tPlugins.Scan(Info)\n    11   \tt := time.Now().Sub(start)\n    12   \tfmt.Printf(\"[*] 扫描结束,耗时: %s\", t)\n    13   }", "ptype": "待定", "confidence": "NAN"}, {"language": "java", "match_type": "ast", "match_rule": "执行系统命令", "description": "执行系统命令", "file_path": ".\\test\\Test.java", "severity": "prompt", "context": "    19       private String demo;\n    20       public String getSampleField(String demo) {\n    21           this.demo=demo;\n--> 22           Runtime.getRuntime.exec(\"calc\");\n    23           return sampleField;\n    24       }\n    25   \n    26       public void setSampleField(String sampleField) {\n    27           this.sampleField = sampleField;", "ptype": "待定", "confidence": "NAN"}, {"language": "java", "match_type": "ast", "match_rule": "执行系统命令", "description": "执行系统命令", "file_path": ".\\test\\Test.java", "severity": "prompt", "context": "    19       private String demo;\n    20       public String getSampleField(String demo) {\n    21           this.demo=demo;\n--> 22           Runtime.getRuntime.exec(\"calc\");\n    23           return sampleField;\n    24       }\n    25   \n    26       public void setSampleField(String sampleField) {\n    27           this.sampleField = sampleField;", "ptype": "待定", "confidence": "NAN"}], "basic": {"totleNum": 7, "criticalLevel": 2, "highLevel": 0, "mediumLevel": 0, "lowLevel": 0, "prompt": 5}}