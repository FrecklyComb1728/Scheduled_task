import smtplib
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
import logging
import os

# =================== 配置参数 ===================
class Config:
    SMTP_SERVER = 'smtp.bee-zh.cn'
    SMTP_PORT = 465
    EMAIL_USER = 'scheduled_task@bee-zh.cn'
    EMAIL_PASSWORD = os.environ.get('TIXINGYOUXIANG_SMTP_PASSWORD')
    RECIPIENT = 'wdsjwyf@qq.com'

    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)

# =================== 日志系统 ===================
def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    log_file = os.path.join(Config.LOG_DIR, f'renewal_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger

# =================== 邮件服务 ===================
def send_email(subject, content):
    try:
        msg = MIMEText(content, 'html', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = Config.EMAIL_USER
        msg['To'] = Config.RECIPIENT
        
        with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
            server.login(Config.EMAIL_USER, Config.EMAIL_PASSWORD)
            server.sendmail(Config.EMAIL_USER, [Config.RECIPIENT], msg.as_string())
        return True
    except Exception as e:
        logger.error(f"邮件发送失败: {str(e)}")
        return False

# =================== 程序入口 ===================
if __name__ == '__main__':
    logger = setup_logger()
    
    html = """
    <div>
        <h1>提醒navy36393续费服务器</h1>
    </div>
    """
    
    subject = "提醒navy36393"
    if send_email(subject, html):
        logger.info("邮件发送成功")
    else:
        logger.error("邮件发送失败")