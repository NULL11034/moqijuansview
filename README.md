# 微信默契局答案获取器

> 用来查看微信默契局的答案

## 功能

* 拦截并解析 HTTP/80 流量（支持 `chunked` 与 `Content-Length`）
* 自动解压 `gzip` 编码的响应包
* 完善的 `chunked` 解码函数
* UAC 提权：以管理员权限运行，自动重启获取更高权限
* （可选）在调试模式下保存抓取到的完整 HTML 内容（`--debug`）

## 使用方法
1. 在 [Release](https://github.com/NULL11034/moqijuansview/releases/tag/Release) 页面下载最新版本的可执行文件。

2. 在电脑上的朋友圈等来源打开默契局宣传图片并点击上方的提取二维码进入默契局页面。

3. 双击运行 `wechat.exe` ，程序会提示 UAC 提权。

4. 完成提权后，开始拦截 HTTP/80 流量。

5. 点击默契局左上角的刷新图标。

6. 当检测到标准 HTTP 请求与响应并成功解压后，将在控制台输出答案列表。
   若在启动时附加 `--debug` 参数，将把完整 HTML 保存到 `./debug/YYYY-MM-DD_HH-MM-SS.html` 文件中，方便离线分析。

7. 按 `Ctrl+C` 停止程序。

    ![d3a7e38f-78c4-4ef9-9579-109df177116c](https://github.com/user-attachments/assets/751bd60f-67db-4d4d-9441-826a06527032)

## 注意事项

* 需要在 Windows 下以管理员权限运行。
* 打包后的 exe 文件已包含所有依赖，无需额外安装。
* 本工具仅供学习和测试，请勿用于非法用途。

## 开发

### 环境

- Python 3.10+
- [sudo](https://learn.microsoft.com/zh-cn/windows/advanced-settings/sudo/) 已启用

  默认情况下, Visual Studio Code 会以用户权限运行, 需要使用 sudo 提权, 否则需要以管理员身份运行 Visual Studio Code 或程序自主提权后在新窗口中运行。

### 使用

1. 克隆本项目。

    ```bash
    git clone https://github.com/NULL11034/moqijuansview.git

    cd ./moqijuansview/
    ```
2. 安装所需依赖。

    ```bash
    pip install -r requirements.txt
    ```

3. 运行程序。

    ```bash
    # 正常模式
    sudo python ./wechat.py

    # 调试模式（保存 HTML 到 debug/ 目录）
    sudo python ./wechat.py --debug
    ```


## 许可证

本项目基于 MIT 协议开源。
