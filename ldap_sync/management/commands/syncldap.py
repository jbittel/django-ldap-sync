from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from notify.models import UserProfile
from django.conf import settings
import ldap
from ldap.controls import SimplePagedResultsControl
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        ldap_users = self.get_ldap_users()
        logger.info("Synchronizing %d users" % len(ldap_users))

        for ldap_user in ldap_users:
            try:
                username = ldap_user[1]['mailNickname'][0]
            except:
                pass
            else:
                try:
                    first_name = ldap_user[1]['givenName'][0]
                except:
                    first_name = ''
                try:
                    last_name = ldap_user[1]['sn'][0]
                except:
                    last_name = ''
                try:
                    id_num = ldap_user[1]['ipPhone'][0]
                except:
                    id_num = ''
                try:
                    email = ldap_user[1]['mail'][0]
                except:
                    email = ''

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User.objects.create_user(username, email)
                    user.first_name = first_name
                    user.last_name = last_name
                    logger.info("User '%s' created" % username)
                else:
                    if not user.first_name == first_name.decode('utf-8'):
                        user.first_name = first_name
                        logger.info("User '%s' first name updated" % username)
                    if not user.last_name == last_name.decode('utf-8'):
                        user.last_name = last_name
                        logger.info("User '%s' last name updated" % username)
                    if not user.email == email:
                        user.email = email
                        logger.info("User '%s' email updated" % username)
                user.save()

                try:
                    profile = user.get_profile()
                except UserProfile.DoesNotExist:
                    profile = UserProfile(user=user, id_num=id_num)
                    logger.info("User '%s' profile created" % username)
                else:
                    if not profile.id_num == id_num:
                        profile.id_num = id_num
                        logger.info("User '%s' id number updated" % username)
                try:
                    profile.save()
                except:
                    logger.error("Duplicate ID '%s' encountered for '%s'" % (id_num, username))

        logger.info("Users are synchronized")

    def get_ldap_users(self):
        filterstr = "(&(objectCategory=person)(objectClass=user))"
        attrlist = ['mailNickname', 'mail', 'givenName', 'sn', 'ipPhone', ]
        page_size = 100
        users = []

        try:
            l = ldap.initialize(settings.AUTH_LDAP_URI)
            l.set_option(ldap.OPT_REFERRALS, 0)
            l.protocol_version = ldap.VERSION3
            l.simple_bind_s(settings.AUTH_LDAP_BASE_USER, settings.AUTH_LDAP_BASE_PASS)
        except ldap.LDAPError, e:
            logger.error("Cannot connect to LDAP server: %s" % str(e))
            return None

        lc = SimplePagedResultsControl(ldap.LDAP_CONTROL_PAGE_OID, True, (page_size, ''))

        while True:
            msgid = l.search_ext(settings.AUTH_LDAP_BASE, ldap.SCOPE_SUBTREE, filterstr, attrlist, serverctrls=[lc])
            rtype, rdata, rmsgid, serverctrls = l.result3(msgid)
            for result in rdata:
                users.append(result)
            pctrls = [
                c
                for c in serverctrls
                if c.controlType == ldap.LDAP_CONTROL_PAGE_OID
            ]
            if pctrls:
                est, cookie = pctrls[0].controlValue
                if cookie:
                    lc.controlValue = (page_size, cookie)
                else:
                    break
            else:
                logger.error("Server ignores RFC 2696 control")
                break

        l.unbind_s()

        return users
