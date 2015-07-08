'''
HTML and Plain template emails

Created on 30 Jan 2015

@author: peterb
'''
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from blueshed.utils.email_template import EmailTemplate


class EmailPlainAndHtml(EmailTemplate):
    
    def run(self):
        plain, html = self._generate_content_()
        msg = MIMEMultipart('alternative')
        msg['From'] = self.mailfromaddr
        msg['To'] =  self.email
        msg['Subject'] = self.kwargs.get("subject")
        msg.attach(MIMEText(plain.decode(encoding='UTF-8'),"plain"))
        msg.attach(MIMEText(html.decode(encoding='UTF-8'),"html"))
        self._send_email_(msg)

    
    def _generate_content_(self):
        loader = self._get_loader_()
        plain = loader.load(self.tmpl+".txt").generate(email=self.email,**self.kwargs)
        html = loader.load(self.tmpl+".html").generate(email=self.email,**self.kwargs)
        return plain,html
