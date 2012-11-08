import ldap
from ldap.controls import SimplePagedResultsControl
import logging

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import User
from django.contrib.auth.models import SiteProfileNotAvailable


LOG = logging.getLogger(__name__)


class Command(NoArgsCommand):
    help = "Synchronize users and groups with an authoritative LDAP server"

    def handle_noargs(self, **options):
        groups = self.get_groups()
        users = self.get_users()

        self.sync_groups(groups)
        self.sync_users(users, groups)

    def get_users(self):
        """
        Retrieve users from target LDAP server.
        """
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
            LOG.error("Cannot connect to LDAP server: %s" % str(e))
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
                LOG.error("Server ignores RFC 2696 control")
                break

        l.unbind_s()

        return users

    def sync_users(self, users):
        """
        Synchronize users with local user database.
        """
        LOG.info("Synchronizing %d users" % len(users))

        for ldap_user in users:
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
                    LOG.info("User '%s' created" % username)
                else:
                    if not user.first_name == first_name.decode('utf-8'):
                        user.first_name = first_name
                        LOG.info("User '%s' first name updated" % username)
                    if not user.last_name == last_name.decode('utf-8'):
                        user.last_name = last_name
                        LOG.info("User '%s' last name updated" % username)
                    if not user.email == email:
                        user.email = email
                        LOG.info("User '%s' email updated" % username)
                user.save()

                try:
                    profile = user.get_profile()
                except (ObjectDoesNotExist, SiteProfileNotAvailable):
                    profile = UserProfile(user=user, id_num=id_num)
                    LOG.info("User '%s' profile created" % username)
                else:
                    if not profile.id_num == id_num:
                        profile.id_num = id_num
                        LOG.info("User '%s' id number updated" % username)
                try:
                    profile.save()
                except:
                    LOG.error("Duplicate ID '%s' encountered for '%s'" % (id_num, username))

        LOG.info("Users are synchronized")

    def get_groups(self):
        """
        Retrieve groups from target LDAP server.
        """
        pass

    def sync_groups(self):
        """
        Synchronize groups with local group database.
        """
        pass
