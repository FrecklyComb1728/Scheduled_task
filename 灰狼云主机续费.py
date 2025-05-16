import requests
import hashlib
import time
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime

# =================== 配置参数 ===================
class Config:
    # 主机配置
    HOST_ID = '9838'
    API_KEY = '5b789449588970a25706918a3fc82010'
    RENEW_MONTH = '1'
    
    # 邮件配置
    SMTP_SERVER = 'smtphz.qiye.163.com'
    SMTP_PORT = '465'
    EMAIL_USER = 'scheduled_task@bee-zh.cn'
    SMTP_PASSWORD = os.environ.get('HUILANGYUNXVFEI_SMTP_PASSWORD')
    RECIPIENT = 'wdsjwyf@qq.com'

# =================== 邮件服务 ===================
def send_email(subject, content):
    try:
        msg = MIMEText(content, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = Config.EMAIL_USER
        msg['To'] = Config.RECIPIENT
        
        with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.login(Config.EMAIL_USER, Config.SMTP_PASSWORD)
            server.sendmail(Config.EMAIL_USER, [Config.RECIPIENT], msg.as_string())
        return True
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        return False

def format_result_html(result):
    status = "成功" if result['code'] == 1 else "失败"
    data = result.get('data', {}) or {}
    
    table_rows = ''.join(f'<tr><td style="border:1px solid #ddd;padding:8px;">{key}</td>'
                         f'<td style="border:1px solid #ddd;padding:8px;">{value}</td></tr>' 
                         for key, value in data.items())
    
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px;">
            灰狼云主机续费报告 - {datetime.now().strftime("%Y-%m-%d %H:%M")}
        </h2>
        <table style="width:100%; border-collapse: collapse;">
            <tr>
                <td style="background-color:#f1f5f9; width:30%; font-weight:bold; border:1px solid #ddd; padding:8px;">状态</td>
                <td style="border:1px solid #ddd; padding:8px;">{status}</td>
            </tr>
            <tr>
                <td style="background-color:#f1f5f9; font-weight:bold; border:1px solid #ddd; padding:8px;">消息</td>
                <td style="border:1px solid #ddd; padding:8px;">{result['msg']}</td>
            </tr>
            {table_rows}
        </table>
        <p style="color:#64748b; font-size:0.8em; margin-top:24px;">本报告由自动化脚本生成，请勿直接回复</p>
    </div>
    """
    return html

def renew_host():
    try:
        print("开始执行灰狼云主机续费操作...")
        
        # 生成签名
        timestamp = str(int(time.time()))
        sign_str = Config.HOST_ID + timestamp + Config.API_KEY
        signature = hashlib.md5(sign_str.encode()).hexdigest()
        
        # 发起请求
        url = 'https://www.yun316.net/api/host/renew'
        payload = {
            'h': Config.HOST_ID,
            't': timestamp,
            's': signature,
            'm': Config.RENEW_MONTH
        }
        
        print(f"发送请求到: {url}, 参数: {payload}")
        response = requests.post(url, data=payload, timeout=10)
        result = response.json()
        
        # 记录结果
        print(f"API响应: {response.text}")
        
        # 发送邮件
        status_msg = status_map.get(result['code'], "未知状态")
        subject = f"灰狼云主机续费报告 - {status_msg}"
        email_content = format_result_html(result)
        if send_email(subject, email_content):
            print("邮件发送成功")
        else:
            print("邮件发送失败")
            
        return result
    except requests.exceptions.RequestException as e:
        error_msg = f"网络请求异常: {str(e)}"
        print(error_msg)
        return {'code': -1, 'msg': error_msg, 'data': None}
    except Exception as e:
        error_msg = f"程序异常: {str(e)}"
        print(error_msg)
        return {'code': -1, 'msg': error_msg, 'data': None}

# 状态码映射
status_map = {
    1: "成功",
    400: "签名验证失败",
    404: "主机不存在",
    500: "系统错误"
}