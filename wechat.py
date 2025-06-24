# -*- coding: utf-8 -*-
import sys
import ctypes
import gzip
import re
from io import BytesIO

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, __file__, None, 1
    )
    sys.exit(0)


try:
    import pydivert
except ImportError:
    print("请先运行：pip install pydivert")
    sys.exit(1)


def dechunk(body: bytes) -> bytes:
    buf = BytesIO(body)
    out = bytearray()
    while True:
        line = buf.readline()
        if not line:
            break
        line = line.strip().split(b";", 1)[0]
        try:
            size = int(line, 16)
        except ValueError:
            break
        if size == 0:
            # 跳过所有 trailers，直到遇到空行
            while True:
                trailer = buf.readline()
                if not trailer or trailer == b"\r\n":
                    break
            break
        chunk = buf.read(size)
        out.extend(chunk)
        buf.read(2)  # 跳过 CRLF
    return bytes(out)

req_buf = {}
resp_buf = {}

def make_key(pkt):
    return (pkt.src_addr, pkt.src_port, pkt.dst_addr, pkt.dst_port)

def extract_answers(html: str):
    return re.findall(r'<div class="option-item[^"]*\bactive\b[^"]*">\s*(.*?)\s*</div>', html, re.S)


FILTER = "tcp.DstPort == 80 or tcp.SrcPort == 80"
print(f">> 过滤 HTTP/80 流量：{FILTER}，Ctrl+C 停止…")

with pydivert.WinDivert(FILTER, layer=pydivert.Layer.NETWORK) as w:
    for pkt in w:
        tcp = pkt.tcp
        data = bytes(tcp.payload)
        key = make_key(pkt)

        # 客户端→服务端：HTTP 请求
        if tcp.dst_port == 80 and data:
            buf = req_buf.get(key, b"") + data
            if b"\r\n\r\n" in buf:
                line = buf.split(b"\r\n", 1)[0].decode(errors="ignore")
                print(f"[HTTP 请求] {line}")
                buf = buf.split(b"\r\n\r\n", 1)[1]
            req_buf[key] = buf

        # 服务端→客户端：HTTP 响应
        elif tcp.src_port == 80 and data:
            buf = resp_buf.get(key, b"") + data

            # 先确保拿到完整头部
            if b"\r\n\r\n" in buf:
                header, body = buf.split(b"\r\n\r\n", 1)
                hs = header.decode(errors="ignore").split("\r\n")
                status = hs[0]
                is_gzip = any(h.lower().startswith("content-encoding: gzip") for h in hs)
                is_chunked = any(h.lower().startswith("transfer-encoding: chunked") for h in hs)

                # 处理 chunked
                if is_chunked:
                    if b"\r\n0\r\n" not in body:
                        resp_buf[key] = buf
                        w.send(pkt)
                        continue
                    full = dechunk(body)
                else:
                    # 处理 Content-Length
                    cl = next((h for h in hs if h.lower().startswith("content-length:")), None)
                    if cl:
                        length = int(cl.split(":", 1)[1].strip())
                        if len(body) < length:
                            resp_buf[key] = buf
                            w.send(pkt)
                            continue
                        full = body[:length]
                    else:
                        full = None

                # 解压 gzip 并提取答案
                if full is not None and is_gzip and "200" in status:
                    try:
                        raw = gzip.decompress(full)
                        html = raw.decode(errors="ignore")
                        print(f"[HTTP 响应 解压 OK，长度={len(raw)}]")
                        # 自动提取答案
                        answers = extract_answers(html)
                        if answers:
                            print("—— 提取到的答案 ——")
                            for idx, ans in enumerate(answers, 1):
                                print(f"{idx}. {ans}")
                        else:
                            print("未在 HTML 中找到任何带 active 的选项。")
                    except Exception as e:
                        print(f"gzip 解压失败：{e}")

                # 清空缓存，确保下一次能重新聚合
                resp_buf[key] = b""

            else:
                resp_buf[key] = buf

        # 放行所有包
        w.send(pkt)