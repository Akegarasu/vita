package cn.attackme.myuploader.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import springfox.documentation.builders.ApiInfoBuilder;
import springfox.documentation.builders.PathSelectors;
import springfox.documentation.builders.RequestHandlerSelectors;
import springfox.documentation.service.ApiInfo;
import springfox.documentation.spi.DocumentationType;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger2.annotations.EnableSwagger2;

/**
 * @Description: swagger配置类
 * @author: Gao Hang Hang
 * @date 2019/01/14 18:42
 */
@Configuration
@EnableSwagger2
public class SwaggerConfig {

    /**
     * TODO
     * 可以根据配置读取是否开启swagger文档，针对测试与生产环境采用不同的配置
     */
    private boolean isSwaggerEnable = true;

    @Bean
    public Docket createRestApi() {
        return new Docket(DocumentationType.SWAGGER_2)
                .groupName("group")
                .enable(isSwaggerEnable)
                .apiInfo(apiInfo()).select()
                // 对所有该包下的Api进行监控，如果想要监控所有的话可以改成any()
                .apis(RequestHandlerSelectors.basePackage("cn.attackme.myuploader"))
                // 对所有路径进行扫描
                .paths(PathSelectors.any())
                .build();
    }

    /**
     * @return 生成文档说明信息
     */
    private ApiInfo apiInfo() {
        return new ApiInfoBuilder()
                .title("SpringBoot实现文件上传系统")
                .description("单文件上传，多文件上传，大文件上传，断点续传，文件秒传，图片上传")
                //.termsOfServiceUrl("http://gaohanghang.github.io")
                .license("Apache 2.0")
                .licenseUrl("http://www.apache.org/licenses/LICENSE-2.0")
                .version("2.0.0").build();
    }
}
