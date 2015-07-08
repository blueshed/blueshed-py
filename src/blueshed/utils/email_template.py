'''
Render a template and email the result

Created on Apr 7, 2013

@author: peterb
'''
from tornado.options import define, options
import tornado.template
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


define("mailhost", default=None, help="smtp host for logging")
define("mailport", default=smtplib.SMTP_PORT, type=int, help="smtp host port")
define("mailusername", default=None, help="smtp username")
define("mailpassword", default=None, help="smtp password")
define("mailsecure", default=False, type=bool, help="smtp secure")
define("mailfromaddr", default=None, help="email address of smtp sender")


def _work_(mail):
    mail.run()


class EmailTemplate(object):
    
    def __init__(self, tmpl_path, tmpl, email, **kwargs):
        self.tmpl_path = tmpl_path
        self.tmpl = tmpl
        self.email = email
        self.kwargs = kwargs
        self.mailfromaddr = kwargs.get("mailfromaddr",options.mailfromaddr)
        self.mailhost = kwargs.get("mailhost",options.mailhost)
        self.mailport = kwargs.get("mailport",options.mailport)
        self.mailusername = kwargs.get("mailusername",options.mailusername)
        self.mailpassword = kwargs.get("mailpassword",options.mailpassword)
        self.mailsecure = kwargs.get("mailsecure",options.mailsecure)
        
    
    def send(self):
        import multiprocessing
        p = multiprocessing.Process(target=_work_, args=(self,))
        p.start()
        
        
    def run(self):
        plain = self._generate_content_()
        msg = MIMEMultipart('alternative')
        msg['From'] = self.mailfromaddr
        msg['To'] =  self.email
        msg['Subject'] = self.kwargs.get("subject")
        msg.attach(MIMEText(plain.decode(encoding='UTF-8'),"plain"))
        self._send_email_(msg)
        
    
    def _get_loader_(self):
        return tornado.template.Loader(self.tmpl_path)
        
    def _generate_content_(self):
        loader = self._get_loader_()
        html = loader.load(self.tmpl).generate(**self.kwargs)
        return html
        
        
    def _send_email_(self, msg):
        smtp = smtplib.SMTP(self.mailhost, self.mailport)
    
        if self.mailsecure is True:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
    
        if self.mailusername:
            smtp.login(self.mailusername, self.mailpassword)
            
        smtp.sendmail(self.mailfromaddr, self.email, msg.as_string())
        
        smtp.quit()