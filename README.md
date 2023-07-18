# IntegraDataAuto - 数据驱动的移动自动化测试框架

## 概述

IntegraDataAuto是一个基于ATXServer2设计的移动设备自动化测试框架，具有以下特点:

- **数据驱动**:使用Excel表格配置测试设备信息和编写测试用例，实现数据驱动的自动化测试；
- **远程管理**:支持通过ATX Server远程连接并管理多台移动设备，无需在本机直接连接设备；
- **设备选择**:每次测试会自动随机选择或根据Excel配置条件选择指定设备,无需每次都重写配置信息；
- **跨平台**:目前支持Android平台的自动化测试，未来计划继续扩展为支持iOS和Web平台。

​		IntegraDataAuto通过Excel数据配置和ATX Server的远程设备管理，大大简化了移动应用的自动化测试。测试人员无需手动连接设备，只需要在Excel里配置设备信息和编写测试用例，即可轻松实现在多设备上的数据驱动的自动化测试。

​		该框架易于维护和扩展，目前已支持Android测试场景，未来将继续扩展对iOS和Web应用的自动化测试支持。

## 快速上手

### 环境搭建

> 其中 atxserver2-android-provider 推荐使用 python3.6 版本
>
> 在配置 atxserver2 时需要使用到 node.js 推荐使用版本为8，npm 为6
>
> 安装好之后可以将 python 、node、npm 换回较高版本
>
> （推荐使用 windows 的 node 环境管理工具 nvm）

1. node.js （版本为8 npm为6）

​		安装网址：http://nodejs.cn/download/

2. rethinkdb

​		安装网址：https://rethinkdb.com/docs/install/

​		项目中的安装包目录有

3. atxserver2：

​		安装网址： https://github.com/openatx/atxserver2

4. atxserver2-android-provider：（python3.6）

​		安装网址：https://github.com/openatx/atxserver2-android-provider

5. python：

   需要的软件包及版本在 requirements.txt 列出

   ```powershell
   pip install -r requirements.txt
   ```

### 环境启动

在项目的 server 目录下写了开启环境的脚本，可以在里面修改路径

> 环境启动.py 有点bug，每次开机如果不先在命令行手动启动，就获取不到设备，但是如果先在命令行启动又终止，再使用 py 脚本启动，是可以成功启动的

`startenv.bat` 启动环境没问题（就是要打开四个黑框框，有点强迫症）

`环境关闭.py` 关闭环境没问题（可能会遇上编码问题，但是功能没问题）

### 开始测试

在 testcase 中运行命令

> xxx 为测试用例名字

``` powershell
cd ./testcase
pytest xxx.py --html=report.html -v
```

### demo

1. 安装 APP（安装包下 appdebug.apk ）

2. 在 `./excel/data/data.xlsx` 中的 `conf` 工作表环境配置

   （详见参数说明）

   ![image-20230718095324291](D:/project/cloneproject/keyword_testing_framework/README.assets/image-20230718095324291.png)

3. 编写测试用例

   在 `./excel/data/data.xlsx` 中，工作表为  `test*` 或者 `*test` 

   > 每一个以 test 开头或以 test 结尾的工作表都会被视作一个单独的测试用例

| 操作                        | 方式                               | 选择器           | 定位元素的值                         | 给获取到的元素命名   | 操作的对象            | 操作的值     | 断言类型            | 断言的值              |
| --------------------------- | ---------------------------------- | ---------------- | ------------------------------------ | -------------------- | --------------------- | ------------ | ------------------- | --------------------- |
| find_and_click              | visibility_of_element_located      | accessibility id | 书城                                 | 书城                 | 书城                  |              |                     |                       |
| find                        | visibility_of_all_elements_located | id               | com.zhao.myreader:id/tv_book_desc    | rv_book_desc_list    |                       |              |                     |                       |
| $random_choice              |                                    |                  |                                      | book_desc            | rv_book_desc_list     |              |                     |                       |
| click                       |                                    |                  |                                      |                      | book_desc             |              |                     |                       |
| find_and_click              | visibility_of_element_located      | id               | com.zhao.myreader:id/btn_read_book   | btn_read_book        |                       |              |                     |                       |
| $action_chains_pointer_down |                                    |                  |                                      |                      |                       | 466,1242,0.5 |                     |                       |
| find_and_click              | visibility_of_element_located      | id               | com.zhao.myreader:id/ll_chapter_list | ll_chapter_list      | ll_chapter_list       |              |                     |                       |
| $store_directories          |                                    |                  |                                      | directories_list_one |                       |              |                     |                       |
| find_and_click              | visibility_of_element_located      | id               | com.zhao.myreader:id/tv_chapter_sort | tv_chapter_sort      | tv_chapter_sort       |              |                     |                       |
| $store_directories          |                                    |                  |                                      | directories_list_two |                       |              |                     |                       |
| assert                      |                                    |                  |                                      |                      | $directories_list_one |              | assert_list_reverse | $directories_list_two |

4. 开始测试

   在 pycharm 中运行 test_dsw.py 文件

   如果需要测试报告，则使用命令行运行

   ```powershell
   cd ./testcase
   pytest test_dsw.py --html=report.html -v
   pytest test_dsw.py --html=report.html -v --excel_path=../excel/data/data.xlsx
   
   ```

   > 可选参数：excel_path



## 参数说明

1. `excel_path` 数据表的路径 可选 

   默认为 `./excel/data/data.xlsx` 

   来源：命令行

   ```powershell
   cd ./testcase>
   pytest test_dsw.py -h
   # 在 Custom options 部分或搜索 excel_path 可以看到
   ```

   代码：

   ```python
   # conftest.py
   def pytest_addoption(parser):
       parser.addoption("--excel_path", action="store", default="../excel/data/data.xlsx",
                        help="可选参数，默认为../excel/data/data.xlsx")
       
   # test_dsw.py
   def test_dsw(pytestconfig, android_driver):
       excel_path = pytestconfig.getoption("excel_path")
   ```

   
