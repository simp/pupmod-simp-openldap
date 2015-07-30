Summary: OpenLDAP Puppet Module
Name: pupmod-openldap
Version: 4.1.1
Release: 2
License: Apache License, Version 2.0
Group: Applications/System
Source: %{name}-%{version}-%{release}.tar.gz
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Requires: pupmod-auditd >= 4.1.0-2
Requires: pupmod-common >= 4.1.0-6
Requires: pupmod-concat >= 2.0.0-0
Requires: pupmod-iptables >= 4.1.0-3
Requires: pupmod-logrotate >= 4.1.0-0
Requires: pupmod-nscd >= 5.0.0-0
Requires: pupmod-pki >= 3.0.0-0
Requires: pupmod-rsyslog >= 4.1.0-0
Requires: pupmod-sssd >= 4.0.0-1
Requires: pupmod-tcpwrappers >= 2.1.0-0
Requires: puppet >= 3.3.0
Requires: simp_bootstrap >= 2.0.0-1
Requires: puppetlabs-stdlib >= 4.1.0-0.SIMP
Buildarch: noarch
Requires: simp-bootstrap >= 4.2.0
Obsoletes: pupmod-openldap-test

Prefix: /etc/puppet/environments/simp/modules

%description
This Puppet module provides the capability to configure OpenLDAP servers and
clients.

Some of the server configurations are pulled from rsync.

%prep
%setup -q

%build

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

mkdir -p %{buildroot}/%{prefix}/openldap

dirs='files lib manifests templates'
for dir in $dirs; do
  test -d $dir && cp -r $dir %{buildroot}/%{prefix}/openldap
done

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

mkdir -p %{buildroot}/%{prefix}/openldap

%files
%defattr(0640,root,puppet,0750)
%{prefix}/openldap

%post
#!/bin/sh

if [ -d %{prefix}/openldap/plugins ]; then
  /bin/mv %{prefix}/openldap/plugins %{prefix}/openldap/plugins.bak
fi

%postun
# Post uninstall stuff

%changelog
* Thu Jul 30 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.1-2
- Made the password policy overlay align with the latest SIMP build of the
  plugin.
- This means that you *must* have version simp-ppolicy-check-password-2.4.39-0
  or later available to the system being configured.

* Sat May 16 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.1-1
- More closely align with the published STIG guidelines.

* Thu Mar 26 2015 Jacob Gingrich <jgingrich@onyxpoint.com> - 4.1.1-0
- Updated the module for facter 2.4.
- nslcd threads set to 5, no longer 'dynamic'.

* Thu Mar 12 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-17
- Fixed an incorrect call to sync_password instead of sync_pw in syncrepl.pp.
- Fixed an incorrect call to $::openldap::server::sync_dn to ldap::sync_dn in hiera.

* Thu Feb 19 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-16
- Migrated to the new 'simp' environment.
- Changed calls directly to /etc/init.d/rsyslog to '/sbin/service rsyslog' so
  that both RHEL6 and RHEL7 are properly supported.

* Fri Jan 16 2015 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-15
- Changed puppet-server requirement to puppet

* Wed Nov 05 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-14
- Changed the cipher sets to the workround FIPS compliant set since
  RHEL6.6 includes the bug that plagues RHEL7.
- Details: https://bugzilla.redhat.com/show_bug.cgi?id=1123092

* Sun Nov 02 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-13
- Updated to add support for custom options as well as proper support for the
  RHEL7 configuration file location.

* Fri Oct 17 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-12
- CVE-2014-3566: Updated ciphers to help mitigate POODLE.
  Unfortunately, OpenSSL cannot set the SSL protocol to be used.
  However, all clients will negotiate the most secure first and
  testing has indicated that they are all using TLSv1.

* Fri Oct 03 2014 Kendall Moore <kmoore@keywcorp.com> - 4.1.0-11
- Updated the manifests and templates for missing variables from ssh_ldap.conf.

* Thu Aug 21 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-10
- Properly account for the fact that @uri is an array, not a string.

* Thu Aug 07 2014 Kendall Moore <kmoore@keywcorp.com> - 4.1.0-9
- Enabled authlogin_nsswitch_use_ldap for nslcd to work with targeted SELinux mode on

* Tue Jul 22 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-8
- Updated to handle the recompiled/deconflicted
  simp-ppolicy-check-password RPM for RHEL7.

* Wed Jul 09 2014 Adam Yohrling <adam.yohrling@onyxpoint.com> - 4.1.0-7
- Modified client certs to point at /etc/pki instead of /etc/openldap/pki,
  which is the server location.

* Mon Jul 07 2014 Nick Markowski <nmarkowski@keywcorp.com> - 4.1.0-6
- Spec tests were missing Facts used by supporting modules, due to
  updates over time. Spec tests now run cleanly.

* Mon Jun 30 2014 Adam Yohrling <adam.yohrling@onyxpoint.com> - 4.1.0-5
- Updated the sync_dn default value to be correct syntactically with
  a 'cn=' and also modified the ou from People to Hosts to match
  the standard SIMP default.

* Sun Jun 22 2014 Kendall Moore <kmoore@keywcorp.com> - 4.1.0-4
- Removed MD5 file checksums for FIPS compliance.

* Wed Apr 30 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-3
- Made numerous modifications to support the removal of the 'default_classes'
  material.
- Changes to defines:
  * syncrepl::conf => syncrepl
  * slapd::conf => <class>
  * slapo::ppolicy::conf => <class>
  * slapo::syncprov::conf => <class>
- Added support for multiple top level hiera values to support a more generic
  LDAP infrastructure.
  * ldap::base_dn
  * ldap::bind_dn
  * ldap::bind_pw
  * ldap::bind_hash
  * ldap::sync_dn
  * ldap::root_dn
  * ldap::root_hash
  * ldap::uri (array)
  * ldap::master
- Updated to use the pki::copy define.
- Removed the openldap::slapd::pki class
- Removed all reliance on Rsync and added the setting of schemas to
  openldap::server. Made the schema source variable so that you can add your
  own elsewhere if you so choose. Users can add to our file space if they wish.

* Thu Feb 13 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-2
- WARNING: All legacy code is probably broken at this point!
- Converted all string booleans to booleans
- Added new options to slapd.conf
- Removed unused nss_* options from pam_ldap.conf
- Updated the slapd.conf.erb template to actually *use* all of the
  variables in the manifest
- Modified the slapd_pki.pp to copy the PKI files instead of messing
  about with ACLs.
- Update to remove warnings about IPTables not being detected. This is a
  nuisance when allowing other applications to manage iptables legitimately.
- Added several additional safety features to bootstrap_ldap.
- A lock file was added at /etc/openldap/puppet_bootstrapped.lock that will
  need to be removed before bootstrap will run again.
- When OS upgrades reconfigure the LDAP configuration structure, the execs
  handle things properly.

* Mon Jan 06 2014 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.1.0-1
- Ensure that Exec['bootstrap_ldap'] does not break LDAP slave
  syncing.

* Thu Dec 12 2013 Morgan Haskel <morgan.haskel@onyxpoint.com> - 4.1.0-0
- Added support for LDAP referral chaining by default.

* Sat Dec 07 2013 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.0-20
- The lastbind material was updated to properly require the simp-lastbind
  package.

* Wed Nov 27 2013 Nick Markowski <nmarkowski@keywcorp.com> - 4.0.0-19
- Ldap bootstrap now uses slaptest to ensure a sane ldap config before blowing
  the databases away.  Re-wrote fixperms to ensure ALL files in /var/lib/ldap/
  owned by ldap.

* Tue Nov 19 2013 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.0-19
- Fixed a bug in the handling of slapd.access. This should be turned
  into a native type.

* Mon Oct 21 2013 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.0-18
- Removed akeys completely.
- Cleaned up some code in the templates.

* Tue Oct 08 2013 Nick Markowski <nmarkowski@keywcorp.com> - 4.0.0-18
- Updated template to reference instance variables with @

* Wed Oct 02 2013 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.0-17
- Use 'versioncmp' for all version comparisons.

* Thu Sep 26 2013 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0.0-16
- Added a dependency on the cacerts directory to the nslcd service.

* Tue Sep 03 2013 Nick Markowski <nmarkowski@keywcorp.com> - 4.0-15
- Incorporated the lastbind overlay to record an authTimestamp which updates
  every time a user binds.

* Wed Jul 10 2013 Trevor Vaughan <tvaughan@onyxpoint.com> - 4.0-14
- The settings on the LDAP server were not set to allow the LDAPSync user to
  pull more than the default number of entries. This caused the slave servers
  to only pull a subset of the proper entries. This has been fixed so that
  including syncprov will set the correct pull settings.

* Fri May 24 2013 Adam Yohrling <adam.yohrling@onyxpoint.com> 4.0-13
- Patched slapd.pp to use a dynamic ldap_sync_dn and ldap_bind_dn so that
  existing servers can optionally be used without reconfiguration.

* Thu May 02 2013 Nick Markowski <nmarkowski@keywcorp.com> 4.0-13
- Removed pull_keys, as openssh now uses openssh-ldap to authenticate public keys.
- Ensured akeys cron job absent.
- Added an exec to slapd.pp to check permissions on /var/lib/ldap/* and chown
  them to ldap:ldap if necessary.
- Changed the slapcat runuser to ldap.

* Mon Feb 25 2013 Maintenance
4.0-12
- Added a call to $::rsync_timeout to the rsync call since it is now required.

* Fri Jan 11 2013 Maintenance
4.0.0-11
- Added support for environments that do not require a bind password
  or username.

* Wed Nov 07 2012 Maintenance
4.0.0-10
- Added support for locker manipulation in DB_CONFIG as well as multi-thread
  support.
- Made the checkpoint variable optional in slapd.conf.
- Add the ability to nuke log files using incrond by setting the
  $force_log_quick_kill variable in openldap::slapd::conf.
- Update to enable transaction auditing by default.
- Updated akeys to ignore anything that is not a regular file or link.

* Mon Sep 24 2012 Maintenance
4.0.0-9
- Update toakeys to print to syslog by default.

* Thu Aug 02 2012 Maintenance
4.0.0-8
- Ensure that nslcd is restarted when host PKI keys are updated.

* Thu Jun 07 2012 Maintenance
4.0.0-7
- Ensure that Arrays in templates are flattened.
- Call facts as instance variables.
- Moved mit-tests to /usr/share/simp...
- Removed test for pam lock
- Updated pp files to better meet Puppet's recommended style guide.

* Mon Mar 12 2012 Maintenance
4.0.0-6
- Updated tests.
- Improved test stubs.

* Fri Feb 10 2012 Maintenance
4.0.0-5
- Removed the local user tests from here and added them to common.

* Wed Dec 14 2011 Maintenance
4.0.0-4
- Added an initial suite of tests.
- Updated the spec file to not require a separate file list.
- Scoped all of the top level variables.
- Made sure that syncrepl.la is only included pre-5.7.
- Dropped the bind_timelimit to '5' to alleviate login failures.
- Added a section for prod_nscd to the RHEL < 6 portion of the openldap
  client_auth segment.

* Mon Dec 05 2011 Maintenance
4.0.0-3
- Permissions on akeys match those set by the cron permissions check script in
  the 'sec' module.

* Mon Nov 07 2011 Maintenance
4.0.0-2
- Fixed call to rsyslog restart for RHEL6.
- Modified the openldap module such that you can now use
  openldap::slapd::access::add to add custom access control capabilities to
  /etc/openldap/slapd.access.
- Added a variable $openldap::slapd::slapd_svc to hold the name of the 'slapd'
  service since it changes from 'ldap' to 'slapd' in RHEL6.
- Fixed the portions that were required to use an OpenLDAP slave in RHEL6.
- Updated to use both nscd and nslcd.
- Added a selective variable for the location of the PAM LDAP configuration
  file based on the version of Red Hat that it's being installed under.

* Mon Oct 10 2011 Maintenance
4.0.0-1
- Updated to put quotes around everything that need it in a comparison
  statement so that puppet > 2.5 doesn't explode with an undef error.
- Modified all multi-line exec statements to act as defined on a single line to
  address bugs in puppet 2.7.5
- Added entries to openldap::slapd::conf to handle all sizelimit and timelimit
  combinations as well as the ability to handle individual entries based on DN.
- Updated the default LDIF file to fully enable the password compliance
  checking.
- Updated auth_config.pp to handle the fact that SSSD can't deal with shadow
  passwords properly.

* Wed Aug 24 2011 Maintenance
4.0-0
- Akeys and /etc/ldap.conf can now use ldaps.
- Incrond now watches for permissions changes on local_keys and spawns akeys
  appropriately.
- Passwords now expire at 180 days by default.
- Ensure that we use the 'slapd' service instead of 'ldap' for RHEL6.
- Replaced the 'listen' array in openldap::slapd::conf with listen_ldap,
  listen_ldapi, and listen_ldaps.
- Added the slapd_shutdown_timeout variable to openldap::slapd::conf.
- Removed the call to functions::init_mod_open_files in openldap::slapd::conf
  with a fully templated /etc/sysconfig/ldap file.
- Removed the call to openldap-servers-overlays since they are now included
  with the main package.
- Updated the syncprov template to properly load the syncprov module.

* Mon Jun 13 2011 Maintenance - 2.0.0-3
- Rewrote the akeys script to properly handle the situation where you have
  local certs that don't work with the remote LDAP server.
- Fixed this module for the case where the $use_sssd variable doesn't exist.
- Default password length is now 14
- Changed the default password expiration to 60 days.

* Tue May 17 2011 Maintenance - 2.0.0-2
- Fixed the password policy entries to properly install. Unfortunately, users
  will need to fix this manually in the actively running LDAP.

* Tue Apr 22 2011 Maintenance - 2.0.0-1
- Added the variable $enable_logging to slapd::conf so that local4 can be
  captured.
- Changed puppet://$puppet_server/ to puppet:///
- The pull_keys define now simply takes all of the values that akeys requires
  instead of pulling them from /etc/ldap.conf. This is because SSSD does not
  populate /etc/ldap.conf.
- Updated to support the use of SSSD
- Added akeys_timeout variable so that you can modify the timeouts in the akeys
  script.
- The openldap module now expects to have an associated rsync space that is
  password protected.
- /etc/cron.hourly/akeys now deletes /etc/cron.hourly/akeys.pl if it exists.
- Ensure that slapd restarts if any part of the cert space gets changed.
- Updated akeys.erb to preserve permissions when copying files from local_keys.
- Updated the /etc/ldap.conf template and define to incorporate all possible
  pam_* options from pam_ldap(5)
- Updated to use the new concat type.
- Changed all instances of defined(Class['foo']) to defined('foo') per the
  directions from the Puppet mailing list.
- Do not log to an audit log by default.
- Do not pass the audit log to syslog by default.
- Rotate the audit log.
- Add support for the SIMP supplied openldap password policy module.
- Stop slapd from purging /etc/openldap
- Change default password mode in /etc/ldap.conf to exop to allow for server
  side password enforcement.
- PwdChangeQuality is now set to 2 in default.ldif. This means that the server
  will only accept password changes on passwords that it can read. This
  requires the 'exop' change above.
- pwdGraceAuthNL is now set to 0 in default.ldif. We do not want to allow
  "grace" logins after lockout.
- Stop slapd from purging /etc/openldap
- Updated to use rsync native type
- Updated to use concat_build and concat_fragment types

* Tue Jan 11 2011 Maintenance
2.0.0-0
- Refactored for SIMP-2.0.0-alpha release

* Fri Jan 07 2011 Maintenance - 1.0-6
- Now support multiple SSH keys in LDAP!
- Migrated akeys.pl to akeys and re-wrote it in Ruby based on ruby-ldap. This
  seems to work much more quickly than the old PERL script.

* Wed Oct 27 2010 Maintenance - 1.0-5
- Fix audit logging issues in OpenLDAP so that it actually uses the audit module.
- Ensure that auditing is able to be disabled.

* Tue Oct 26 2010 Maintenance - 1.0-4
- Converting all spec files to check for directories prior to copy.

* Thu Sep 09 2010 Maintenance
1.0-3
- Replaced tcpwrappers::tcpwrappers_allow with tcpwrappers::allow.

* Tue Aug 10 2010 Maintenance
1.0-2
- Modified the ppolicy overlay settings to use the proper DN for the default
  password policy. The policy now takes effect properly.

* Wed Jul 14 2010 Maintenance
1.0-1
- Added schema for freeradius

* Fri May 21 2010 Maintenance
1.0-0
- Added Dependency on pupmod-ssh
- Code doc and refactor.

* Thu Jan 28 2010 Maintenance
0.1-32
- Critical: Fixed a bug in akeys.pl that would result in the deletion of all
  local keys from the auth_keys directory.

* Thu Jan 14 2010 Maintenance
0.1-31
- Minor refactor to call the new function for setting max open files.

* Wed Jan 06 2010 Maintenance
0.1-30
- You can now set the maximum number of open files using the
  $ulimit_max_open_files variable in the openldap::slapd::conf define.
  - The default has been set to 81920 which should handle almost any site.

* Thu Dec 31 2009 Maintenance
0.1-29
- Fixed an issue with ssl start_tls not being present in the /etc/ldap.conf
  configuration by default.
- Added an option 'use_certs' that indicates whether or not the client should
  use the host's PKI certificates.
- Set SSL to be enabled by default.

* Tue Dec 15 2009 Maintenance
0.1-28
- Moved the copy of /etc/ssh/local_keys to the top of the akeys.pl script so
  that LDAP errors would not prevent it from happening.
- Now support base64 encoded entries in the akeys.pl script for the SSH key in LDAP.
- Modified the configuration to use the last entry in ldapuri as the default
  LDAP master and a variable, ldap_master_uri for explicitly setting the value.
- Openldap slave no longer validates certs in support of GNOME.

* Mon Nov 02 2009 Maintenance
0.1-27
- Changed the permissions on /etc/ldap.conf to 644 by default so that the GUI
  applications would work better by default.

* Tue Oct 06 2009 Maintenance
0.1-26
- Added a fact $openldap_arch to provide the build architecture of the openldap
  running on the target system.
- Modified the modulepath segment of the slapd.pp manifest to use the
  $openldap_arch fact instead of the $architecture fact.

* Tue Sep 29 2009 Maintenance
0.1-25
- Split out the module path to support both 64 and 32 bit properly
