package com.gaohanghang.springbootonlineexecutor.controller;

import com.gaohanghang.springbootonlineexecutor.service.ExecuteStringSourceService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class RunCodeController {
    private static final String defaultSource = "public class Run {\n"
            + "    public static void main(String[] args) {\n"
            + "        \n"
            + "    }\n"
            + "}";
    private Logger logger = LoggerFactory.getLogger(RunCodeController.class);
    @Autowired
    private ExecuteStringSourceService executeStringSourceService;

    @GetMapping("/")
    public String entry(Model model) {
        model.addAttribute("lastSource", defaultSource);
        return "ide";
    }

    @PostMapping("/run")
    public String runCode(@RequestParam("source") String source, Model model) {
        String runResult = executeStringSourceService.execute(source);
        runResult = runResult.replaceAll(System.lineSeparator(), "<br/>"); // 处理html中换行的问题

        model.addAttribute("lastSource", source);
        model.addAttribute("runResult", runResult);
        return "ide";
    }
}
