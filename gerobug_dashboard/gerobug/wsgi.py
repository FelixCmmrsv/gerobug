"""
WSGI config for gerobug project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""


import os, logging, gerocert.gerocert

from django.core.wsgi import get_wsgi_application
from geromail.thread import RunGeromailThread
from dashboards.models import BugReport, BugHunter, ReportStatus, StaticRules, BlacklistRule, CertificateData
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist
from prerequisites.models import MailBox
from dashboards.rulestemplate import *


# LOGGING INITIATION
def log_config():
    logging.basicConfig(filename='log/gerobug.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# INSERT STATUS TO DB
def init_status_db(id, name):
    if not ReportStatus.objects.filter(status_id=id).exists():
        status = ReportStatus()
        
        status.status_id = id
        status.status_name = name
        
        status.save()
        log_config()
        logging.debug("Init Status DB success")
    
    else:
        logging.debug("Status DB already exists")

# INSERT DEFAULT RULES (TERMS, SCOPE, ETC) AND BLACKLIST RULE TO DB
def init_rules_db():
    if  not StaticRules.objects.filter(pk=1).exists():
        staticrules = StaticRules()
        
        staticrules.RDP = RDP_template
        staticrules.bountyterms = bountyterms_template
        staticrules.inscope = inscope_templates
        staticrules.outofscope = outofscope_templates
        staticrules.reportguidelines = reportguidelines_templates
        staticrules.faq = faq_templates
        staticrules.save()
        log_config()
        logging.debug("Init Rules DB success")
    
    else:
        log_config()
        logging.debug("Rules DB already exists")
    
    if not BlacklistRule.objects.filter(rule_id=1).exists():
        blacklistrule = BlacklistRule()
        
        blacklistrule.rule_id = 1
        blacklistrule.max_counter = 10
        blacklistrule.buffer_monitor = 60
        blacklistrule.buffer_blacklist = 3600
        blacklistrule.buffer_clean = 86400
        blacklistrule.save()
        log_config()
        logging.debug("Init Blacklist Rules DB success")
    
    else:
        log_config()
        logging.debug("Blacklist Rules DB already exists")

# INSERT CERTIFICATE DATA TO DB
def init_cert_db(): 
    if not CertificateData.objects.filter(cert_id=1).exists():
        certdata = CertificateData()
        
        certdata.cert_id = 1
        certdata.officer_name = "Billy Sudarsono"
        certdata.officer_title = "Founder of Gerobug"
        certdata.save()

        gerocert.gerocert.generate_sample()
        log_config()
        logging.debug("Init Certificate Data success")
    
    else:
        log_config()
        logging.debug("Certificate Data already exists")

# INIT MAILBOX
def init_mailbox_db():
    if not MailBox.objects.filter(mailbox_id=1).exists():
        mailbox = MailBox()
        mailbox.mailbox_id = 1
        mailbox.email = ""
        mailbox.password = ""
        mailbox.save()
        log_config()
        logging.debug("Init Mailbox success")

    else:
        log_config()
        logging.debug("Mailbox already exists")

# INIT GROUP REVIEWER CREATION
def init_group():
    perm_list = Permission.objects.all()
    permissions = {}
    for perm in perm_list:
        permissions[perm.codename] = perm
    try:
        checker = Group.objects.get(name="Reviewer")
    except ObjectDoesNotExist:
        g_reviewer = Group.objects.create(name="Reviewer")
        g_reviewer.permissions.add(permissions['view_group'])
        g_reviewer.permissions.add(permissions['view_user'])
        g_reviewer.permissions.add(permissions['view_contenttype'])
        g_reviewer.permissions.add(permissions['view_bughunter'])
        g_reviewer.permissions.add(permissions['change_bugreport'])
        g_reviewer.permissions.add(permissions['view_bugreport'])
        g_reviewer.permissions.add(permissions['delete_bugreport'])
        g_reviewer.permissions.add(permissions['view_reportstatus'])
        g_reviewer.permissions.add(permissions['view_staticrules'])
        g_reviewer.permissions.add(permissions['view_session'])
    except:
        log_config()
        logging.debug("Group Reviewer shall be created successfully. Visit the Admin Site!")

def start_app():
    init_status_db(0, "Not Valid")
    init_status_db(1, "Need to Review")
    init_status_db(2, "In Review")
    init_status_db(3, "Fixing")
    init_status_db(4, "Fixing (Retest)")
    init_status_db(5, "Bounty Calculation")
    init_status_db(6, "Bounty in Process")
    init_status_db(7, "Completed")
    init_group()
    init_rules_db()
    init_cert_db()
    init_mailbox_db()

    log_config()
    logging.info("Number of Status         :"+str(ReportStatus.objects.count()))
    logging.info("Number of Report         :"+str(BugReport.objects.count()))
    logging.info("Number of Bug Hunters    :"+str(BugHunter.objects.count()))


    # RUN GEROMAIL MODULES
    RunGeromailThread(1).start()
    return get_wsgi_application()


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gerobug.settings')
application = start_app()