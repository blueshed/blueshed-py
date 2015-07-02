'''
Created on Apr 7, 2013

@author: peterb
'''
from pkg_resources import resource_filename  # @UnresolvedImport
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from blueshed.utils.email_template import EmailTemplate

def _work_(mail):
    mail.run()


class EmailPassword(EmailTemplate):
    
    def __init__(self, tmpl_path, email, **kwargs):
        EmailTemplate.__init__(self, tmpl_path, None, email, **kwargs)
        
    def run(self):
        plain, html = self._generate_content_()
        msg = MIMEMultipart('alternative')
        msg['From'] = self.mailfromaddr
        msg['To'] =  self.email
        msg['Subject'] = 'Welcome to blueshed-blogs'
        msg.attach(MIMEText(plain.decode(encoding='UTF-8'),"plain"))
        msg.attach(MIMEText(html.decode(encoding='UTF-8'),"html"))
        self._send_email_(msg)
        
        
    def _generate_content_(self):
        loader = self._get_loader_()
        plain = loader.load("email/password.txt").generate(email=self.email,**self.kwargs)
        html = loader.load("email/password.html").generate(email=self.email,**self.kwargs)
        return plain,html
        