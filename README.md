# 使用说明
2019年6月24日  已打包成EXE 1、通过双击**demo\dist\Cqvip_main.exe**  既可，无需配置相关环境和库文件  
## 注意：  
别直接用window的文本编辑器直接打开Config.ini，window文本编辑器编码格式默认是有BOM，会改变配置文件的编码格式，所以请用Notepad++
1. 其中**demo\dist\Config.ini**中： 
    ``` ini
    [DB] ;数据库相关参数设定，只需新建一个cqvipcrawler数据库即可，或者执行对应的SQL语句
    dbname = cqvipcrawler ;数据库名称这个得新建
    dbhost = 127.0.0.1 
    dbuser = root
    dbpwd = 12345678
    dbcharset = utf8
    dbport = 3306
    [Cqvip] ;目前只做了维普
    restart = 0  ;0 继续原有参数执行；  1：恢复初始，重新执行
    input = 自组网 ;输入关键词
    starttime = 1990 ;开始年份
    endtime = 2018 ;结束年份
    searchmode = 1 ;选择模式 1：标题 2：作者 3：关键字 4：单位 5:出刊物
    startpage = 156 ;[参量不用动]
    maxpage = 267;[参量不用动]
    stopflag = 0;[参量不用动]
    flag_get_all_url = 0;[参量不用动]
    
    ```
 ## 举例
例一　需要查询以【标题】为 _**自组网**_ 检索【维普】从【2001年-2018年】的全部文献
 修改如下：
 ``` ini
    [Cqvip]
    restart = 1 ;0 继续原有参数执行；  1：恢复初始，重新执行
    input = 自组网 ;输入关键词
    starttime = 2001 ;开始年份
    endtime = 2018 ;结束年份
    searchmode = 1 ;选择模式 1：标题 2：作者 3：关键字 4：单位 5:出刊物
```
例二   
    如果查询到一半停止了，需要重复进行，则重新打开exe即可  
例三   
    如果需要更改检索其他项，则同例1
