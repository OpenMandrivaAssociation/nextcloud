# based my build for stella. symbianflo

%if %{_use_internal_dependency_generator}
%define __noautoreq /usr/bin/php
%else
%define _requires_exceptions /usr/bin/php
%endif

Summary:	Private file sync and share server
Name:		nextcloud
Version:	11.0.3
Release:	2
Source0:	https://download.nextcloud.com/server/releases/%{name}-%{version}.tar.bz2
Source1:	apache.example.conf
Source100:	%{name}.rpmlintrc

License:	AGPLv3
Group:		Monitoring
Url:		http://nextcloud.com/

# apache
Requires:	config(apache-base)
Requires:	config(apache-mod_php)
# perl
Requires:	perl(Locale::PO)
Requires:	perl(Cwd)
Requires:	perl(Data::Dumper)
Requires:	perl(File::Basename)
Requires:	perl(File::Path)
Requires:	perl(Locale::PO)
#php
Requires:	php-cli >= 4.1
Requires:	config(php-zip)
Requires:	config(php-mbstring)
Requires:	config(php-gd)
Requires:	config(php-curl)
Requires:	config(php-iconv)
Requires:	config(php-sqlite3)
Requires:	config(php-pdo_sqlite)
Requires:	config(php-pgsql)
Requires:	config(php-ldap)
Requires:	config(php-intl)
#  drop cacheing because of conflicts,Sflo
# Suggests:     config(php-xcache)
Requires:	config(php-mcrypt)
Requires:	mariadb
Requires:	samba-client

# files preview
Requires:	ffmpeg
Suggests:	libreoffice

BuildArch:	noarch

%description
A personal cloud server which runs on you personal server 
and enables accessing your data from everywhere and sharing 
with other people.

%files
%doc AUTHORS 
%attr(-,apache,apache) %{_datadir}/%{name}
# Not sure if this is useful...
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/.htaccess
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf
%config(noreplace) %{_sysconfdir}/httpd/conf/webapps.d/%{name}.config.sample.php
%{_sysconfdir}/pki/%{name}/*.pem
#--------------------------------------------------------------------


%prep
%setup -qn %{name}
sed -i "s|'appstoreenabled'.*|'appstoreenabled' => false,|" config/config.sample.php

%build
# Since they said is mine , then this is a must. Symbianflo
echo "MRB aint no shit"

%install
mkdir -p %{buildroot}%{_datadir}/owncloud
(
cd %{buildroot}%{_datadir}
tar xjf %{SOURCE0}
)

# clean zero lenght
find %{buildroot} -size 0 -delete

# move config to /etc
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d
mv %{buildroot}%{_datadir}/%{name}/config/config.sample.php %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}.config.sample.php
# Not sure if this is useful...
mv %{buildroot}%{_datadir}/%{name}/config/.htaccess %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d

# install apache config file
install -m 644 %{SOURCE1}  %{buildroot}%{_sysconfdir}/httpd/conf/webapps.d/%{name}.conf


# fix some attr
find %{buildroot}%{_datadir}/owncloud -type f -exec chmod 0644 {} \;
find %{buildroot}%{_datadir}/owncloud -type d -exec chmod 0755 {} \;

# pem cert.
mkdir -p %{buildroot}%{_sysconfdir}/pki/%{name}
find . %{buildroot} -name "*.pem" -exec mv --target-directory=%{buildroot}%{_sysconfdir}/pki/%{name} {} \;

%post
ln -s %{_sysconfdir}/httpd/conf/webapps.d %{_datadir}/%{name}/config

%postun
rm -Rf %{_datadir}/%{name}/config
