require 'spec_helper_acceptance'
require 'erb'

test_name 'simp_openldap class'

describe 'simp_openldap class' do
  servers = hosts_with_role(hosts, 'server')
  # slaves = hosts_with_role(hosts, 'slave')

  let(:server_manifest) {
    <<-EOS
      include 'simp_openldap::server'
    EOS
  }

  servers.each do |server|
    context "simp_openldap::server #{server}" do
      let(:server_fqdn) { fact_on(server, 'fqdn') }
      let(:base_dn) { fact_on(server, 'domain').split('.').map{ |d| "dc=#{d}" }.join(',') }

      let(:server_hieradata)      { File.read(File.expand_path('templates/server_hieradata.yaml.erb', File.dirname(__FILE__))) }
      let(:server_hieradata_tls)  { File.read(File.expand_path('templates/server_hieradata_tls.yaml.erb', File.dirname(__FILE__))) }
      let(:add_testuser)          { File.read(File.expand_path('templates/add_testuser.ldif.erb', File.dirname(__FILE__))) }
      let(:add_testuser_to_admin) { File.read(File.expand_path('templates/add_testuser_to_admin.ldif.erb', File.dirname(__FILE__))) }

      context 'default parameters (no pki)' do
        it 'should configure server with tls disabled and with no errors' do
          echo_on(server, base_dn)

          on(server, 'mkdir -p /usr/local/sbin/simp')
          set_hieradata_on(server, ERB.new(server_hieradata).result(binding))
          apply_manifest_on(server, server_manifest, :catch_failures => true)
          apply_manifest_on(server, server_manifest, :acceptable_exit_codes => [0,2])
          apply_manifest_on(server, server_manifest, :acceptable_exit_codes => [0,2])

          # reboot to apply auditd changes
          # shell( 'shutdown -r now', { :expect_connection_failure => true } )
        end

        it 'should be idempotent' do
          apply_manifest(server_manifest, {:catch_changes => true})
        end

        context 'user management' do
          it 'should be able to connect and use ldapsearch' do
            on(server, "ldapsearch -LLL -D cn=LDAPAdmin,ou=People,#{base_dn} -H ldap://#{server_fqdn} -w suP3rP@ssw0r!")
          end

          it 'should be able to add a user' do
            create_remote_file(server, '/tmp/add_testuser.ldif', ERB.new(add_testuser).result(binding))

            on(server, "ldapadd -D cn=LDAPAdmin,ou=People,#{base_dn} -H ldap://#{server_fqdn} -w suP3rP@ssw0r! -x -f /tmp/add_testuser.ldif")

            result = on(server, "ldapsearch -LLL -D cn=LDAPAdmin,ou=People,#{base_dn} -H ldap://#{server_fqdn} -w suP3rP@ssw0r! -x uid=test.user")
            expect(result.stdout).to include("dn: uid=test.user,ou=People,#{base_dn}")
          end

          it 'should be able to add user to group' do
            create_remote_file(server, '/tmp/add_testuser_to_admin.ldif', ERB.new(add_testuser_to_admin).result(binding))

            on(server, "ldapmodify -D cn=LDAPAdmin,ou=People,#{base_dn} -H ldap://#{server_fqdn} -w suP3rP@ssw0r! -x -f /tmp/add_testuser_to_admin.ldif")

            result = on(server, "ldapsearch -LLL -D cn=LDAPAdmin,ou=People,#{base_dn} -H ldap://#{server_fqdn} -w suP3rP@ssw0r! -x cn=test.user")
            expect(result.stdout).to include("dn: cn=test.user,ou=Group,#{base_dn}")
          end

          context 'should be able to check password complexity' do
            password_list = [
              'p@ssW0rd',      # too short
              'SupErpAssW0rD', # not enough character classes
              'SupRrpassW0rd', # too many character classes in a row
            ]
            password_list.each_with_index do |pass,i|
              it "should reject bad password #{pass}" do
                sleep(5)
                result = on(server, "ldappasswd -D uid=test.user,ou=People,#{base_dn} -H ldap://#{server_fqdn} -w 'suP3rP@ssw0r!' -a 'suP3rP@ssw0r!' -s '#{pass}'", :acceptable_exit_codes => [1])
                expect(result.stdout).to include("Result: Constraint violation (19)")
              end
            end

            # this one should work
            pass = '6q!Bqr3ek^K!9b'
            it "should accept good password #{pass}" do
              sleep(5)
              on(server, "ldappasswd -D uid=test.user,ou=People,#{base_dn} -H ldap://#{server_fqdn} -w 'suP3rP@ssw0r!' -a 'suP3rP@ssw0r!' -s '#{pass}'")
            end
          end

          it 'should be able to expire user passwords using ppolicy' do
           # set clock forward to expire test.user
           on(server, "date --set='next year'")

           # should error out with a password expired message
           on(server, "ldapwhoami -D uid=test.user,ou=People,#{base_dn} -H ldap://#{server_fqdn} -x -w suP3rP@ssw0r! -e ppolicy", :acceptable_exit_codes => [49])

           on(server, "date --set='last year'")
          end

        end

        context 'with tls enabled' do
          it 'should be able to connect using tls and use ldapsearch' do
            on(server, 'rm /root/.ldaprc', :accept_all_exit_codes => true)
            on(server, 'mkdir -p /usr/local/sbin/simp', :accept_all_exit_codes => true)

            # convert certs to pkcs12
            certpath = '/etc/pki/simp-testing/pki'
            on(server, "openssl pkcs12 -export -in #{certpath}/private/#{server_fqdn}.pem -out #{certpath}/private/#{server_fqdn}.p12 -passout pass: -name #{server_fqdn}")
            on(server, "pk12util -i #{certpath}/private/#{server_fqdn}.p12 -d sql:/etc/openldap/certs -k /etc/openldap/certs/password -W '' -n #{server_fqdn}")
            on(server, 'chown :ldap -R /etc/pki/simp-testing/')

            set_hieradata_on(server, ERB.new(server_hieradata_tls).result(binding))
            apply_manifest_on(server, server_manifest, :catch_failures => true)
            apply_manifest_on(server, server_manifest, :acceptable_exit_codes => [0,2])

            on(server, "ldapsearch -ZZ -LLL -D cn=LDAPAdmin,ou=People,#{base_dn} -H ldap://#{server_fqdn} -x -w suP3rP@ssw0r!")
          end

          it 'should reject non-tls connections' do
            on(server, "ldapsearch -LLL -D cn=LDAPAdmin,ou=People,#{base_dn} -H ldap://#{server_fqdn} -x -w suP3rP@ssw0r!", :acceptable_exit_codes=> [13])
          end
        end
      end
    end
  end
end
